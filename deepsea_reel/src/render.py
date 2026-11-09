# Rolex Deepsea Challenge reel — frame renderer (skia + PIL), 1080x1920 @30
import numpy as np, json, math, sys, os, subprocess
import skia
from PIL import Image, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# ---------------- brand tokens ----------------
def C(hexs, a=1.0):
    hexs = hexs.lstrip('#'); r, g, b = int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16)
    return skia.Color4f(r/255, g/255, b/255, a)
BG_TOP, BG_BOT = '#0B1A29', '#03070C'
ACCENT = '#7FE3F0'      # ice / lume
ACCENT2 = '#D9BC84'     # champagne (sparingly)
TEXT = '#F3F6F8'
MUTED = '#8FA3B3'
PANEL = '#0D1A26'

FD = '/usr/share/fonts/opentype/inter/'
FJ = '/usr/share/fonts/truetype/jetbrains-mono/'
TF = {
    'big': skia.Typeface.MakeFromFile(FD + 'InterDisplay-Bold.otf'),
    'black': skia.Typeface.MakeFromFile(FD + 'InterDisplay-ExtraBold.otf'),
    'cap': skia.Typeface.MakeFromFile(FD + 'Inter-SemiBold.otf'),
    'med': skia.Typeface.MakeFromFile(FD + 'Inter-Medium.otf'),
    'mono': skia.Typeface.MakeFromFile(FJ + 'JetBrainsMono-Medium.ttf'),
    'monob': skia.Typeface.MakeFromFile(FJ + 'JetBrainsMono-Bold.ttf'),
}
def font(k, size):
    f = skia.Font(TF[k], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); return f

# ---------------- timeline ----------------
KEEP = json.load(open('keep.json'))  # [[raw_in, raw_out], ...]
OUT_STARTS = []; acc = 0.0
for a, b in KEEP:
    OUT_STARTS.append(acc); acc += b - a
DUR = acc
NFRAMES = int(round(DUR * FPS))

def raw_of(t):
    for (a, b), s in zip(KEEP, OUT_STARTS):
        if t < s + (b - a) - 1e-9: return a + (t - s)
    a, b = KEEP[-1]; return b - 1e-3
def O(r):
    """raw time -> output time (snaps into kept range)"""
    for (a, b), s in zip(KEEP, OUT_STARTS):
        if r < a: return s
        if r <= b: return s + (r - a)
    return DUR

# ---------------- easing helpers ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x + 2)**3 / 2
def eout(x):
    x = clamp(x); return 1 - (1 - x)**3
