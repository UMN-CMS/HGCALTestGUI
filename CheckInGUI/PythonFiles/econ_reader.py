import signal
import threading
import time

import numpy as np
import cv2 as cv
import pipeline
import dm_rebuild
import econ_link
# import zxingcpp  # decoding disabled for now

# ---------------- Settings ----------------
CAMERA_INDEX = 0                 # tried first; other indices are searched if it fails
CAMERA_SEARCH = 10               # a replugged camera can come back as /dev/videoN, N > 0
REPEAT_COOLDOWN_S = 2.0          # don't re-report the same code within this window
QUIET_ZONE_PX = 20               # padding added around the crop so the decoder sees a margin

WIN_MAIN = 'Econ Reader'        # one resizable window: Controls | Color over Processed | Rebuilt
TILE_H = 240                     # height the camera views are scaled to inside the window
REBUILT_COL_W = 360              # width of the Rebuilt column (full window height)
START_SCALE = 1.0                # initial window size relative to the full canvas
REBUILT_MODULE_PX = 16           # size of each module in the Rebuilt window
SEND_BTN_H = 56                  # height of the 'Send to GUI' button under the Rebuilt view
FLASH_S = 1.5                    # how long the button shows 'Sent' / errors
SEND_REPEAT_S = 3.0              # ignore re-sending the same code within this window
MOTION_LEVEL = 4.0               # mean grey-level change per frame that counts as moving
STILL_S = 1.0                    # board must be still this long (then 'Average frames' more)

# --- zxing decoding disabled for now ---
# READ_OPTS = dict(
#     formats=zxingcpp.BarcodeFormat.DataMatrix,
#     try_rotate=True,
#     try_invert=True,
#     try_downscale=True,
# )
# # Older zxing-cpp versions (Python 3.9) may not have try_invert.
# try:
#     zxingcpp.read_barcodes(np.full((32, 32), 255, np.uint8), **READ_OPTS)
#     HAS_TRY_INVERT = True
# except TypeError:
#     READ_OPTS.pop('try_invert')
#     HAS_TRY_INVERT = False


def on_code(text):
    """Called once per new scan. Replace with whatever you need (write to file, send to PLC, etc.)."""
    print(f"[{time.strftime('%H:%M:%S')}] {text}", flush=True)


# ---------------- Slider panel ----------------
class Controls:
    """Self-drawn slider panel.

    OpenCV's built-in trackbars rely on Qt fonts, which the pip opencv-python wheel
    doesn't ship on Linux, so their labels often show up blank. This panel draws
    everything with OpenCV's own Hershey fonts, which always work.

    Click or drag on a row to set it; scroll the mouse wheel over a row for +/-1.
    """
    ROW_H = 34
    W = 560
    BAR_X0 = 210
    BAR_X1 = 450
    FONT = cv.FONT_HERSHEY_SIMPLEX

    def __init__(self):
        self.items = []
        self.by_name = {}
        self.drag = None

    def add(self, name, value, lo, hi, names=None):
        item = dict(name=name, value=value, lo=lo, hi=hi, names=names)
        self.items.append(item)
        self.by_name[name] = item

    def get(self, name):
        return self.by_name[name]['value']

    def set(self, name, v):
        it = self.by_name[name]
        it['value'] = int(min(it['hi'], max(it['lo'], v)))

    def _set_from_x(self, i, x):
        it = self.items[i]
        frac = (x - self.BAR_X0) / float(self.BAR_X1 - self.BAR_X0)
        frac = min(1.0, max(0.0, frac))
        it['value'] = int(round(it['lo'] + frac * (it['hi'] - it['lo'])))

    def height(self):
        return len(self.items) * self.ROW_H + 30

    def mouse(self, event, x, y, flags):
        """x, y relative to the panel's top-left corner (may be outside it while dragging)."""
        if self.drag is None and not (0 <= x < self.W):
            return
        i = y // self.ROW_H
        on_row = 0 <= i < len(self.items)
        if event == cv.EVENT_LBUTTONDOWN and on_row:
            self.drag = i
            self._set_from_x(i, x)
        elif event == cv.EVENT_MOUSEMOVE and self.drag is not None and (flags & cv.EVENT_FLAG_LBUTTON):
            self._set_from_x(self.drag, x)
        elif event == cv.EVENT_LBUTTONUP:
            self.drag = None
        elif event == cv.EVENT_MOUSEWHEEL and on_row:
            it = self.items[i]
            step = 1 if cv.getMouseWheelDelta(flags) > 0 else -1
            self.set(it['name'], it['value'] + step)

    def render(self):
        h = self.height()
        img = np.full((h, self.W, 3), 38, np.uint8)
        for i, it in enumerate(self.items):
            cy = i * self.ROW_H + self.ROW_H // 2
            if i % 2:
                cv.rectangle(img, (0, i * self.ROW_H), (self.W, (i + 1) * self.ROW_H), (48, 48, 48), -1)
            cv.putText(img, it['name'], (10, cy + 5), self.FONT, 0.5, (235, 235, 235), 1, cv.LINE_AA)
            span = max(1, it['hi'] - it['lo'])
            kx = int(self.BAR_X0 + (it['value'] - it['lo']) / span * (self.BAR_X1 - self.BAR_X0))
            cv.rectangle(img, (self.BAR_X0, cy - 3), (self.BAR_X1, cy + 3), (90, 90, 90), -1)
            cv.rectangle(img, (self.BAR_X0, cy - 3), (kx, cy + 3), (0, 170, 255), -1)
            cv.circle(img, (kx, cy), 8, (255, 255, 255), -1, cv.LINE_AA)
            val = it['names'][it['value'] - it['lo']] if it['names'] else str(it['value'])
            cv.putText(img, val, (self.BAR_X1 + 18, cy + 5), self.FONT, 0.5, (0, 220, 255), 1, cv.LINE_AA)
        cv.putText(img, 'click/drag/scroll a row  |  Enter = send  s = save  q = quit',
                   (10, h - 10), self.FONT, 0.42, (160, 160, 160), 1, cv.LINE_AA)
        return img


