"""Rebuild a clean ECON Data Matrix from the processed Snapshot image.

Every ECON code is a 16x16 Data Matrix (12 data + 12 error-correction codewords),
written in ASCII mode, whose text matches FORMAT (320ICEC, D or T, two letters, digits).

The Snapshot (dark code on white, after your blur/threshold/morphology tuning) is
usually *almost* right: blobs are fat or merged, some modules are wrong. Instead of
asking a decoder to cope with that, we:

  1. Fit the 16x16 module grid: in all 4 orientations, sample the ink at each module
     centre and score how well the border matches the finder (solid L on two sides,
     alternating clock track on the other two) plus how cleanly the module values split
     into ink / no ink. The grid is hill-climbed into place.
  2. Read the codewords out of the grid (ISO 16022 placement) and run Reed-Solomon
     error correction. Modules close to the ink/no-ink cutoff make their codeword an
     *erasure* - RS can fix twice as many erasures as unknown errors - so we retry
     with more and more of the least-confident codewords erased. A correction only
     counts if its text matches FORMAT; that check is so strict that RS can be allowed
     to use its full capacity.
  3. Write the corrected codewords back into a perfect symbol. That is the nearest
     valid Data Matrix to what the camera saw, and it scans like a printed label.
  4. If that still fails (too many codewords wrong for RS alone), search: KNOWN_STARTS
     fixes the first 7 data codewords exactly. Any 12 correct codewords determine the
     other 12, so take those 7 plus every choice of 5 from the most reliable remaining
     codewords, solve for the rest, keep candidates whose text matches FORMAT, and score
     each against what the camera saw (a missing mark is cheap - faint marks are common -
     but ink where the candidate has none is expensive). The best is accepted only if it
     fits well and clearly beats the runner-up, so a capture that is genuinely ambiguous
     stays unverified.
"""
import itertools
import re

import numpy as np
import cv2 as cv

SIZE = 16                 # modules per side, finder included
NDATA, NECC = 12, 12      # data / error-correction codewords
FORMAT = re.compile(r'320ICEC[DT][A-Z]{2}[0-9]+')
KNOWN_STARTS = ('320ICECD', '320ICECT')  # fixed leading text
PREFIX = '320ICEC'                       # common to both starts

# format-constrained search (step 4); thresholds calibrated on real + simulated captures
SEARCH_POOL = 14         # choose the 5 "trusted" codewords from this many most reliable
SEARCH_MAX_COST = 50.0   # mismatch cost of the best candidate must be at most this... (right
                         # answers measured 23-36, the best wrong answer or non-code 83+)
SEARCH_MIN_GAP = 20.0    # ...and at least this much lower than the runner-up's
MISS_COST, EXTRA_COST = 1.0, 3.0  # candidate ink where image is blank / blank where image is ink


# ---------------- GF(256) / Reed-Solomon (ECC200: poly 0x12D, roots a^1..a^n) ----------------
_EXP = np.zeros(512, np.int32)
_LOG = np.zeros(256, np.int32)
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x12D
_EXP[255:510] = _EXP[:255]
_EXP, _LOG = _EXP.tolist(), _LOG.tolist()  # plain lists: much faster scalar lookups than numpy


def _mul(a, b):
    return 0 if a == 0 or b == 0 else int(_EXP[_LOG[a] + _LOG[b]])


def _div(a, b):
    return 0 if a == 0 else int(_EXP[(_LOG[a] - _LOG[b]) % 255])


def _poly_eval_low(p, x):
    """p[i] is the coefficient of x^i."""
    y = 0
    for c in reversed(p):
        y = _mul(y, x) ^ c
    return y