def P(t, t0, d): return ease((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def lerp(a, b, k): return a + (b - a) * k

# ---------------- footage ----------------
RGBA = np.load('rgba.npy', mmap_mode='r')
STATS = json.load(open('stats.json'))
SEGB = [0, 238, 621, 908, 1356, 1762, 2228, 2494, 2644]
RECT = [(101, 291, 600), (81, 271, 593), (89, 304, 625), (78, 286, 612), (83, 296, 556), (72, 289, 608), (78, 276, 585), (120, 288, 579)]
SEG = []
_st = np.array(STATS)
for i in range(8):
    x = _st[SEGB[i]:SEGB[i+1]]
    SEG.append(dict(top=float(np.percentile(x[:, 0], 1)), hw=float(np.median(x[:, 2])), hc=float(np.median(x[:, 3])),
                    x0=RECT[i][0], x1=RECT[i][1], bot=RECT[i][2]))
_fade_cache = {}
def seg_of(fi):
    for i in range(8):
        if fi < SEGB[i+1]: return i
    return 7
def fade_mask(si):
    if si in _fade_cache: return _fade_cache[si]
    s = SEG[si]; yy, xx = np.mgrid[0:626, 0:352].astype(np.float32)
    side = np.clip((xx - s['x0']) / 16, 0, 1) * np.clip((s['x1'] - xx) / 16, 0, 1)
    bot = np.clip((s['bot'] - 6 - yy) / 70, 0, 1)
    m = (side ** 1.5) * (bot ** 1.3)
    _fade_cache[si] = m; return m

def person_image(fi, scale):
    """returns (skia image, origin_x_src, origin_y_src) for person at scale."""
    si = seg_of(fi); s = SEG[si]
    fr = np.array(RGBA[fi]).astype(np.float32)
    a = fr[..., 3] / 255.0 * fade_mask(si)
    x0, x1 = max(0, s['x0'] - 2), min(352, s['x1'] + 3)
    y0, y1 = int(max(0, s['top'] - 12)), min(626, s['bot'] + 1)
    rgb = fr[y0:y1, x0:x1, :3] / 255.0
    # gentle grade: tiny contrast + saturation, keep warmth
    l = rgb.mean(2, keepdims=True)
    rgb = l + (rgb - l) * 1.05
    rgb = (rgb - 0.5) * 1.04 + 0.5 + 0.005
    rgb = np.clip(rgb, 0, 1)
    im = Image.fromarray(np.dstack([rgb * 255, a[y0:y1, x0:x1] * 255]).astype(np.uint8), 'RGBA')
    tw, th = max(1, int(round((x1 - x0) * scale))), max(1, int(round((y1 - y0) * scale)))
    im = im.resize((tw, th), Image.LANCZOS)
    r, g, b, al = im.split()
    rgbim = Image.merge('RGB', (r, g, b)).filter(ImageFilter.UnsharpMask(radius=max(1.2, scale * 0.45), percent=55, threshold=2))
    im = Image.merge('RGBA', (*rgbim.split(), al))
    arr = np.ascontiguousarray(np.asarray(im))
    sk = skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)
    return sk, x0, y0, s

def draw_person(cv, fi, headw, cx, ytop, punch=1.0, anchor=None, alpha=1.0):
    s0 = SEG[seg_of(fi)]
    sc = headw / s0['hw'] * punch
    img, x0, y0, s = person_image(fi, sc)
    # map: src head-center -> cx ; src top -> ytop  (then punch around anchor)
    base_sc = headw / s['hw']
    X = lambda xs: cx + (xs - s['hc']) * base_sc
    Y = lambda ys: ytop + (ys - s['top']) * base_sc
    dx, dy = X(x0), Y(y0)
    if anchor is not None and punch != 1.0:
        ax, ay = anchor
        dx = ax + (dx - ax) * punch; dy = ay + (dy - ay) * punch
    p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
    cv.drawImage(img, dx, dy, skia.SamplingOptions(skia.FilterMode.kLinear), p)

# ---------------- assets ----------------
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
    img = asset(name); iw, ih = img.width(), img.height()
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

# ---------------- background ----------------
def make_bg():
    s = skia.Surface(W, H); cv = s.getCanvas()
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C(BG_TOP).toColor(), C(BG_BOT).toColor()]))
    cv.drawRect(skia.Rect(0, 0, W, H), p)
    # faint "light from the surface" at the top-left edge, low opacity
    p2 = skia.Paint(Shader=skia.GradientShader.MakeRadial((140, -120), 900, [C(ACCENT, 0.10).toColor(), C(ACCENT, 0.0).toColor()]))
    cv.drawRect(skia.Rect(0, 0, W, H), p2)
    p3 = skia.Paint(Shader=skia.GradientShader.MakeRadial((1000, 700), 700, [C('#1C4A66', 0.18).toColor(), C('#1C4A66', 0).toColor()]))
    cv.drawRect(skia.Rect(0, 0, W, H), p3)
    return s.makeImageSnapshot()
BG = None

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
        sp = paint('#000000', 0.55 * a); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7))
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
    for w in words:
        bare = w.strip(',.!?—:;').lower()
        col = ACCENT if any(bare == k or (k in bare and len(k) > 3) for k in kwset) else TEXT
        text(cv, w, x, CAP_Y, f, col, 1.0, shadow=True)
        x += f.measureText(w) + space

# ---------------- layouts ----------------
FULL = dict(headw=450, ytop=380)
LOW = dict(headw=262, ytop=846)
TOP_H = 800

def entrance(t, t0, d=0.30):
    k = ease((t - t0) / d); return k, (1 - k) * 26

def panel_top(cv, name, t, t0, **kw):
    k, dy = entrance(t, t0)
    cv.save(); cv.translate(0, -dy * 0.0)
    m = draw_cover(cv, name, (0, 0, W, TOP_H), alpha=k, **kw)
    cv.restore()
    divider(cv, TOP_H, k)
    return m

def card_top(cv, name, t, t0, src_box=None, focus=(0.5, 0.5), bg_white=False):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 110, 96 + dy, 970, 770 + dy
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 40, 40)
    sp = paint('#000000', 0.55 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 28))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 6, y0 + 26, x1 - 6, y1 + 26), 40, 40), sp)
    cv.save(); cv.clipRRect(r, True)
    if bg_white:
        cv.drawRect(skia.Rect(x0, y0, x1, y1), paint('#F4F5F6', k))
    m = draw_cover(cv, name, (x0, y0, x1, y1), alpha=k, src_box=src_box, focus=focus)
    # bottom scrim for the label
    g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y1 - 200), (0, y1)], [C('#000000', 0).toColor(), C('#03070C', 0.78 * k).toColor()]))
    cv.drawRect(skia.Rect(x0, y1 - 200, x1, y1), g)
    cv.restore()
    cv.drawRRect(r, paint('#FFFFFF', 0.14 * k, stroke=2))
    return (x0, y0, x1, y1), k

def circle_me(cv, fi, cx, cy, d, t, t0, a=1.0):
    k = ease((t - t0 - 0.30) / 0.30) * a  # after the asset lands
    if k <= 0: return
    r = d / 2
    cv.save()
    path = skia.Path(); path.addCircle(cx, cy, r)
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    cv.drawCircle(cx, cy + 10, r, sp)
    cv.clipPath(path, True)
    cv.drawRect(skia.Rect(cx - r, cy - r, cx + r, cy + r), paint('#0E2233', k))
    hw = d * 0.44
    draw_person(cv, fi, hw, cx, cy - r + d * 0.13, alpha=k)
    cv.restore()
    cv.drawCircle(cx, cy, r, paint('#FFFFFF', 0.30 * k, stroke=3))