# ---------------- Background decoder ----------------
class Decoder(threading.Thread):
    """Decodes in a background thread so the video never stutters."""

    def __init__(self):
        super().__init__(daemon=True)
        self._lock = threading.Lock()
        self._job = None
        self._wake = threading.Event()
        self.busy = False
        self.running = True
        self.last_text = None
        self.last_time = 0.0
        self.last_quad = None

    def submit(self, images):
        if self.busy:
            return False
        with self._lock:
            self._job = images
            self.busy = True
        self._wake.set()
        return True

    def run(self):
        while self.running:
            if not self._wake.wait(0.1):
                continue
            self._wake.clear()
            with self._lock:
                images, self._job = self._job, None
            if images is None:
                self.busy = False
                continue

            hit = None
            for img in images:
                for r in zxingcpp.read_barcodes(img, **READ_OPTS):
                    if r.valid and r.text:
                        hit = r
                        break
                if hit:
                    break

            if hit is not None:
                now = time.time()
                if hit.text != self.last_text or now - self.last_time > REPEAT_COOLDOWN_S:
                    on_code(hit.text)
                p = hit.position
                self.last_quad = np.array(
                    [[p.top_left.x, p.top_left.y], [p.top_right.x, p.top_right.y],
                     [p.bottom_right.x, p.bottom_right.y], [p.bottom_left.x, p.bottom_left.y]],
                    dtype=np.int32) - QUIET_ZONE_PX
                self.last_text = hit.text
                self.last_time = now
            self.busy = False


