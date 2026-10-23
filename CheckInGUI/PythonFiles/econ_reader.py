import threading
import time

import numpy as np
import cv2 as cv
# import zxingcpp  # decoding disabled for now

# ---------------- Settings ----------------
CAMERA_INDEX = 0
REPEAT_COOLDOWN_S = 2.0          # don't re-report the same code within this window
QUIET_ZONE_PX = 20               # padding added around the crop so the decoder sees a margin

WIN_PROC = 'Postprocessed'
WIN_COLOR = 'Color'
WIN_SNAP = 'Snapshot'
WIN_CTRL = 'Controls'

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

    def __init__(self, win):
        self.win = win
        self.items = []
        self.by_name = {}
        self.drag = None
        cv.namedWindow(win, cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback(win, self._mouse)

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

    def _mouse(self, event, x, y, flags, param):
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
        h = len(self.items) * self.ROW_H + 30
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
        cv.putText(img, 'click/drag or scroll a row   |   s = save crops   q = quit',
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


def pad(img, white=True):
    if white:
        return cv.copyMakeBorder(img, *[QUIET_ZONE_PX] * 4, cv.BORDER_CONSTANT, value=255)
    return cv.copyMakeBorder(img, *[QUIET_ZONE_PX] * 4, cv.BORDER_REPLICATE)


def square(k):
    # Square kernel keeps square cells square (round kernels shave the corners off)
    return cv.getStructuringElement(cv.MORPH_RECT, (k, k))


# ---------------- Main ----------------
def main():
    cap = cv.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    ctl = Controls(WIN_CTRL)
    ctl.add('Scan box px',     300, 50, 1000)                        # side of the square scan region
    ctl.add('Snapshot every s',  5, 1, 30)                           # how often the Snapshot window refreshes
    ctl.add('Average frames',    8, 1, 30)                           # temporal noise averaging
    ctl.add('Blur',              0, 0, 10)                           # Gaussian blur (rounds corners!)
    ctl.add('Contrast boost',    1, 0, 1, ['off', 'on'])             # CLAHE
    ctl.add('Threshold mode',    2, 0, 2, ['manual', 'otsu', 'adaptive'])
    ctl.add('Threshold',       127, 0, 255)                          # used in manual mode
    ctl.add('Adaptive size',    51, 3, 301)                          # neighbourhood; > one cell
    ctl.add('Adaptive offset',   7, 0, 40)
    ctl.add('Code is',           1, 0, 1, ['dark', 'light'])         # light = marks brighter than chip
    ctl.add('Speck removal',     0, 0, 10)                           # removes isolated noise dots
    ctl.add('Gap fill',          0, 0, 20)                           # fills gaps between cells

    cv.namedWindow(WIN_PROC, cv.WINDOW_NORMAL)
    cv.namedWindow(WIN_SNAP, cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO)  # resizable, stays square
    cv.resizeWindow(WIN_SNAP, 300, 300)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # decoder = Decoder()   # zxing disabled
    # decoder.start()
    avg = None
    last_snap = 0.0

    while True:
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

        # 1. Temporal averaging: random sensor noise cancels out, a still part stays sharp
        n = max(1, ctl.get('Average frames'))
        if avg is None or avg.shape != gray.shape:
            avg = gray.astype(np.float32)
        cv.accumulateWeighted(gray, avg, 1.0 / n)
        smooth = cv.convertScaleAbs(avg)

        # 2. Spatial smoothing + contrast
        b = ctl.get('Blur')
        if b:
            smooth = cv.GaussianBlur(smooth, (2 * b + 1, 2 * b + 1), 0)
        if ctl.get('Contrast boost'):
            smooth = clahe.apply(smooth)

        # 3. Threshold (white = brighter than cutoff)
        code_light = ctl.get('Code is')
        mode = ctl.get('Threshold mode')
        if mode == 1:
            t, binary = cv.threshold(smooth, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
            ctl.set('Threshold', int(t))  # show what Otsu picked
        elif mode == 2:
            block = ctl.get('Adaptive size') | 1  # must be odd
            off = ctl.get('Adaptive offset')
            binary = cv.adaptiveThreshold(smooth, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv.THRESH_BINARY, block, -off if code_light else off)
        else:
            _, binary = cv.threshold(smooth, ctl.get('Threshold'), 255, cv.THRESH_BINARY)

        # 4. Make the code white so the same morphology works for both polarities
        code = binary if code_light else cv.bitwise_not(binary)
        s = ctl.get('Speck removal')
        if s:
            code = cv.morphologyEx(code, cv.MORPH_OPEN, square(2 * s + 1))   # kill small noise blobs
        m = ctl.get('Gap fill')
        if m:
            code = cv.morphologyEx(code, cv.MORPH_CLOSE, square(2 * m + 1))  # bridge gaps between cells
        image = cv.bitwise_not(code)  # final: dark code on white, like a printed label

        # 5. Crop the scan box and hand it to the decoder
        height, width = image.shape[:2]
        side = min(ctl.get('Scan box px'), width, height)  # square, never bigger than the frame
        x1, y1 = width // 2 - side // 2, height // 2 - side // 2
        x2, y2 = x1 + side, y1 + side
        snapshot = image[y1:y2, x1:x2]
        smooth_roi = smooth[y1:y2, x1:x2]

        # Averaged grayscale first: zxing's own binarizer keeps cell edges intact.
        # Our thresholded image is the second attempt.
        # --- zxing disabled ---
        # variants = [pad(smooth_roi, white=False), pad(snapshot)]
        # if not HAS_TRY_INVERT:
        #     variants.append(pad(255 - smooth_roi, white=False))
        # decoder.submit(variants)  # decoding runs continuously in the background

        # Snapshot window is a still image, refreshed on a timer
        now = time.time()
        if now - last_snap >= ctl.get('Snapshot every s'):
            cv.imshow(WIN_SNAP, snapshot.copy())
            last_snap = now

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
        cv.imshow(WIN_PROC, proc_disp)
        cv.imshow(WIN_COLOR, frame)
        cv.imshow(WIN_CTRL, ctl.render())

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):  # save what the decoder sees, for debugging
            stamp = time.strftime('%Y%m%d_%H%M%S')
            cv.imwrite(f'snap_{stamp}_raw.png', gray[y1:y2, x1:x2])
            cv.imwrite(f'snap_{stamp}_smooth.png', smooth_roi)
            cv.imwrite(f'snap_{stamp}_processed.png', snapshot)
            print(f"Saved snap_{stamp}_*.png")

    # decoder.running = False   # zxing disabled
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