def asset_full(cv, name, t, t0, fade_from=1050, fade_to=1400, top=0, **kw):
    k, dy = entrance(t, t0)
    m = draw_cover(cv, name, (0, top, W, fade_to), alpha=k, **kw)
    if top > 0:
        g0 = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, top - 1), (0, top + 170)], [C('#0A1826', 1).toColor(), C('#0A1826', 0).toColor()]))
        cv.drawRect(skia.Rect(0, top - 1, W, top + 170), g0)
    g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, fade_from), (0, fade_to)], [C(BG_BOT, 0).toColor(), C('#050B12', 1).toColor()]))
    cv.drawRect(skia.Rect(0, fade_from, W, fade_to + 2), g)
    return m

# ---------------- graphics ----------------
def g_depth(cv, t, t0, mode='descend', **o):
    """vertical depth scale 0..11 km. modes: descend (counter), dive (down & back)."""
    k, dy = entrance(t, t0)
    X, Y0, Y1 = 140, 230, 740
    yof = lambda m: Y0 + (Y1 - Y0) * m / 11000
    cv.drawRect(skia.Rect(X - 1, Y0, X + 1, Y1), paint('#FFFFFF', 0.35 * k))
    fm = font('mono', 20)
    for km in range(0, 12):
        y = yof(km * 1000); L = 22 if km % 2 == 0 else 12
        cv.drawRect(skia.Rect(X - L, y - 1, X, y + 1), paint('#FFFFFF', 0.45 * k))
        if km % 2 == 0: text(cv, f"{km} km", X - 32, y + 7, fm, MUTED, k, align='right')
    if mode == 'descend':
        label(cv, o['lab'], 90, 160, P(t, t0 + 0.15, 0.5), ACCENT, 28, a=k)
        d = 10935 * ease((t - o['ta']) / (o['tb'] - o['ta']))
        y = yof(d)
        trim = skia.Path(); trim.moveTo(X, Y0); trim.lineTo(X, y)
        cv.drawPath(trim, paint(ACCENT, 0.9 * k, stroke=4))
        cv.drawCircle(X, y, 11, paint(ACCENT, k))
        cv.drawRect(skia.Rect(X + 18, y - 1, X + 150, y + 1), paint(ACCENT, 0.6 * k))
        txt = f"{int(round(d)):,}".replace(',', ' ') + " m"
        text(cv, txt, 300, 520, font('big', 150), TEXT, k, track=-3, shadow=True)
        label(cv, 'GŁĘBOKOŚĆ DNA', 306, 590, 1.0, MUTED, 26, a=k)
    elif mode == 'dive':
        label(cv, o['lab'], 90, 160, P(t, t0 + 0.15, 0.5), ACCENT, 28, a=k)
        down = ease((t - o['ta']) / (o['tb'] - o['ta'])); up = ease((t - o['tc']) / (o['td'] - o['tc']))
        dmax = 10908
        d = dmax * down * (1 - up)
        y = yof(d)
        path = skia.Path(); path.moveTo(X, Y0); path.lineTo(X, yof(dmax * down))
        cv.drawPath(path, paint(ACCENT, 0.55 * k, stroke=4))
        if up > 0:
            p2 = skia.Path(); p2.moveTo(X + 16, yof(dmax)); p2.lineTo(X + 16, y)
            cv.drawPath(p2, paint(ACCENT2, 0.9 * k, stroke=4))
            cv.drawCircle(X + 16, y, 11, paint(ACCENT2, k))
        else:
            cv.drawCircle(X, y, 11, paint(ACCENT, k))
        if up <= 0:
            txt = f"{int(round(d)):,}".replace(',', ' ') + " m"
            a1 = 1.0
        else:
            txt = '10 908 m'; a1 = 1.0
        text(cv, txt, 300, 640, font('big', 96), TEXT, a1 * k, track=-2, shadow=True)
        label(cv, 'DNO · CHALLENGER DEEP' if down >= 1 else 'ZANURZENIE', 306, 700, 1.0, MUTED, 24, a=a1 * k)
        a2 = P(t, o['td'] - 0.05, 0.25)
        text(cv, 'WRÓCIŁ', 300, 360, font('big', 118), ACCENT2, a2 * k, track=-2, shadow=True)
        label(cv, 'NA POWIERZCHNIĘ', 306, 412, 1.0, MUTED, 24, a=a2 * k)