def rs_correct(cw, nsym, erasures=()):
    """Correct codeword list cw (data + ecc, first codeword = highest power) in place.

    erasures: indices of codewords known to be unreliable.
    Returns number of codewords changed, or None if uncorrectable.
    """
    n = len(cw)
    synd = [0] * nsym
    for j in range(nsym):
        a = int(_EXP[j + 1])
        s = 0
        for c in cw:
            s = _mul(s, a) ^ c
        synd[j] = s
    if not any(synd):
        return 0

    # erasure locator prod(1 - X x), X = a^(n-1-p)
    gamma = [1]
    for p in erasures:
        X = int(_EXP[n - 1 - p])
        gamma = [g ^ _mul(X, h) for g, h in zip(gamma + [0], [0] + gamma)]

    # Berlekamp-Massey, seeded with the erasures
    f = len(erasures)
    lam, B, L = gamma[:], gamma[:], f
    for r in range(f, nsym):
        d = 0
        for i, c in enumerate(lam):
            if r - i >= 0:
                d ^= _mul(c, synd[r - i])
        B = [0] + B
        if d:
            new = [a ^ _mul(d, b) for a, b in zip(lam + [0] * (len(B) - len(lam)),
                                                  B + [0] * (len(lam) - len(B)))]
            if 2 * L <= r + f:
                B = [_div(c, d) for c in lam]
                L = r + 1 + f - L
            lam = new
    while len(lam) > 1 and lam[-1] == 0:
        lam.pop()
    if len(lam) - 1 != L or 2 * (L - f) + f > nsym:
        return None

    # Chien search
    pos = [p for p in range(n) if _poly_eval_low(lam, int(_EXP[(255 - (n - 1 - p)) % 255])) == 0]
    if len(pos) != L:
        return None

    # Forney (first consecutive root a^1, so no extra X factor)
    omega = [0] * nsym
    for i, s in enumerate(synd):
        for k, c in enumerate(lam):
            if i + k < nsym:
                omega[i + k] ^= _mul(s, c)
    dlam = [lam[i] if i % 2 else 0 for i in range(1, len(lam))]  # formal derivative
    for p in pos:
        xi = int(_EXP[(255 - (n - 1 - p)) % 255])
        den = _poly_eval_low(dlam, xi)
        if den == 0:
            return None
        cw[p] ^= _div(_poly_eval_low(omega, xi), den)
    return len(pos)


# ---------------- Module placement (ISO 16022 Annex F) ----------------
def _placement(nrow, ncol):
    """Map of the data region: value = codeword*8 + bit (bit 0 = MSB), -1 = fixed corner."""
    a = np.full((nrow, ncol), -2, np.int32)

    def mod(r, c, ch, bit):
        if r < 0:
            r += nrow
            c += 4 - ((nrow + 4) % 8)
        if c < 0:
            c += ncol
            r += 4 - ((ncol + 4) % 8)
        a[r, c] = ch * 8 + bit

    def utah(r, c, ch):
        for bit, (dr, dc) in enumerate([(-2, -2), (-2, -1), (-1, -2), (-1, -1),
                                        (-1, 0), (0, -2), (0, -1), (0, 0)]):
            mod(r + dr, c + dc, ch, bit)

    def corner(ch, cells):
        for bit, (r, c) in enumerate(cells):
            mod(r, c, ch, bit)

    n, m = nrow, ncol
    corners = {
        1: [(n-1, 0), (n-1, 1), (n-1, 2), (0, m-2), (0, m-1), (1, m-1), (2, m-1), (3, m-1)],
        2: [(n-3, 0), (n-2, 0), (n-1, 0), (0, m-4), (0, m-3), (0, m-2), (0, m-1), (1, m-1)],
        3: [(n-3, 0), (n-2, 0), (n-1, 0), (0, m-2), (0, m-1), (1, m-1), (2, m-1), (3, m-1)],
        4: [(n-1, 0), (n-1, m-1), (0, m-3), (0, m-2), (0, m-1), (1, m-3), (1, m-2), (1, m-1)],
    }
    ch, r, c = 0, 4, 0
    while True:
        if r == n and c == 0:
            corner(ch, corners[1]); ch += 1
        if r == n - 2 and c == 0 and m % 4:
            corner(ch, corners[2]); ch += 1
        if r == n - 2 and c == 0 and m % 8 == 4:
            corner(ch, corners[3]); ch += 1
        if r == n + 4 and c == 2 and m % 8 == 0:
            corner(ch, corners[4]); ch += 1
        while True:
            if 0 <= r < n and 0 <= c < m and a[r, c] == -2:
                utah(r, c, ch); ch += 1
            r -= 2; c += 2
            if not (r >= 0 and c < m):
                break
        r += 1; c += 3
        while True:
            if 0 <= r < n and 0 <= c < m and a[r, c] == -2:
                utah(r, c, ch); ch += 1
            r += 2; c -= 2
            if not (r < n and c >= 0):
                break
        r += 3; c += 1
        if not (r < n or c < m):
            break
    a[a == -2] = -1  # unfilled bottom-right 2x2: fixed pattern
    return a


