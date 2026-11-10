# ---------------- easing helpers ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x + 2)**3 / 2
def eout(x):
    x = clamp(x); return 1 - (1 - x)**3
def P(t, t0, d): return ease((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def lerp(a, b, k): return a + (b - a) * k


_asset = {}
def asset(name):
    if name not in _asset:
        im = Image.open('assets/' + name).convert('RGBA')
        arr = np.ascontiguousarray(np.asarray(im))
        _asset[name] = skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)
    return _asset[name]
SAMP = skia.SamplingOptions(skia.CubicResampler.Mitchell())

def draw_cover(cv, name, dst, focus=(0.5, 0.5), zoom=1.0, zfocus=None, alpha=1.0, src_box=None, zfull=None):
    """draw image covering dst rect. src_box optional (x0,y0,x1,y1) in image px to fit-cover.
    zoom >1 zooms around zfocus (image px)."""
    img = name if isinstance(name, skia.Image) else asset(name); iw, ih = img.width(), img.height()
    dx0, dy0, dx1, dy1 = dst; dw, dh = dx1 - dx0, dy1 - dy0
    if src_box is None:
        sc = max(dw / iw, dh / ih); sw, sh = dw / sc, dh / sc
        sx0 = (iw - sw) * focus[0]; sy0 = (ih - sh) * focus[1]
    else:
        bx0, by0, bx1, by1 = src_box; sw, sh = bx1 - bx0, by1 - by0
        sx0, sy0 = bx0, by0
    if zoom != 1.0 and zfocus is not None:
        fx, fy = zfocus
        nsw, nsh = sw / zoom, sh / zoom
        # move window so focus point drifts toward the center as zoom grows
        k = clamp((zoom - 1) / max(1e-6, zfull - 1)) if zfull else 1.0
        cx = lerp(sx0 + sw / 2, fx, k); cy = lerp(sy0 + sh / 2, fy, k)
        cx = clamp(cx, nsw / 2, iw - nsw / 2); cy = clamp(cy, nsh / 2, ih - nsh / 2)
        sx0, sy0, sw, sh = cx - nsw / 2, cy - nsh / 2, nsw, nsh
    p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
    cv.save(); cv.clipRect(skia.Rect(dx0, dy0, dx1, dy1))
    cv.drawImageRect(img, skia.Rect(sx0, sy0, sx0 + sw, sy0 + sh), skia.Rect(dx0, dy0, dx1, dy1), SAMP, p)
    cv.restore()
    # return mapping image->screen
    scx, scy = dw / sw, dh / sh
    return lambda x, y: (dx0 + (x - sx0) * scx, dy0 + (y - sy0) * scy), scx


# ---------------- text helpers ----------------
def paint(col, a=1.0, stroke=None, aa=True):
    p = skia.Paint(AntiAlias=aa); c = C(col, a); p.setColor4f(c)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p
def tw(s, f, track=0): return f.measureText(s) + track * max(0, len(s) - 1)
def text(cv, s, x, y, f, col=TEXT, a=1.0, align='left', track=0, shadow=False):
    if a <= 0.001 or not s: return
    w = tw(s, f, track)
    if align == 'center': x -= w / 2
    elif align == 'right': x -= w
    p = paint(col, a)
    if shadow:
        sp = paint('#000000', 0.85 * a); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
        _draw(cv, s, x, y + 3, f, sp, track)
    _draw(cv, s, x, y, f, p, track)
    return w
def _draw(cv, s, x, y, f, p, track):
    if track == 0: cv.drawString(s, x, y, f, p); return
    for ch in s:
        cv.drawString(ch, x, y, f, p); x += f.measureText(ch) + track

def label(cv, s, x, y, prog=1.0, col=ACCENT, size=28, align='left', a=1.0, track=3):
    """mono label that types itself (prog 0..1)."""
    n = int(round(len(s) * clamp(prog)))
    f = font('mono', size)
    full = tw(s, f, track)
    if align == 'center': x -= full / 2
    text(cv, s[:n], x, y, f, col, a, track=track)
    if 0 < prog < 1:  # caret
        cx = x + tw(s[:n], f, track) + 4
        cv.drawRect(skia.Rect(cx, y - size * 0.8, cx + 3, y + 4), paint(col, a))

def pill(cv, s, cx, y, prog=1.0, col=ACCENT, size=30, fill=PANEL, a=1.0):
    if prog <= 0: return
    a = a * clamp(prog * 4)
    f = font('mono', size); full = tw(s, f, 3)
    w = full + 56; h = size + 34
    r = skia.RRect.MakeRectXY(skia.Rect(cx - w/2, y - h/2, cx + w/2, y + h/2), h/2, h/2)
    cv.drawRRect(r, paint(fill, 0.82 * a))
    cv.drawRRect(r, paint(col, 0.55 * a, stroke=2))
    label(cv, s, cx - full / 2, y + size * 0.36, prog, col, size, a=a)

def trim_stroke(cv, path, prog, col=ACCENT, width=4, a=1.0):
    if prog <= 0: return
    p = paint(col, a, stroke=width)
    if prog < 1: p.setPathEffect(skia.TrimPathEffect.Make(0, prog))
    cv.drawPath(path, p)

def bigword(cv, lines, t, t0, kw_t=None, lab=None, y_top=150, size=150, col=TEXT, accent_line=None):
    """Big word block above the head. Fully readable by kw_t."""
    d = 0.32
    if kw_t is not None: d = clamp(kw_t - t0 - 0.06, 0.0, 0.32)
    k = 1.0 if d <= 0.02 else ease((t - t0) / d)
    a = k; dy = (1 - k) * 18
    y = y_top + dy
    if lab:
        label(cv, lab, 540, y + 10, 1.0, ACCENT, 28, align='center', a=a, track=5); y += 30
    if len(lines) > 1: size = min(size, 104)
    for i, ln in enumerate(lines):
        y += size * 0.98
        fs = size
        while tw(ln, font('big', fs), -2) > 940: fs -= 4
        cc = ACCENT if (accent_line is not None and i == accent_line) else col
        text(cv, ln, 540, y, font('big', fs), cc, a, align='center', track=-2, shadow=True)

def divider(cv, y, a=1.0):
    cv.drawRect(skia.Rect(0, y - 1, W, y + 1), paint('#FFFFFF', 0.16 * a))


# ---------------- captions ----------------
CAPS = json.load(open('captions.json'))  # [text, raw_start, raw_end, [keywords]]
CAP_Y = 1492
def caption(cv, t):
    cur = None
    for i, (s, rs, re_, kws) in enumerate(CAPS):
        st = O(rs) - 0.03
        nxt = O(CAPS[i+1][1]) - 0.03 if i + 1 < len(CAPS) else DUR + 1
        en = min(nxt, O(re_) + 0.6)
        if st <= t < en: cur = (s, kws); break
    if not cur: return
    s, kws = cur
    size = 60; words = s.split(' ')
    while True:
        f = font('cap', size); space = f.measureText(' ')
        total = sum(f.measureText(w) for w in words) + space * (len(words) - 1)
        if total <= 820 or size <= 44: break
        size -= 2
    x = 500 - total / 2
    kwset = [k.lower() for k in kws]
    t_s, t_e = O(CAPS[i][1]), O(CAPS[i][2])
    tot = sum(len(w) for w in words); acc_ = 0
    for w in words:
        wst = t_s + (t_e - t_s) * acc_ / max(1, tot); acc_ += len(w)
        lit = 1.0 if i == 0 else 0.42 + 0.58 * clamp((t - wst + 0.04) / 0.10)
        bare = w.strip(',.!?—:;„”').lower()
        col = ACCENT if any(bare == k or (k in bare and len(k) > 3) for k in kwset) else TEXT
        text(cv, w, x, CAP_Y, f, col, lit, shadow=True)
        x += f.measureText(w) + space