def g_limit(cv, t, t0, o):
    k, _ = entrance(t, t0)
    label(cv, 'GRANICA WYTRZYMAŁOŚCI', 90, 160, P(t, t0 + 0.1, 0.45), ACCENT, 28, a=k)
    X, Y0, Y1 = 140, 230, 740; lo, hi = 10800, 11080
    yof = lambda m: Y0 + (Y1 - Y0) * (m - lo) / (hi - lo)
    cv.drawRect(skia.Rect(X - 1, Y0, X + 1, Y1), paint('#FFFFFF', 0.35 * k))
    for m in range(lo, hi + 1, 20):
        y = yof(m); L = 22 if m % 100 == 0 else 10
        cv.drawRect(skia.Rect(X - L, y - 1, X, y + 1), paint('#FFFFFF', 0.4 * k))
        if m % 100 == 0: text(cv, f"{m:,} m".replace(',', ' '), X - 32, y + 7, font('mono', 20), MUTED, k, align='right')
    # line 1: deepest point
    p1 = P(t, o['t1'], 0.45); y = yof(10935)
    ln = skia.Path(); ln.moveTo(X, y); ln.lineTo(X + 820, y)
    trim_stroke(cv, ln, p1, TEXT, 3, k)
    text(cv, 'NAJGŁĘBSZY PUNKT ZIEMI', X + 30, y - 22, font('mono', 26), TEXT, p1 * k, track=2)
    text(cv, '10 935 m', X + 820, y - 18, font('big', 54), TEXT, p1 * k, align='right')
    p2 = P(t, o['t2'], 0.45); y2 = yof(11000)
    ln2 = skia.Path(); ln2.moveTo(X, y2); ln2.lineTo(X + 820, y2)
    trim_stroke(cv, ln2, p2, ACCENT, 5, k)
    text(cv, 'LIMIT ZEGARKA', X + 30, y2 + 50, font('mono', 26), ACCENT, p2 * k, track=2)
    text(cv, '11 000 m', X + 820, y2 + 62, font('big', 54), ACCENT, p2 * k, align='right')

def g_can(cv, t, t0, o):
    k, _ = entrance(t, t0)
    label(cv, 'CIŚNIENIE NA DNIE ≈ 1 086 BAR', 540, 150, P(t, t0 + 0.1, 0.5), ACCENT, 28, align='center', a=k)
    cx, base, w, h0 = 540, 690, 250, 420
    crush = ease((t - o['tc']) / 0.42)
    h = h0 * (1 - 0.48 * crush)
    top = base - h
    rx, ry = w / 2, 26
    pth = skia.Path()
    # side walls with crumple zigzag
    n = 9
    def side(xs, sgn):
        pts = []
        for i in range(n + 1):
            yy = base - h * i / n
            z = (0 if i in (0, n) else (1 if i % 2 else -1)) * 22 * crush * sgn
            pts.append((xs + z, yy))
        return pts
    L = side(cx - rx, 1); R = side(cx + rx, -1)
    pth.moveTo(*L[0])
    for p_ in L[1:]: pth.lineTo(*p_)
    pth.addOval(skia.Rect(cx - rx, top - ry, cx + rx, top + ry))
    pth.moveTo(*R[0])
    for p_ in R[1:]: pth.lineTo(*p_)
    pth.addArc(skia.Rect(cx - rx, base - ry, cx + rx, base + ry), 0, 180)
    trim_stroke(cv, pth, P(t, t0 + 0.2, 0.7), TEXT, 4, k)
    # inner rim
    rim = skia.Path(); rim.addOval(skia.Rect(cx - rx * 0.62, top - ry * 0.5, cx + rx * 0.62, top + ry * 0.5))
    trim_stroke(cv, rim, P(t, t0 + 0.7, 0.4), MUTED, 3, k)
    # pressure arrows after crush
    pa = P(t, o['tc'] + 0.45, 0.3)
    for dx in (-1, 1):
        ax = cx + dx * (rx + 90)
        ar = skia.Path(); ar.moveTo(ax + dx * 60, base - h / 2); ar.lineTo(ax, base - h / 2)
        ar.moveTo(ax + dx * 18, base - h / 2 - 16); ar.lineTo(ax, base - h / 2); ar.lineTo(ax + dx * 18, base - h / 2 + 16)
        cv.drawPath(ar, paint(ACCENT, pa * k, stroke=4))

def g_material(cv, t, t0, o):
    k, _ = entrance(t, t0)
    def card(x0, kk, tag, word, col, dyk):
        if kk <= 0: return
        y0 = 190 + (1 - kk) * 40
        r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x0 + 420, y0 + 440), 32, 32)
        sp = paint('#000000', 0.45 * kk); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 6, y0 + 20, x0 + 414, y0 + 460), 32, 32), sp)
        cv.drawRRect(r, paint(PANEL, 0.92 * kk))
        cv.drawRRect(r, paint(col, 0.45 * kk, stroke=2))
        label(cv, tag, x0 + 40, y0 + 70, 1.0, MUTED, 24, a=kk)
        yy = y0 + 250
        for i, wd in enumerate(word):
            text(cv, wd, x0 + 40, yy + i * 100, font('big', 96), col, kk, track=-2)
        return y0
    yA = card(80, k, 'PROTOTYP · 2012', ['STAL'], TEXT, 0)
    kb = P(t, o['tb'], 0.38)
    card(580, kb, 'PRODUKCJA · 2022', ['TYTAN', 'RLX'], ACCENT, 0)
    ps = P(t, o['ts'], 0.4)
    if ps > 0:
        f = font('big', 96); wdt = tw('STAL', f, -2)
        ln = skia.Path(); ln.moveTo(120 - 10, 190 + 250 - 33); ln.lineTo(120 + wdt + 10, 190 + 250 - 33)
        trim_stroke(cv, ln, ps, ACCENT2, 7, k)