_PLACE = _placement(SIZE - 2, SIZE - 2)


def _finder_mask():
    """Expected ink (+1) / blank (-1) on the border, 0 inside. Row 0 is the top."""
    p = np.zeros((SIZE, SIZE), np.float32)
    alt = np.arange(SIZE) % 2
    p[0, :] = np.where(alt == 0, 1, -1)         # top clock track
    p[:, SIZE - 1] = np.where(alt == 1, 1, -1)  # right clock track
    p[:, 0] = 1                                 # left solid
    p[SIZE - 1, :] = 1                          # bottom solid
    return p


_MASK = _finder_mask()
_BORDER = _MASK != 0


def read_codewords(cells, cutoff):
    """Codewords plus a confidence per codeword (its least certain module)."""
    inner = cells[1:-1, 1:-1]
    cw = [0] * (NDATA + NECC)
    conf = np.full(NDATA + NECC, np.inf)
    spread = cells.std() + 1e-6
    for (r, c), v in np.ndenumerate(_PLACE):
        if v < 0:
            continue
        ch, bit = divmod(int(v), 8)
        if inner[r, c] > cutoff:
            cw[ch] |= 0x80 >> bit
        conf[ch] = min(conf[ch], abs(inner[r, c] - cutoff) / spread)
    return cw, conf


def write_symbol(cw):
    """Perfect module matrix (True = ink) for a full codeword list."""
    bits = _MASK > 0
    inner = np.zeros(_PLACE.shape, bool)
    for (r, c), v in np.ndenumerate(_PLACE):
        if v >= 0:
            ch, bit = divmod(int(v), 8)
            inner[r, c] = bool(cw[ch] & (0x80 >> bit))
    inner[-1, -1] = inner[-2, -2] = True  # fixed bottom-right corner pattern
    bits[1:-1, 1:-1] = inner
    return bits


def decode_text(data):
    """Text of ASCII-mode data codewords, or None if they aren't plain ASCII."""
    out = []
    for c in data:
        if 1 <= c <= 128:
            out.append(chr(c - 1))
        elif 130 <= c <= 229:
            out.append(f'{c - 130:02d}')  # digit pair
        elif c == 129:
            break  # pad
        else:
            return None
    return ''.join(out)


def ascii_encode(text):
    """ASCII-mode codewords (digit pairs packed), as the marker writes them."""
    out, i = [], 0
    while i < len(text):
        if text[i:i + 2].isdigit() and len(text[i:i + 2]) == 2:
            out.append(130 + int(text[i:i + 2]))
            i += 2
        else:
            out.append(ord(text[i]) + 1)
            i += 1
    return out


def correct(cells, nudge=0.0):
    """RS-correct a sampled, upright grid. nudge moves the ink cutoff, in std units.

    Returns (bits, n_fixed, text, cost) or None. cost = RS capacity used (2*errors + erasures).
    """
    t, _ = otsu_split(cells)
    t += nudge * cells.std()
    cw, conf = read_codewords(cells, t)
    order = list(np.argsort(conf))
    for f in range(NECC + 1):  # erase 0, 1, 2 ... least-confident codewords
        trial = cw[:]
        fixed = rs_correct(trial, NECC, sorted(order[:f]))
        if fixed is None:
            continue
        text = decode_text(trial[:NDATA])
        if not FORMAT.fullmatch(text or ''):
            continue  # RS "fixed" it into something that isn't an ECON code
        cost = f + 2 * (fixed - f)
        return write_symbol(trial), sum(a != b for a, b in zip(cw, trial)), text, cost
    return None


_BITS = np.array([[(v >> (7 - b)) & 1 for b in range(8)] for v in range(256)], np.float32)