def _text_bar(width, text, scale, color, thickness, height):
    bar = np.full((height, width, 3), 255, np.uint8)
    # shrink to fit; Hershey fonts are ASCII only
    text = ''.join(ch if 32 <= ord(ch) < 127 else '?' for ch in text)
    while scale > 0.3:
        (tw, th), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, scale, thickness)
        if tw <= width - 16:
            break
        scale -= 0.05
    cv.putText(bar, text, ((width - tw) // 2, (height + th) // 2), cv.FONT_HERSHEY_SIMPLEX,
               scale, color, thickness, cv.LINE_AA)
    return bar


def rebuilt_view(fit, status=None):
    """Big clean symbol for the physical scanner, the decoded string, and a status line.

    status: show only this message (no symbol), e.g. while the board is moving.
    """
    if status is not None or fit is None:
        img = np.full((320, 320, 3), 255, np.uint8)
        text, msg, color = '', status or 'no code found - adjust controls', (0, 0, 200)
    else:
        img = cv.cvtColor(dm_rebuild.render(fit.bits, REBUILT_MODULE_PX, quiet=4), cv.COLOR_GRAY2BGR)
        if fit.verified:
            text = fit.text or '?'
            if fit.method == 'search':
                msg = f'OK by format search, fixed {fit.n_fixed} codewords, margin {fit.gap:.0f}'
            else:
                msg = f'OK, fixed {fit.n_fixed} codewords'
            color = (0, 150, 0)
        else:
            text = f'guess: {fit.text}' if fit.text else ''
            msg, color = 'UNVERIFIED - adjust controls', (0, 0, 200)
    w = img.shape[1]
    return np.vstack([img,
                      _text_bar(w, text, 0.9, (0, 0, 0) if fit and fit.verified else color, 2, 44),
                      _text_bar(w, msg, 0.5, color, 1, 30)])


def _fit(img, w, h, interp):
    """Scale img to fit inside w x h, centred on a dark background."""
    if img.ndim == 2:
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    s = min(w / img.shape[1], h / img.shape[0])
    nw, nh = max(1, int(img.shape[1] * s)), max(1, int(img.shape[0] * s))
    out = np.full((h, w, 3), 38, np.uint8)
    x, y = (w - nw) // 2, (h - nh) // 2
    out[y:y + nh, x:x + nw] = cv.resize(img, (nw, nh), interpolation=interp)
    return out


def _label(img, text):
    (tw, th), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    cv.rectangle(img, (0, 0), (tw + 16, th + 14), (38, 38, 38), -1)
    cv.putText(img, text, (8, th + 7), cv.FONT_HERSHEY_SIMPLEX, 0.55, (235, 235, 235), 1, cv.LINE_AA)
    return img


class Dashboard:
    """All views composed into one resizable window.

        +----------+-----------+---------+
        |          |   Color   |         |
        | Controls +-----------+ Rebuilt |
        |          | Processed |         |
        +----------+-----------+---------+

    The bottom of the Rebuilt column is a 'Send to GUI' button.

    OpenCV hands mouse events over in canvas coordinates even when the window is
    resized, so clicks are routed to the controls panel (top-left of the canvas)
    or the send button.
    """

    def __init__(self, ctl, on_send):
        self.ctl = ctl
        self.on_send = on_send
        self.send_text = None   # verified code the button would send; None = disabled
        self.flash = None       # (message, BGR colour, until) shown briefly on the button
        self.btn_rect = None    # (x0, y0, x1, y1) of the button in canvas coordinates
        self.sized = False
        cv.namedWindow(WIN_MAIN, cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO)
        cv.setMouseCallback(WIN_MAIN, self._mouse)

    def _mouse(self, event, x, y, flags, param):
        r = self.btn_rect
        if (event == cv.EVENT_LBUTTONDOWN and self.ctl.drag is None and r is not None
                and r[0] <= x < r[2] and r[1] <= y < r[3]):
            self.on_send()
            return
        self.ctl.mouse(event, x, y, flags)  # panel sits at (0, 0); it ignores clicks off itself

    def _button(self, w):
        if self.flash is not None and time.time() < self.flash[2]:
            text, bg, fg = self.flash[0], self.flash[1], (255, 255, 255)
        elif self.send_text:
            text, bg, fg = 'Send to GUI  [Enter]', (0, 140, 0), (255, 255, 255)
        else:
            text, bg, fg = 'Send to GUI (no verified code)', (70, 70, 70), (150, 150, 150)
        btn = np.full((SEND_BTN_H, w, 3), 38, np.uint8)
        cv.rectangle(btn, (8, 6), (w - 9, SEND_BTN_H - 7), bg, -1)
        text = ''.join(ch if 32 <= ord(ch) < 127 else '?' for ch in text)
        scale = 0.7
        while True:
            (tw, th), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, scale, 2)
            if tw <= w - 32 or scale <= 0.35:
                break
            scale -= 0.05
        cv.putText(btn, text, ((w - tw) // 2, (SEND_BTN_H + th) // 2), cv.FONT_HERSHEY_SIMPLEX,
                   scale, fg, 2, cv.LINE_AA)
        return btn

    def show(self, color, processed, rebuilt):
        tw = int(round(color.shape[1] * TILE_H / color.shape[0]))
        middle = np.vstack([_label(cv.resize(color, (tw, TILE_H), interpolation=cv.INTER_AREA), 'Color'),
                            _label(_fit(processed, tw, TILE_H, cv.INTER_AREA), 'Processed')])
        panel = self.ctl.render()
        h = max(middle.shape[0], panel.shape[0])  # never crop the controls
        panel, middle = (cv.copyMakeBorder(im, 0, h - im.shape[0], 0, 0, cv.BORDER_CONSTANT,
                                           value=(38, 38, 38)) for im in (panel, middle))
        # nearest-neighbour keeps the rebuilt modules crisp for the physical scanner
        right = np.vstack([_fit(rebuilt, REBUILT_COL_W, h - SEND_BTN_H, cv.INTER_NEAREST),
                           self._button(REBUILT_COL_W)])
        x0 = panel.shape[1] + middle.shape[1]
        self.btn_rect = (x0, h - SEND_BTN_H, x0 + REBUILT_COL_W, h)
        canvas = np.hstack([panel, middle, right])
        if not self.sized:  # initial size only; after that the user's resize sticks
            cv.resizeWindow(WIN_MAIN, int(canvas.shape[1] * START_SCALE), int(canvas.shape[0] * START_SCALE))
            self.sized = True
        cv.imshow(WIN_MAIN, canvas)


def pad(img, white=True):
    if white:
        return cv.copyMakeBorder(img, *[QUIET_ZONE_PX] * 4, cv.BORDER_CONSTANT, value=255)
    return cv.copyMakeBorder(img, *[QUIET_ZONE_PX] * 4, cv.BORDER_REPLICATE)


def open_camera():
    """Open the camera at CAMERA_INDEX, or else the first index that delivers frames.

    After a USB replug the camera often reappears under a new /dev/video number, and
    a UVC camera also creates metadata nodes that open but never give frames.
    """
    for idx in [CAMERA_INDEX] + [i for i in range(CAMERA_SEARCH) if i != CAMERA_INDEX]:
        cap = cv.VideoCapture(idx, cv.CAP_V4L2)  # direct V4L2: fast, no GStreamer probing
        if cap.isOpened():
            for _ in range(10):  # first frames can fail while the camera wakes up
                if cap.read()[0]:
                    print(f"Using camera index {idx}", flush=True)
                    return cap
        cap.release()
    return None


# ---------------- Main ----------------
def main():
    stop = []  # set by SIGTERM (the GUI's Reconnect Camera button) for a clean exit
    signal.signal(signal.SIGTERM, lambda signum, frame: stop.append(signum))

    cap = open_camera()
    if cap is None:
        print("Cannot open camera - check the USB cable, then press Reconnect Camera in the GUI",
              flush=True)
        return

    ctl = Controls()
    ctl.add('Scan box px',     300, 50, 1000)                        # side of the square scan region
    ctl.add('Decode every s',   10, 1, 30)                           # how often a new still is decoded
    ctl.add('Average frames',    30, 1, 30)                           # temporal noise averaging
    ctl.add('Blur',              10, 0, 10)                           # Gaussian blur (rounds corners!)
    ctl.add('Threshold mode',    2, 0, 2, ['manual', 'otsu', 'adaptive'])
    ctl.add('Adaptive size',    201, 3, 301)                          # neighbourhood; > one cell
    ctl.add('Adaptive offset',   10, 0, 40)
    ctl.add('Manual Threshold', 127, 0, 255)                          # used in manual mode

    last_sent = [None, 0.0]  # (text, time) of the last send

    def send():
        """Send the currently shown, verified code to the GUI (button or Enter)."""
        text = dash.send_text
        now = time.time()
        until = now + FLASH_S
        if not text:
            dash.flash = ('No verified code to send', (0, 0, 170), until)
        elif text == last_sent[0] and now - last_sent[1] < SEND_REPEAT_S:
            dash.flash = (f'Already sent {text}', (170, 110, 0), until)  # double click
        elif econ_link.send_code(text):
            last_sent[:] = [text, now]
            print(f"[{time.strftime('%H:%M:%S')}] sent to GUI: {text}", flush=True)
            dash.flash = (f'Sent {text}', (170, 110, 0), until)
        else:
            dash.flash = ('Send failed', (0, 0, 170), until)

    dash = Dashboard(ctl, send)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # decoder = Decoder()   # zxing disabled
    # decoder.start()
    worker = pipeline.DecodeWorker()  # separate process: decoding never stalls the video
    submitted = 0.0           # when the snapshot being decoded was taken
    last_text = None
    rebuilt = rebuilt_view(None, 'waiting for first snapshot')
    avg = None
    last_snap = 0.0
    prev_small = None
    last_motion = time.time()
    moving = True             # treat start-up as motion: decode once things settle
    avg_count = 0

    while not stop:
        ret, frame = cap.read()
        if not ret:
            for _ in range(50):
                ret, frame = cap.read()
                if ret:
                    break
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Scan box (square, never bigger than the frame)
        height, width = gray.shape[:2]
        side = min(ctl.get('Scan box px'), width, height)
        x1, y1 = width // 2 - side // 2, height // 2 - side // 2
        x2, y2 = x1 + side, y1 + side

        # Motion check: never decode (or show an old code) while the board is moving
        now = time.time()
        small = cv.resize(gray[y1:y2, x1:x2], (64, 64), interpolation=cv.INTER_AREA).astype(np.float32)
        if prev_small is not None and np.abs(small - prev_small).mean() > MOTION_LEVEL:
            last_motion = now
            if not moving:
                moving = True
                rebuilt = rebuilt_view(None, 'moving - hold the board still')
                dash.send_text = None  # the shown code may no longer be the chip under the camera
        prev_small = small

        # 1. Temporal averaging: random sensor noise cancels out, a still part stays sharp.
        # Restarted while moving/settling so it never holds ghosts of the old position;
        # then a true mean of the first n still frames, a running average after that.
        n = max(1, ctl.get('Average frames'))
        if avg is None or avg.shape != gray.shape or now - last_motion < STILL_S:
            avg = gray.astype(np.float32)
            avg_count = 1
        else:
            avg_count += 1
            cv.accumulateWeighted(gray, avg, 1.0 / min(avg_count, n))
        still = now - last_motion >= STILL_S and avg_count >= n
        smooth = cv.convertScaleAbs(avg)

        # 2-4. Blur, contrast, threshold, morphology
        settings = {name: ctl.get(name) for name in pipeline.PIPELINE_SLIDERS}
        image, otsu_t = pipeline.process(smooth, settings, clahe)
        if otsu_t is not None:
            ctl.set('Manual Threshold', int(otsu_t))  # show what Otsu picked

        # 5. Crop the scan box
        snapshot = image[y1:y2, x1:x2]
        smooth_roi = smooth[y1:y2, x1:x2]

        # Averaged grayscale first: zxing's own binarizer keeps cell edges intact.
        # Our thresholded image is the second attempt.
        # --- zxing disabled ---
        # variants = [pad(smooth_roi, white=False), pad(snapshot)]
        # if not HAS_TRY_INVERT:
        #     variants.append(pad(255 - smooth_roi, white=False))
        # decoder.submit(variants)  # decoding runs continuously in the background

        # A still snapshot goes to the decoder on a timer - and right away once the
        # board settles after moving - whenever the decoder is free.
        if still and (moving or now - last_snap >= ctl.get('Decode every s')):
            last_snap = now
            if worker.submit(snapshot.copy()) is not None:
                submitted = now
                if moving:
                    rebuilt = rebuilt_view(None, 'decoding...')
                moving = False

        done = worker.poll()
        if done is not None:
            _, fit, err = done
            if err:
                print(f'[decoder error] {err}', flush=True)
            elif submitted >= last_motion:  # else the board moved: result may be another chip
                if fit is not None and fit.verified and fit.text and fit.text != last_text:
                    on_code(fit.text)
                    last_text = fit.text
                rebuilt = rebuilt_view(fit)
                dash.send_text = fit.text if fit is not None and fit.verified and fit.text else None

        # Display
        # recent = time.time() - decoder.last_time < 1.0   # zxing disabled
        recent = False
        color = (0, 255, 0) if recent else (0, 200, 255)
        proc_disp = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        cv.rectangle(proc_disp, (x1, y1), (x2, y2), color, 3)
        cv.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        # --- zxing disabled ---
        # if recent and decoder.last_quad is not None:
        #     cv.polylines(frame, [decoder.last_quad + (x1, y1)], True, (255, 0, 255), 2)
        # if decoder.last_text:
        #     cv.putText(frame, decoder.last_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX,
        #                0.8, color, 2, cv.LINE_AA)
        dash.show(frame, proc_disp, rebuilt)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key in (10, 13, 0x8d):  # Enter, keypad Enter
            send()
        if key == ord('s'):  # save what the decoder sees, for debugging
            stamp = time.strftime('%Y%m%d_%H%M%S')
            cv.imwrite(f'snap_{stamp}_raw.png', gray[y1:y2, x1:x2])
            cv.imwrite(f'snap_{stamp}_smooth.png', smooth_roi)
            cv.imwrite(f'snap_{stamp}_processed.png', snapshot)
            print(f"Saved snap_{stamp}_*.png")

    # decoder.running = False   # zxing disabled
    worker.stop()
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