def g_bars(cv, t, t0, o):
    k, _ = entrance(t, t0)
    label(cv, 'MASA · PORÓWNANIE', 90, 170, 1.0, ACCENT, 28, a=k)
    X0, Wmax = 90, 900
    def bar(y, frac, col, a, lab):
        label(cv, lab, X0, y - 24, 1.0, MUTED, 24, a=a)
        r0 = skia.RRect.MakeRectXY(skia.Rect(X0, y, X0 + Wmax, y + 34), 17, 17)
        cv.drawRRect(r0, paint('#FFFFFF', 0.06 * a))
        r = skia.RRect.MakeRectXY(skia.Rect(X0, y, X0 + Wmax * frac, y + 34), 17, 17)
        cv.drawRRect(r, paint(col, a))
    bar(290, 1.0, '#9AA7B2', k, 'PROTOTYP 2012')
    sh = ease((t - o['ts']) / 0.42)
    bar(430, 1.0 - 0.30 * sh, ACCENT, k, 'DEEPSEA CHALLENGE · TYTAN RLX')
    # ghost of the removed 30 %
    if sh > 0:
        gx0 = X0 + Wmax * 0.70; gx1 = X0 + Wmax * (1.0 - 0.30 * sh)
        eff = skia.DashPathEffect.Make([10, 8], 0)
        pp = paint(ACCENT, 0.6 * sh * k, stroke=2); pp.setPathEffect(eff)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(X0 + Wmax * 0.70, 430, X0 + Wmax, 464), 17, 17), pp)
    a = P(t, o['ts'] + 0.42, 0.25)
    text(cv, '−30%', 84, 680, font('big', 150), ACCENT, a * k, track=-4, shadow=True)
    label(cv, 'LŻEJSZY OD PROTOTYPU', 96, 740, 1.0, MUTED, 26, a=a * k)

def g_phone(cv, t, t0, o):
    k, _ = entrance(t, t0)
    x0, y0, x1, y1 = 150, 150, 410, 680
    ph = skia.Path(); ph.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 44, 44))
    trim_stroke(cv, ph, P(t, t0 + 0.05, 0.6), TEXT, 4, k)
    isl = skia.Path(); isl.addRRect(skia.RRect.MakeRectXY(skia.Rect(240, 178, 320, 200), 11, 11))
    trim_stroke(cv, isl, P(t, t0 + 0.55, 0.25), MUTED, 3, k)
    label(cv, 'TELEFON', 280, 740, P(t, t0 + 0.6, 0.3), MUTED, 26, align='center', a=k)
    a = P(t, o['tw'], 0.3)
    label(cv, 'CAŁY ZEGAREK', 520, 340, 1.0, ACCENT, 28, a=a * k)
    text(cv, '≈250 g', 510, 480, font('big', 150), TEXT, a * k, track=-3, shadow=True)

def g_divers(cv, t, t0, o):
    k, _ = entrance(t, t0, 0.2)
    rows = [('40 m', 'NURKOWANIE REKREACYJNE'), ('300 m', 'TYPOWY ZEGAREK NURKOWY'), ('332 m', 'REKORD ŚWIATA W NURKOWANIU')]
    for i, (num, tag) in enumerate(rows):
        kk = P(t, o['tr'][i], 0.35) * k
        if kk <= 0: continue
        y0 = 150 + i * 190 + (1 - kk) * 30
        r = skia.RRect.MakeRectXY(skia.Rect(90, y0, 990, y0 + 160), 28, 28)
        cv.drawRRect(r, paint(PANEL, 0.9 * kk)); cv.drawRRect(r, paint('#FFFFFF', 0.12 * kk, stroke=2))
        text(cv, num, 130, y0 + 108, font('big', 84), TEXT, kk, track=-2)
        label(cv, tag, 440, y0 + 92, 1.0, MUTED, 24, a=kk)
    a = P(t, o['tz'], 0.35)
    if a > 0:
        y0 = 150 + 3 * 190 - 10
        text(cv, 'Deepsea Challenge:  11 000 m', 130, y0 + 60, font('cap', 44), ACCENT, a * k)