def search(cells):
    """Format-constrained search (step 4). Returns [(cost, text, codewords)], best first."""
    n = NDATA + NECC
    lo, hi = np.percentile(cells, 5), np.percentile(cells, 95)
    p = np.clip((cells - lo) / (hi - lo + 1e-6), 0, 1)[1:-1, 1:-1]  # ink probability
    # cost[ch, v]: how badly value v for codeword ch disagrees with the image
    pm = np.zeros((n, 8), np.float32)
    for (r, c), v in np.ndenumerate(_PLACE):
        if v >= 0:
            pm[v // 8, v % 8] = p[r, c]
    cost = (_BITS[None] * (1 - pm[:, None]) * MISS_COST
            + (1 - _BITS[None]) * pm[:, None] * EXTRA_COST).sum(2)
    t, _ = otsu_split(cells)
    read, _ = read_codewords(cells, t)

    found = {}
    for start in KNOWN_STARTS:
        known = ascii_encode(start)
        k = len(known)
        # most reliable = read value is cheapest to explain
        free = sorted(range(k, n), key=lambda i: cost[i, read[i]])
        for trusted in itertools.combinations(free[:SEARCH_POOL], NDATA - k):
            trial = known + read[k:]
            erased = [i for i in range(k, n) if i not in trusted]
            if rs_correct(trial, NECC, erased) is None:
                continue
            text = decode_text(trial[:NDATA])
            if text and FORMAT.fullmatch(text):
                key = tuple(trial)
                if key not in found:
                    found[key] = (float(cost[np.arange(n), trial].sum()), text, trial)
    return sorted(found.values(), key=lambda r: r[0])


# ---------------- Grid fitting ----------------
def order_corners(pts):
    """tl, tr, br, bl"""
    pts = np.asarray(pts, np.float32)
    s = pts.sum(1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]],
                    np.float32)


def module_size(quad):
    """Module size in pixels of the grid spanning quad."""
    return min(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[3] - quad[0])) / SIZE


def sample(ink_blur, quad):
    """Mean ink at each module centre of the grid spanning quad."""
    src = np.array([[0, 0], [SIZE, 0], [SIZE, SIZE], [0, SIZE]], np.float32)
    H = cv.getPerspectiveTransform(src, quad)
    g = np.arange(SIZE) + 0.5
    gx, gy = np.meshgrid(g, g)
    pts = cv.perspectiveTransform(np.stack([gx, gy], -1).reshape(-1, 1, 2).astype(np.float32), H)
    pts = pts.reshape(SIZE, SIZE, 2)
    return cv.remap(ink_blur, pts[..., 0], pts[..., 1], cv.INTER_LINEAR,
                    borderMode=cv.BORDER_CONSTANT, borderValue=0)


def otsu_split(v):
    """Threshold and separation (between-class / total variance, 0..1) of a set of values."""
    v = np.sort(v.ravel())
    n = len(v)
    total = v.var() + 1e-9
    c = np.cumsum(v)
    k = np.arange(1, n)
    w0 = k / n
    m0 = c[:-1] / k
    m1 = (c[-1] - c[:-1]) / (n - k)
    between = w0 * (1 - w0) * (m0 - m1) ** 2
    i = int(np.argmax(between))
    return (v[i] + v[i + 1]) / 2, between[i] / total


def score(cells):
    """Best (score, k) over the 4 rotations: finder correlation + ink/no-ink separation."""
    z = (cells - cells.mean()) / (cells.std() + 1e-6)
    _, sep = otsu_split(cells)
    best = (-np.inf, 0)
    for k in range(4):
        corr = np.corrcoef(np.rot90(z, k)[_BORDER], _MASK[_BORDER])[0, 1]
        best = max(best, (corr + sep, k))
    return best


def shift_side(quad, side, amount):
    """Move one side of quad (0=top,1=right,2=bottom,3=left) outward by amount px."""
    q = quad.copy()
    i, j = [(0, 1), (1, 2), (2, 3), (3, 0)][side]
    edge = q[j] - q[i]
    normal = np.array([edge[1], -edge[0]], np.float32)
    normal /= np.linalg.norm(normal) + 1e-9
    if np.dot(normal, (q[i] + q[j]) / 2 - q.mean(0)) < 0:
        normal = -normal
    q[i] += normal * amount
    q[j] += normal * amount
    return q