def g_comment(cv, t, t0, o):
    k, _ = entrance(t, t0)
    text(cv, 'Co sądzisz?', 540, 260, font('big', 118), TEXT, k, align='center', track=-2, shadow=True)
    y0 = 360; r = skia.RRect.MakeRectXY(skia.Rect(90, y0, 990, y0 + 150), 75, 75)
    cv.drawRRect(r, paint(PANEL, 0.95 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.18 * k, stroke=2))
    cv.drawCircle(165, y0 + 75, 42, paint('#173246', k))
    cv.drawCircle(165, y0 + 75, 42, paint(ACCENT, 0.7 * k, stroke=2))
    text(cv, 'Ty', 165, y0 + 88, font('cap', 34), TEXT, k, align='center')
    s = 'Deepsea Challenge to…'
    pr = P(t, o['tt'], 0.95)
    if pr <= 0:
        text(cv, 'Dodaj komentarz…', 232, y0 + 90, font('med', 40), MUTED, 0.8 * k)
    else:
        n = int(len(s) * pr); ss = s[:n]
        w = text(cv, ss, 232, y0 + 90, font('med', 40), TEXT, k) or 0
        if (int(t * 2.5) % 2 == 0) or pr < 1:
            cv.drawRect(skia.Rect(236 + w, y0 + 50, 239 + w, y0 + 100), paint(ACCENT, k))
    # send button
    cv.drawCircle(925, y0 + 75, 40, paint(ACCENT, (0.35 + 0.65 * (pr >= 1)) * k))
    ar = skia.Path(); ar.moveTo(908, y0 + 75); ar.lineTo(942, y0 + 75); ar.moveTo(928, y0 + 60); ar.lineTo(943, y0 + 75); ar.lineTo(928, y0 + 90)
    cv.drawPath(ar, paint('#03070C', k, stroke=5))

def follow_card(cv, t, t0, o):
    k = clamp((t - t0) / 0.12 + 0.35); dy = 0
    y0 = 150 + dy; r = skia.RRect.MakeRectXY(skia.Rect(80, y0, 1000, y0 + 170), 85, 85)
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 24))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(90, y0 + 18, 990, y0 + 188), 85, 85), sp)
    cv.drawRRect(r, paint(PANEL, 0.95 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.16 * k, stroke=2))
    cv.drawCircle(165, y0 + 85, 55, paint('#173246', k)); cv.drawCircle(165, y0 + 85, 55, paint(ACCENT, k, stroke=3))
    text(cv, 'ZD', 165, y0 + 100, font('big', 42), ACCENT, k, align='center')
    text(cv, '@zegarkidawida', 240, y0 + 101, font('cap', 44), TEXT, k)
    # button with tap
    tap = o['tap']; pr = clamp((t - tap) / 0.24)
    s = 1 - 0.07 * math.sin(math.pi * pr) if 0 < pr < 1 else 1
    done = t >= tap + 0.12
    bx0, bx1, by0, by1 = 712, 966, y0 + 45, y0 + 125
    # button sits under the card to the right
    bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
    cv.save(); cv.translate(bcx, bcy); cv.scale(s, s); cv.translate(-bcx, -bcy)
    br = skia.RRect.MakeRectXY(skia.Rect(bx0, by0, bx1, by1), 40, 40)
    if not done:
        cv.drawRRect(br, paint(ACCENT, k)); text(cv, 'Obserwuj', bcx, bcy + 12, font('cap', 34), '#03070C', k, align='center')
    else:
        cv.drawRRect(br, paint(PANEL, k)); cv.drawRRect(br, paint(ACCENT, k, stroke=2))
        text(cv, 'Obserwujesz', bcx, bcy + 12, font('cap', 30), ACCENT, k, align='center')
    cv.restore()
    if 0 < pr < 1.6:  # tap ring
        rr = 20 + 50 * clamp(pr / 1.6)
        cv.drawCircle(bcx + 40, bcy + 6, rr, paint('#FFFFFF', 0.5 * (1 - clamp(pr / 1.6)) * k, stroke=3))

# ---------------- beats ----------------
BEATS = json.load(open('beats.json'))
for b in BEATS: b['t0'] = O(b['raw'])
def beat_at(t):
    cur = BEATS[0]
    for b in BEATS:
        if t >= b['t0'] - 1e-6: cur = b
    return cur

def punch_val(t, kw):
    if kw is None: return 1.0
    return 1.0 + 0.065 * ease((t - (O(kw) - 0.12)) / 0.42)

def render(t, cv, hook_variant=None):
    raw = raw_of(t); fi = min(2643, int(round(raw * FPS)))
    cv.drawImage(BG, 0, 0)
    b = beat_at(t)
    L = b['layout']; t0 = b['t0']
    if hook_variant and L == 'hook': L = hook_variant
    if L == 'hook':   # hero full + circle + headline
        asset_full(cv, 'hero.jpg', t, -1, src_box=(500, 170, 1560, 1134), fade_from=1080, fade_to=1400, top=440)
        label(cv, 'RÓW MARIAŃSKI  ·  10 935 m', 540, 170, 1.0, ACCENT, 28, align='center', track=4)
        text(cv, 'Wrzuć go na dno', 540, 290, font('big', 100), TEXT, 1, align='center', track=-2, shadow=True)
        text(cv, 'oceanu.', 540, 395, font('big', 100), ACCENT, 1, align='center', track=-2, shadow=True)
        circle_me(cv, fi, 210, 1190, 270, t, -1)
    elif L == 'hookB':  # me full + live depth counter
        draw_person(cv, fi, FULL['headw'], 540, FULL['ytop'])
        label(cv, 'RÓW MARIAŃSKI', 540, 140, 1.0, ACCENT, 28, align='center', track=5)
        d = 10935 * (0.80 + 0.20 * eout(t / 1.6))
        text(cv, f"−{int(round(d)):,}".replace(',', ' ') + ' m', 540, 300, font('big', 150), TEXT, 1, align='center', track=-3, shadow=True)
    elif L == 'hookC':  # split: beam image + headline in panel
        draw_cover(cv, 'beam.jpg', (0, 0, W, TOP_H), src_box=(0, 120, 840, 742))
        g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 430), (0, TOP_H)], [C('#03070C', 0).toColor(), C('#03070C', 0.85).toColor()]))
        cv.drawRect(skia.Rect(0, 430, W, TOP_H), g)
        text(cv, 'Przeżyje dno oceanu.', 540, 720, font('big', 84), TEXT, 1, align='center', track=-2, shadow=True)
        divider(cv, TOP_H)
        draw_person(cv, fi, LOW['headw'], 540, LOW['ytop'])
    elif L == 'full':
        pv = punch_val(t, b.get('punch'))
        anchor = (540, FULL['ytop'] + FULL['headw'] * 1.1)
        draw_person(cv, fi, FULL['headw'], 540, FULL['ytop'], punch=pv, anchor=anchor)
        if b.get('follow'):
            follow_card(cv, t, t0, dict(tap=O(b['tap'])))
        else:
            bigword(cv, b['big'], t, t0, O(b['kw']) if b.get('kw') else None, b.get('lab'), y_top=b.get('ytop', 132),
                    size=b.get('size', 150), accent_line=b.get('accent'))
    else:
        # all top-half layouts: me in LOW framing
        draw_person(cv, fi, LOW['headw'], 540, LOW['ytop'])
        if L == 'card':
            box, k = card_top(cv, b['img'], t, t0, src_box=b.get('box'), bg_white=b.get('white', False))
            x0, y0, x1, y1 = box
            label(cv, b['lab'], 160, y1 - 52, P(t, t0 + 0.32, 0.6), ACCENT if not b.get('white') else ACCENT, 30, a=k)
        elif L == 'depth':
            g_depth(cv, t, t0, 'descend', lab='RÓW MARIAŃSKI · PACYFIK', ta=O(b['ta']), tb=O(b['tb']))
        elif L == 'dive':
            g_depth(cv, t, t0, 'dive', lab='2012 · ZEGAREK NA RAMIENIU ROBOTA', ta=O(b['ta']), tb=O(b['tb']), tc=O(b['tc']), td=O(b['td']))
        elif L == 'can':
            g_can(cv, t, t0, dict(tc=O(b['tc'])))
        elif L == 'limit':
            g_limit(cv, t, t0, dict(t1=O(b['t1']), t2=O(b['t2'])))
        elif L == 'material':
            g_material(cv, t, t0, dict(tb=O(b['tb']), ts=O(b['ts'])))
        elif L == 'bars':
            g_bars(cv, t, t0, dict(ts=O(b['ts'])))
        elif L == 'phone':
            g_phone(cv, t, t0, dict(tw=O(b['tw'])))
        elif L == 'divers':
            g_divers(cv, t, t0, dict(tr=[O(x) for x in b['tr']], tz=O(b['tz'])))
        elif L == 'comment':
            g_comment(cv, t, t0, dict(tt=O(b['tt'])))
        elif L == 'dial':
            m, sc = panel_top(cv, 'dial.jpg', t, t0, src_box=(470, 150, 1610, 994))
            x0, y0 = m(880, 612); x1, y1 = m(1212, 678)
            pth = skia.Path(); pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 14, 14))
            trim_stroke(cv, pth, P(t, O(b['to']), 0.55), ACCENT, 4)
            pill(cv, 'ZAPROJEKTOWANY NA 11 000 m', 540, 730, P(t, O(b['to']) + 0.6, 0.6), ACCENT, 28)
        elif L == 'dim':
            m, sc = panel_top(cv, 'front_blue.jpg', t, t0, src_box=(0, 330, 1260, 1263))
            xa, ya = m(212, 405); xb, yb = m(1004, 405)
            pr = P(t, O(b['to']), 0.5)
            cxm = (xa + xb) / 2
            ln = skia.Path(); ln.moveTo(cxm, ya); ln.lineTo(xa, ya); ln.moveTo(cxm, ya); ln.lineTo(xb, ya)
            trim_stroke(cv, ln, pr, ACCENT, 4)
            for xx in (xa, xb):
                tk = skia.Path(); tk.moveTo(xx, ya - 26); tk.lineTo(xx, ya + 26)
                trim_stroke(cv, tk, P(t, O(b['to']) + 0.45, 0.2), ACCENT, 4)
            pill(cv, '⌀ 50 mm · KOPERTA', 540, 730, P(t, O(b['to']) + 0.6, 0.45), ACCENT, 28)
        elif L == 'sapph':
            m, sc = panel_top(cv, 'dial2.jpg', t, t0, src_box=(220, 70, 1180, 780))
            x0, y0 = m(428, 196); x1, y1 = m(962, 574)
            ov = skia.Path(); ov.addOval(skia.Rect(x0, y0, x1, y1))
            trim_stroke(cv, ov, P(t, O(b['to']), 0.6), ACCENT, 4)
            pill(cv, 'SZKŁO SZAFIROWE · 9,5 mm', 540, 730, P(t, O(b['to']) + 0.6, 0.6), ACCENT, 28)
        elif L == 'cameron':
            zin = ease((t - O(b['z1'])) / 0.6); zout = ease((t - O(b['z2'])) / 0.55)
            z = 1 + 1.25 * zin * (1 - zout)
            m, sc = panel_top(cv, 'cameron.webp', t, t0, src_box=(93, 0, 1760, 1235), zoom=z, zfocus=(1395, 150), zfull=2.25)
            wx, wy = m(1393, 88)
            ring = skia.Path(); ring.addCircle(wx, wy, 58 * sc)
            ra = 1 - zout
            trim_stroke(cv, ring, P(t, O(b['z1']) + 0.6, 0.4) * ra, ACCENT, 4)
            pp = P(t, O(b['z1']) + 0.9, 0.5)
            if pp > 0 and ra > 0: pill(cv, 'PROTOTYP NA RAMIENIU ROBOTA', 540, 730, pp, ACCENT, 26, a=ra)
            na = P(t, O(b['z2']) + 0.55, 0.3)
            if na > 0: pill(cv, 'JAMES CAMERON', 540, 730, 1.0, TEXT, 28, a=na)
    if L in ('beam',):
        pass
    if b['layout'] == 'beam' and not hook_variant:
        pass
    caption(cv, t)