def _moves(quad, step):
    """Candidate quads one step away: each side in/out, translate, rotate."""
    c = quad.mean(0)
    size = np.linalg.norm(quad[2] - quad[0]) / 2
    for side in range(4):
        for d in (-step, step):
            yield shift_side(quad, side, d)
    for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
        yield quad + np.float32([dx, dy])
    for a in (step / size, -step / size):
        R = np.float32([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        yield (quad - c) @ R.T + c


def _jumps(quad, mod):
    """Whole-module jumps. A grid shifted by exactly n modules still lines up with the
    marks and looks locally fine, so small steps alone can't escape it."""
    for n in (1, 2, 3):
        for side in range(4):
            for d in (-n, n):
                yield shift_side(quad, side, d * mod)
        for dx, dy in ((n, 0), (-n, 0), (0, n), (0, -n)):
            yield quad + np.float32([dx * mod, dy * mod])


def fit_grid(ink, quad, steps=(1.0, 0.5, 0.25)):
    """Hill-climb the grid placement coarse to fine, with whole-module jumps between climbs."""
    mod = max(1.0, module_size(quad))
    k = max(1, int(round(mod * 0.5)))
    ink_blur = cv.blur(ink, (k, k))

    def climb(q, s, kk):
        for step in steps:
            for _ in range(12):
                improved = False
                for cand in _moves(q, step * mod):
                    cs, ck = score(sample(ink_blur, cand))
                    if cs > s + 1e-4:
                        s, kk, q, improved = cs, ck, cand, True
                if not improved:
                    break
        return q, s, kk

    s, kk = score(sample(ink_blur, quad))
    # wide scan of each side on its own first: the start box can be a couple of modules
    # off, and the climb alone settles for a grid that is only partly on the marks
    for _ in range(2):
        for side in range(4):
            base = quad
            for d in np.arange(-2.0, 2.01, 0.25):
                cand = shift_side(base, side, d * mod)
                cs, ck = score(sample(ink_blur, cand))
                if cs > s + 1e-4:
                    s, kk, quad = cs, ck, cand
    quad, s, kk = climb(quad, s, kk)
    for _ in range(4):
        jumped = max(((score(sample(ink_blur, j)), j) for j in _jumps(quad, mod)),
                     key=lambda r: r[0][0])
        (js, jk), jq = jumped
        jq, js, jk = climb(jq, js, jk)
        if js <= s + 1e-4:
            break
        quad, s, kk = jq, js, jk
    return s, kk, quad, sample(ink_blur, quad)


def locate(ink):
    """Rough rotated box around the densest patch of marks (stray specks are too sparse)."""
    h, w = ink.shape
    density = cv.GaussianBlur((ink > 127).astype(np.float32), (0, 0), min(h, w) / 30)
    b = (density > 0.5 * np.percentile(density, 95)).astype(np.uint8)
    n, lab, stats, cent = cv.connectedComponentsWithStats(b)
    if n < 2:
        return np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    # biggest blob, mildly favouring the one nearest the centre
    d = np.hypot(cent[1:, 0] - w / 2, cent[1:, 1] - h / 2) / max(h, w)
    i = 1 + int(np.argmax(stats[1:, cv.CC_STAT_AREA] * (1.0 - d)))
    pts = cv.findNonZero((lab == i).astype(np.uint8))
    return order_corners(cv.boxPoints(cv.minAreaRect(pts)))


def mirror(cells):
    """Reflect across the diagonal through the finder's L corner. The finder looks identical
    either way, so a mirrored camera image fits the border perfectly and only the RS check
    can tell which reading is right."""
    return cells[::-1, ::-1].T


def _upright(ink, quad, k, footprint):
    """The grid at quad, sampled averaging footprint (fraction of a module) around each
    centre and rotated upright, plus its mirror image."""
    b = max(1, int(round(module_size(quad) * footprint)))
    cells = np.rot90(sample(cv.blur(ink, (b, b)), quad), k)
    return [cells, mirror(cells)]


def _variants(ink, quad, k):
    """Same grid sampled a few slightly different ways (and mirrored). Each flips a different
    handful of borderline modules; RS only accepts one that is actually consistent."""
    for footprint in (0.5, 0.25, 0.75):
        views = _upright(ink, quad, k, footprint)
        for nudge in (0.0, -0.15, 0.15, -0.3, 0.3):
            for v in views:
                yield v, nudge


# ---------------- Public API ----------------
def render(bits, module_px=10, quiet=2):
    """Dark-on-white symbol, like a printed label."""
    img = np.where(bits, 0, 255).astype(np.uint8)
    img = cv.copyMakeBorder(img, quiet, quiet, quiet, quiet, cv.BORDER_CONSTANT, value=255)
    return cv.resize(img, None, fx=module_px, fy=module_px, interpolation=cv.INTER_NEAREST)


class Fit:
    def __init__(self, bits, quad, score, verified, n_fixed=0, text=None, method=None, gap=None):
        self.bits = bits          # 16x16 bool matrix, True = ink, upright (finder L bottom-left)
        self.quad = quad          # tl,tr,br,bl of the fitted grid in snapshot coordinates
        self.score = score        # finder correlation + separation, roughly 0..2
        self.verified = verified  # True: a valid symbol whose text matches FORMAT
        self.n_fixed = n_fixed    # codewords that had to be repaired
        self.text = text          # decoded text (best guess if not verified), None if undecodable
        self.method = method      # 'rs' (error correction) or 'search' (format search)
        self.gap = gap            # search only: how far ahead of the runner-up (bigger = surer)


def rebuild(snapshot):
    """Fit an ECON Data Matrix to the processed Snapshot image (dark code on white).

    Returns a Fit (check .verified), or None if nothing resembling a symbol was found.
    """
    if snapshot.ndim == 3:
        snapshot = cv.cvtColor(snapshot, cv.COLOR_BGR2GRAY)
    ink = 255.0 - snapshot.astype(np.float32)
    h, w = ink.shape
    # Two starting boxes: the densest patch of marks, and the whole Snapshot (you frame
    # the code with the scan box; marks are often much fatter on one side, which can
    # fool the density box into covering only that side). The RS check, not the fit
    # score, decides which fit is real: a misplaced grid can still look grid-like, but
    # its codewords won't check out.
    starts = [locate(ink), np.float32([[0, 0], [w, 0], [w, h], [0, h]])]

    best, best_bad = None, None
    for quad0 in starts:
        s, k, quad, cells = fit_grid(ink, quad0)
        res = None
        for cand, nudge in _variants(ink, quad, k):
            res = correct(cand, nudge)
            if res is not None:
                break
        if res is not None:
            bits, n_fixed, text, cost = res
            if best is None or (cost, -s) < best[0]:
                best = ((cost, -s), Fit(bits, quad, s, True, n_fixed, text, 'rs'))
        elif best_bad is None or s > best_bad[0]:
            best_bad = (s, quad, np.rot90(cells, k), k)
    if best is not None:
        return best[1]
    if best_bad is None or best_bad[0] < 0.8:
        return None
    s, quad, cells, k = best_bad

    # small footprint: neighbours' fat blobs bleed in less
    views = _upright(ink, quad, k, 0.3)
    cands = sorted((c for v in views for c in search(v)), key=lambda r: r[0])
    if cands:
        c0, text, cw0 = cands[0]
        gap = (cands[1][0] - c0) if len(cands) > 1 else np.inf
        if c0 <= SEARCH_MAX_COST and gap >= SEARCH_MIN_GAP:
            fixed = min(sum(x != y for x, y in zip(read_codewords(v, otsu_split(v)[0])[0], cw0))
                        for v in views)
            return Fit(write_symbol(cw0), quad, s, True, fixed, text, 'search', gap)

    t, _ = otsu_split(cells)
    bits = cells > t
    bits[_BORDER] = _MASK[_BORDER] > 0  # at least make the finder perfect
    # uncorrected best guess (likely partly wrong); of the two readings, keep the one
    # that looks more like an ECON code
    guesses = []
    for v in (cells, mirror(cells)):
        cw, _ = read_codewords(v, t)
        g = decode_text(cw[:NDATA])
        n = 0
        while g and n < min(len(g), len(PREFIX)) and g[n] == PREFIX[n]:
            n += 1
        guesses.append((n, g))
    guess = max(guesses, key=lambda r: r[0])[1]
    return Fit(bits, quad, s, False, text=guess)