def render_beam(t, cv, b, fi):
    pass

# beam layout handled separately (asset full)
_orig_render = render
def render2(t, cv, hook_variant=None):
    b = beat_at(t)
    if b['layout'] == 'beam':
        raw = raw_of(t); fi = min(2643, int(round(raw * FPS)))
        cv.drawImage(BG, 0, 0)
        t0 = b['t0']
        asset_full(cv, 'beam.jpg', t, t0, src_box=(40, 0, 800, 985), fade_from=1060, fade_to=1400)
        g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, 420)], [C('#03070C', 0.6).toColor(), C('#03070C', 0).toColor()]))
        cv.drawRect(skia.Rect(0, 0, W, 420), g)
        a = P(t, t0 + 0.25, 0.3)
        label(cv, 'ZAPROJEKTOWANY NA', 1000, 1080, 1.0, ACCENT, 26, align='left', a=0)
        text(cv, '11 000 m', 360, 1225, font('big', 124), TEXT, a, track=-3, shadow=True)
        label(cv, 'GŁĘBOKOŚCI BEZ POWROTU', 366, 1285, P(t, t0 + 0.6, 0.6), ACCENT, 24, a=a)
        circle_me(cv, fi, 190, 1200, 250, t, t0)
        caption(cv, t)
        return
    _orig_render(t, cv, hook_variant)

def frame_rgba(t, hook_variant=None):
    global BG
    if BG is None: BG = make_bg()
    s = skia.Surface(W, H); cv = s.getCanvas()
    render2(t, cv, hook_variant)
    a = s.makeImageSnapshot().toarray()
    return np.ascontiguousarray(a[..., [2, 1, 0, 3]])  # BGRA -> RGBA

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        out = sys.argv[2]
        for tt in sys.argv[3:]:
            arr = frame_rgba(float(tt))
            Image.fromarray(arr[..., :3]).save(f"{out}_{float(tt):06.2f}.jpg", quality=92)
    elif mode == 'range':
        a, b, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        hv = sys.argv[5] if len(sys.argv) > 5 else None
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709',
                               '-color_primaries', 'bt709', '-color_trc', 'bt709', outp], stdin=subprocess.PIPE)
        for f in range(a, b):
            arr = frame_rgba(f / FPS, hv)
            ff.stdin.write(arr.tobytes())
        ff.stdin.close(); ff.wait()
    elif mode == 'info':
        print('DUR', DUR, 'NFRAMES', NFRAMES)
        for b in BEATS: print(round(b['t0'], 2), b['layout'], b.get('big', ''))
