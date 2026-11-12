# Rolex Cafe reel — frame renderer (skia + PIL), 1080x1920 @30. Real camera footage only (no cut-outs).
import numpy as np, json, math, sys, os, subprocess
import skia
from PIL import Image, ImageFilter

W, H, FPS = 1080, 1920, 30
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def C(hexs, a=1.0):
    hexs = hexs.lstrip('#'); r, g, b = int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16)
    return skia.Color4f(r/255, g/255, b/255, a)
# ---- brand: espresso + gold (+ Rolex green as second accent) ----
BG_TOP, BG_BOT = '#10201A', '#050B08'
ACCENT = '#B89A5E'     # muted antique gold
ACCENT2 = '#EFE8DA'    # ivory
RED = '#7A2E33'        # burgundy
TEXT = '#EFE8DA'
MUTED = '#9E9C8C'
PANEL = '#11211A'
FD = '/usr/share/fonts/opentype/inter/'; FJ = '/usr/share/fonts/truetype/jetbrains-mono/'
FO = '/tmp/claude-0/-home-user-yt/518eefe0-9fd3-5fc6-a870-afc36e74b829/scratchpad/fonts/'
TF = {'big': skia.Typeface.MakeFromFile(FO + 'CormorantGaramond_600SemiBold.ttf'),
      'bigi': skia.Typeface.MakeFromFile(FO + 'CormorantGaramond_500Medium_Italic.ttf'),
      'cap': skia.Typeface.MakeFromFile(FO + 'CormorantGaramond_600SemiBold.ttf'),
      'capi': skia.Typeface.MakeFromFile(FO + 'CormorantGaramond_600SemiBold_Italic.ttf'),
      'med': skia.Typeface.MakeFromFile(FO + 'CormorantGaramond_500Medium.ttf'),
      'mono': skia.Typeface.MakeFromFile(FO + 'Cinzel_500Medium.ttf')}
def font(k, size):
    f = skia.Font(TF[k], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); return f

KEEP = json.load(open('keep.json'))
OUT_STARTS = []; acc = 0.0
for a, b in KEEP: OUT_STARTS.append(acc); acc += b - a
DUR = acc; NFRAMES = int(round(DUR * FPS))
def raw_of(t):
    for (a, b), s in zip(KEEP, OUT_STARTS):
        if t < s + (b - a) - 1e-9: return a + (t - s)
    return KEEP[-1][1] - 1e-3
def O(r):
    for (a, b), s in zip(KEEP, OUT_STARTS):
        if r < a: return s
        if r <= b: return s + (r - a)
    return DUR

CAPS = json.load(open('captions.json')); CAP_Y = 1500
exec(open('_helpers.py').read())
def hairframe(cv, x0, y0, x1, y1, a=1.0, col=None, r=6, inset=9):
    col = col or ACCENT
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r), paint(col, 0.85 * a, stroke=1.6))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + inset, y0 + inset, x1 - inset, y1 - inset), max(1, r - 3), max(1, r - 3)), paint(col, 0.40 * a, stroke=1.0))
def pill(cv, s, cx, y, prog=1.0, col=ACCENT, size=30, fill=PANEL, a=1.0):
    if prog <= 0: return
    a = a * clamp(prog * 4)
    f = font('mono', size - 2); full = tw(s, f, 4)
    w = full + 70; h = size + 40
    cv.drawRect(skia.Rect(cx - w/2, y - h/2, cx + w/2, y + h/2), paint('#0A1510', 0.86 * a))
    hairframe(cv, cx - w/2, y - h/2, cx + w/2, y + h/2, a, col, r=2, inset=6)
    label(cv, s, cx - full / 2, y + size * 0.33, prog, col, size - 2, a=a, track=4)
def caption(cv, t):
    cur = None
    for i, (s_, rs, re_, kws) in enumerate(CAPS):
        st = O(rs) - 0.03
        nxt = O(CAPS[i+1][1]) - 0.03 if i + 1 < len(CAPS) else DUR + 1
        en = min(nxt, O(re_) + 0.6)
        if st <= t < en: cur = (i, s_, kws); break
    if not cur: return
    i, s_, kws = cur
    words = s_.split(' '); size = 76
    def wfont(w):
        bare = w.strip(',.!?—:;„”').lower()
        return bare, any(bare == k.lower() or (k.lower() in bare and len(k) > 3) for k in kws)
    while True:
        fs = [font('capi' if wfont(w)[1] else 'cap', size) for w in words]
        space = fs[0].measureText(' ')
        total = sum(f.measureText(w) for f, w in zip(fs, words)) + space * (len(words) - 1)
        if total <= 840 or size <= 52: break
        size -= 2
    x = 500 - total / 2
    t_s, t_e = O(CAPS[i][1]), O(CAPS[i][2]); tot = sum(len(w) for w in words); acc_ = 0
    for w, f in zip(words, fs):
        wst = t_s + (t_e - t_s) * acc_ / max(1, tot); acc_ += len(w)
        lit = 1.0 if i == 0 else 0.68 + 0.32 * clamp((t - wst + 0.04) / 0.14)
        col = ACCENT if wfont(w)[1] else TEXT
        text(cv, w, x, CAP_Y, f, col, lit, shadow=True)
        x += f.measureText(w) + space


# ---------------- footage (real camera frame, never cut out) ----------------
FR = np.load('frames.npy', mmap_mode='r'); NRAW = FR.shape[0]
SW, SH = 464, 826
FACES = np.array(json.load(open('faces.json')), float)
def grade(rgb):
    x = rgb.astype(np.float32) / 255
    l = x.mean(2, keepdims=True)
    x = l + (x - l) * 1.03
    x = (x - 0.5) * 1.06 + 0.5 - 0.012
    return np.clip(x * 255, 0, 255).astype(np.uint8)
def foot_img(fi, box, scale):
    x0, y0, x1, y1 = box
    a = grade(np.array(FR[fi, y0:y1, x0:x1]))
    im = Image.fromarray(a, 'RGB')
    tw_, th_ = int(round((x1 - x0) * scale)), int(round((y1 - y0) * scale))
    im = im.resize((tw_, th_), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=max(1.2, scale * 0.5), percent=60, threshold=2))
    arr = np.dstack([np.asarray(im), np.full((th_, tw_), 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.ColorType.kRGBA_8888_ColorType)

S_FULL = 1080 / SW
def draw_full(cv, fi, punch=1.0, anchor=(540, 820)):
    img = foot_img(fi, (0, 0, SW, SH), S_FULL)
    cv.save()
    if punch != 1.0:
        cv.translate(anchor[0], anchor[1]); cv.scale(punch, punch); cv.translate(-anchor[0], -anchor[1])
    cv.drawImage(img, 0, 0)
    cv.restore()
    # gentle edge falloff (light in the room), top a bit stronger for the big word
    g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, 360)], [C('#070504', a).toColor() for a in (0.78, 0.6, 0.3, 0.1, 0.0)], [0, 0.3, 0.6, 0.85, 1.0]))
    cv.drawRect(skia.Rect(0, 0, W, 360), g)
    g2 = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 1250), (0, H)], [C('#070504', a).toColor() for a in (0.0, 0.12, 0.45, 0.68, 0.75)], [0, 0.15, 0.4, 0.65, 1.0]))
    cv.drawRect(skia.Rect(0, 1250, W, H), g2)

WIN = dict(y0=660, y1=1420, src_top=60, scale=1.4)
def draw_window(cv, fi, t=0, t0=-1):
    s = WIN['scale']; h = WIN['y1'] - WIN['y0']
    sy0 = WIN['src_top']; sy1 = int(sy0 + h / s)
    img = foot_img(fi, (0, sy0, SW, sy1), s)
    w = img.width(); x0 = (W - w) / 2
    y0w = WIN['y0']; y1w = y0w + img.height()
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0w, x0 + w, y1w), 4, 4)
    sp = paint('#000000', 0.55); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    cv.drawRect(skia.Rect(x0 + 8, y0w + 24, x0 + w - 8, y1w + 24), sp)
    cv.save(); cv.clipRRect(r, True); cv.drawImage(img, x0, y0w); cv.restore()
    hairframe(cv, x0 - 14, y0w - 14, x0 + w + 14, y1w + 14, 1.0, ACCENT, r=3, inset=6)

def bokeh(cv, t, a=1.0):
    return
    for i in range(12):
        sx = (i * 397 % 1000) / 1000; sy = (i * 619 % 1000) / 1000
        x = 60 + sx * 960 + math.sin(t * 0.35 + i) * 30
        y = (sy * 2100 - t * (14 + i % 5 * 6)) % 2100 - 90
        r = 26 + (i * 37 % 50)
        p = paint(ACCENT if i % 3 else ACCENT2, (0.045 + 0.03 * ((i * 13) % 3)) * a)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.45))
        cv.drawCircle(x, y, r, p)

def circle_me(cv, fi, cx, cy, d, t, t0):
    k = 1.0
    f = FACES[min(fi, NRAW - 1)]
    fcx, fcy = f[0] + f[2] / 2, f[1] + f[2] * 0.55
    span = f[2] * 1.55; s = d / span
    box = (int(max(0, fcx - span / 2)), int(max(0, fcy - span / 2)), int(min(SW, fcx + span / 2)), int(min(SH, fcy + span / 2)))
    img = foot_img(fi, box, s)
    r = d / 2
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    cv.drawCircle(cx, cy + 10, r, sp)
    cv.save(); path = skia.Path(); path.addCircle(cx, cy, r); cv.clipPath(path, True)
    p = skia.Paint(AntiAlias=True); p.setAlphaf(k)
    cv.drawImage(img, cx - (fcx - box[0]) * s, cy - (fcy - box[1]) * s, skia.SamplingOptions(), p)
    cv.restore()
    cv.drawCircle(cx, cy, r, paint(ACCENT, 0.9 * k, stroke=1.6)); cv.drawCircle(cx, cy, r + 8, paint(ACCENT, 0.45 * k, stroke=1.0))

_VID = {}
def vid(name, lt):
    if name not in _VID: _VID[name] = np.load(name + '.npy', mmap_mode='r')
    a = _VID[name]; i = int(clamp(lt * 30, 0, a.shape[0] - 1))
    rgb = np.array(a[i])
    arr = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.ColorType.kRGBA_8888_ColorType)

def make_bg():
    s = skia.Surface(W, H); cv = s.getCanvas()
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C(BG_TOP).toColor(), C(BG_BOT).toColor()])))
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial((160, -100), 950, [C(ACCENT, 0.10).toColor(), C(ACCENT, 0).toColor()])))
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial((1000, 1100), 800, [C('#2A3F7A', 0.18).toColor(), C('#2A3F7A', 0).toColor()])))
    return s.makeImageSnapshot()
BG = None

def entrance(t, t0, d=0.5):
    k = ease((t - t0) / d); return k, (1 - k) * 18

def top_word(cv, lines, t, t0, kw=None, lab=None, fi=0, size=118, accent=None, strikes=None):
    """big word above the head in FULL; sized to the highest hair point of this beat."""
    d = 0.30 if kw is None else clamp(O(kw) - t0 - 0.06, 0.0, 0.30)
    k = 1.0 if d <= 0.02 else ease((t - t0) / d)
    limit = BEAT_HAIR(t0) - 18   # screen y the text must stay above
    y = 58
    if lab:
        label(cv, lab, 540, y + 22, 1.0, ACCENT, 26, align='center', a=k, track=5); y += 34
    n = len(lines)
    fs = min(size, (limit - y - 10) / (0.95 * n))
    for i, ln in enumerate(lines):
        f_ = fs
        while tw(ln, font('big', f_), -2) > 960: f_ -= 3
        y += f_ * 0.95
        fnt = font('bigi' if accent == i else 'big', f_ * 1.08); lw = tw(ln, fnt, 0)
        col = TEXT
        kk = 1.0 if d <= 0.02 else ease((t - t0 - 0.05 * i) / max(d, 0.2))
        if kk > 0: text(cv, ln, 540, y + (1 - kk) * 12, fnt, col, kk, align='center', shadow=True)
        for sub, st_raw in (strikes or []):
            j = ln.find(sub)
            if j < 0: continue
            sx0 = 540 - lw / 2 + tw(ln[:j], fnt, -2) - 6; sx1 = sx0 + tw(sub, fnt, -2) + 12
            ps = P(t, O(st_raw), 0.32)
            if ps > 0:
                yy = y - f_ * 0.34
                cv.drawRect(skia.Rect(sx0, yy - 4, sx0 + (sx1 - sx0) * ps, yy + 4), paint(RED, 1.0))
    pu = P(t, t0 + max(d, 0.02) + 0.05, 0.5)
    if pu > 0 and y + 26 < limit and not strikes:
        half = min(lw, 520) * 0.5 * pu; yy = y + 20
        cv.drawRect(skia.Rect(540 - half, yy - 0.8, 540 - 14, yy + 0.8), paint(ACCENT, 0.9))
        cv.drawRect(skia.Rect(540 + 14, yy - 0.8, 540 + half, yy + 0.8), paint(ACCENT, 0.9))
        dm = skia.Path(); dm.moveTo(540, yy - 6); dm.lineTo(546, yy); dm.lineTo(540, yy + 6); dm.lineTo(534, yy); dm.close()
        cv.drawPath(dm, paint(ACCENT, pu))

_hair_cache = {}
def BEAT_HAIR(t0):
    if t0 in _hair_cache: return _hair_cache[t0]
    b = beat_at(t0 + 1e-3); i = BEATS.index(b)
    t1 = BEATS[i + 1]['t0'] if i + 1 < len(BEATS) else DUR
    fis = [min(NRAW - 1, int(round(raw_of(tt) * FPS))) for tt in np.arange(t0, t1, 1 / FPS)]
    hy = min(FACES[f][1] - 0.36 * FACES[f][2] for f in fis) * S_FULL
    _hair_cache[t0] = hy; return hy

# ---------------- top-panel graphics ----------------
TOP = 640
def card(cv, x0, y0, x1, y1, k=1.0, border=ACCENT, ba=0.35):
    sp = paint('#000000', 0.45 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    cv.drawRect(skia.Rect(x0 + 6, y0 + 18, x1 - 6, y1 + 18), sp)
    cv.drawRect(skia.Rect(x0, y0, x1, y1), paint(PANEL, 0.96 * k))
    hairframe(cv, x0, y0, x1, y1, k, ACCENT, r=3, inset=9)

def img_card(cv, name, t, t0, src_box, box=(110, 70, 970, 600), lab=None, lab_t=None, white=False):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = box; y0 += dy; y1 += dy
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 3, 3)
    sp = paint('#000000', 0.55 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 28))
    cv.drawRect(skia.Rect(x0 + 6, y0 + 24, x1 - 6, y1 + 24), sp)
    cv.save(); cv.clipRRect(r, True)
    kb = 1 + 0.04 * clamp((t - t0) / 4.0)
    m = draw_cover(cv, name, (x0, y0, x1, y1), alpha=k, src_box=src_box, zoom=kb, zfocus=((src_box[0] + src_box[2]) / 2, (src_box[1] + src_box[3]) / 2), zfull=2.0)
    if lab:
        g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y1 - 170), (0, y1)], [C('#000000', 0).toColor(), C('#070504', 0.8 * k).toColor()]))
        cv.drawRect(skia.Rect(x0, y1 - 170, x1, y1), g)
    cv.restore()
    hairframe(cv, x0 - 14, y0 - 14, x1 + 14, y1 + 14, k, ACCENT, r=3, inset=6)
    if lab: label(cv, lab, x0 + 44, y1 - 40, P(t, lab_t if lab_t is not None else t0 + 0.3, 0.55), ACCENT, 28, a=k)
    return m, k

def g_doc(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'USPTO · WNIOSEK O ZNAK TOWAROWY', x0 + 44, y0 + 66, 1.0, MUTED, 24, a=k)
    cv.drawRect(skia.Rect(x0 + 44, y0 + 92, x1 - 44, y0 + 94), paint('#FFFFFF', 0.10 * k))
    rows = [('ZNAK', 'ROLEX CAFE', o['tm']), ('ZGŁASZAJĄCY', 'Rolex SA', o['tr']), ('DATA', '30 września', o['td'])]
    yy = y0 + 170
    for i, (key, val, tt) in enumerate(rows):
        label(cv, key, x0 + 44, yy, 1.0, MUTED, 22, a=k)
        f = font('big', 64 if i == 0 else 44)
        n = int(len(val) * P(t, tt, 0.5 if i == 0 else 0.35))
        text(cv, val[:n], x0 + 340, yy + (8 if i == 0 else 4), f, ACCENT if i == 0 else TEXT, k, track=-1)
        yy += 92 if i == 0 else 78
    # class row (the line that matters)
    ry = y1 - 120
    label(cv, 'KLASA 43', x0 + 44, ry + 48, 1.0, MUTED, 22, a=k)
    text(cv, 'usługi kawiarniane', x0 + 340, ry + 52, font('big', 44), TEXT, k)
    pth = skia.Path(); pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 24, ry, x1 - 24, ry + 84), 20, 20))
    trim_stroke(cv, pth, P(t, o['tc'], 0.6), ACCENT2, 4, k)
    stamp(cv, x1 - 150, y0 + 255, t, o['ts'])

def steam(cv, cx, y_bot, y_top, t, a=1.0):
    for j, dx in enumerate((-34, 0, 34)):
        pth = skia.Path(); first = True
        for i in range(0, 41):
            u = i / 40; yy = y_bot - (y_bot - y_top) * u
            xx = cx + dx + math.sin(u * 5.0 - t * 2.2 + j * 1.7) * (6 + 10 * u)
            if first: pth.moveTo(xx, yy); first = False
            else: pth.lineTo(xx, yy)
        p = paint('#FFFFFF', 1.0, stroke=3)
        p.setShader(skia.GradientShader.MakeLinear([(0, y_bot), (0, y_top)], [C('#FFFFFF', 0.0).toColor(), C('#FFFFFF', 0.55 * a).toColor(), C('#FFFFFF', 0).toColor()], [0, 0.35, 1]))
        cv.drawPath(pth, p)

def stamp(cv, cx, cy, t, t1, s='ZŁOŻONO · USPTO'):
    pr = P(t, t1, 0.4)
    if pr <= 0: return
    f = font('mono', 20); w = tw(s, f, 4) + 44
    cv.save(); cv.translate(cx, cy); cv.rotate(-7)
    r = skia.Path(); r.addRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2, -28, w / 2, 28), 10, 10))
    trim_stroke(cv, r, pr, ACCENT2, 4)
    label(cv, s, -w / 2 + 22, 8, 1.0, ACCENT2, 20, a=P(t, t1 + 0.35, 0.25), track=4)
    cv.restore()

def watch_icon(cv, cx, cy, pr, col):
    if pr <= 0: return
    pth = skia.Path(); pth.addCircle(cx, cy, 26)
    pth.moveTo(cx - 14, cy - 24); pth.lineTo(cx - 12, cy - 42); pth.lineTo(cx + 12, cy - 42); pth.lineTo(cx + 14, cy - 24)
    pth.moveTo(cx - 14, cy + 24); pth.lineTo(cx - 12, cy + 42); pth.lineTo(cx + 12, cy + 42); pth.lineTo(cx + 14, cy + 24)
    pth.moveTo(cx, cy); pth.lineTo(cx, cy - 15); pth.moveTo(cx, cy); pth.lineTo(cx + 11, cy + 5)
    trim_stroke(cv, pth, pr, col, 3)

def g_pin(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    # dotted map texture
    for gx in range(x0 + 40, x1 - 20, 34):
        for gy in range(int(y0) + 40, int(y1) - 20, 34):
            cv.drawCircle(gx, gy, 1.6, paint('#FFFFFF', 0.10 * k))
    # stylised lake (crescent) drawing itself
    lk = skia.Path(); cx, cy = 430, y0 + 330
    lk.moveTo(cx - 230, cy - 30); lk.cubicTo(cx - 150, cy + 150, cx + 140, cy + 130, cx + 240, cy - 90)
    lk.cubicTo(cx + 230, cy - 20, cx + 120, cy + 10, cx + 40, cy + 30)
    lk.cubicTo(cx - 60, cy + 50, cx - 170, cy + 10, cx - 230, cy - 30); lk.close()
    cv.drawPath(lk, paint(ACCENT2, 0.16 * k * P(t, t0 + 0.6, 0.3)))
    trim_stroke(cv, lk, P(t, t0 + 0.15, 0.6), ACCENT2, 3, k)
    label(cv, 'JEZIORO GENEWSKIE', cx - 120, cy + 105, P(t, t0 + 0.6, 0.5), MUTED, 18, a=k)
    # pin drop (eased, no bounce) + ripple
    px, py = cx - 170, cy - 30
    pd = P(t, o['tp'], 0.45)
    if pd > 0:
        yy = py - 120 * (1 - pd)
        rp = clamp((t - o['tp'] - 0.45) / 0.7)
        if 0 < rp < 1: cv.drawCircle(px, py, 10 + 46 * eout(rp), paint(ACCENT, 0.6 * (1 - rp), stroke=2))
        pin = skia.Path(); pin.moveTo(px, yy); pin.cubicTo(px - 30, yy - 40, px - 26, yy - 74, px, yy - 76); pin.cubicTo(px + 26, yy - 74, px + 30, yy - 40, px, yy)
        cv.drawPath(pin, paint(ACCENT, pd)); cv.drawCircle(px, yy - 50, 10, paint(PANEL, pd))
    text(cv, 'GENEWA', 640, y0 + 160, font('big', 72), TEXT, P(t, o['tp'] + 0.5, 0.3), track=-1)
    label(cv, 'SZWAJCARIA', 644, y0 + 205, 1.0, MUTED, 22, a=P(t, o['tp'] + 0.5, 0.3))
    label(cv, 'F.P. JOURNE', 644, y0 + 300, P(t, o['tn'], 0.4), ACCENT, 34)
    label(cv, 'ZEGARMISTRZ · RESTAURACJA', 644, y0 + 345, P(t, o['tn'] + 0.4, 0.5), MUTED, 20)

def g_brands(cv, t, t0, o):
    k, _ = entrance(t, t0, 0.2)
    text(cv, 'Inne marki już to robią', 90, 92, font('big', 58), TEXT, k, track=-1)
    items = [('SAINT LAURENT', 'KAWIARNIA'), ('LOUIS VUITTON', 'KAWIARNIE I RESTAURACJE'), ('PRADA', 'KAWIARNIA')]
    for i, (nm, sub) in enumerate(items):
        kk = P(t, o['tt'][i], 0.35) * k
        x0 = 90; y0 = 140 + i * 162
        ph = skia.RRect.MakeRectXY(skia.Rect(x0, y0, 990, y0 + 145), 28, 28)
        if kk < 1: cv.drawRRect(ph, paint(ACCENT, 0.22 * k * (1 - kk), stroke=2))
        if kk <= 0: continue
        y0 += (1 - kk) * 30
        card(cv, x0, y0, 990, y0 + 145, kk, ACCENT, 0.3)
        text(cv, nm, x0 + 40, y0 + 92, font('big', 62), TEXT, kk, track=-1)
        label(cv, sub, 950, y0 + 84, 1.0, MUTED, 20, a=kk, align='right' if False else 'left') if False else label(cv, sub, 990 - 40 - tw(sub, font('mono', 20), 3), y0 + 84, 1.0, MUTED, 20, a=kk)

def g_funnel(cv, t, t0, o):
    k, _ = entrance(t, t0, 0.2)
    nodes = [('KAWA', 'za kilkanaście złotych', o['t1']), ('LOJALNOŚĆ', 'wobec marki', o['t2']), ('PIERWSZY ZEGAREK', 'kiedyś', o['t3'])]
    X = 150; ys = [130, 320, 510]
    for i, (nm, sub, tt) in enumerate(nodes):
        kk = P(t, tt, 0.35) * k
        if i > 0:
            ln = skia.Path(); ln.moveTo(X, ys[i - 1] + 30); ln.lineTo(X, ys[i] - 30)
            trim_stroke(cv, ln, P(t, tt - 0.35, 0.35), ACCENT, 3, k)
        if kk <= 0: continue
        cv.drawCircle(X, ys[i], 22, paint(PANEL, kk)); cv.drawCircle(X, ys[i], 22, paint(ACCENT if i < 2 else ACCENT2, kk, stroke=3))
        if i == 2: cv.drawCircle(X, ys[i], 9, paint(ACCENT2, kk))
        text(cv, nm, X + 60, ys[i] + 18, font('big', 64), TEXT if i < 2 else ACCENT2, kk, track=-1)
        label(cv, sub.upper(), X + 64, ys[i] + 62, 1.0, MUTED, 22, a=kk)
        if i == 2: watch_icon(cv, X + 60 + tw(nm, font('big', 64), -1) + 70, ys[i], P(t, tt + 0.4, 0.6), ACCENT2)

def g_wait(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 70 + dy, 980, 590 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'ROLEX CAFE · REZERWACJA STOLIKA', x0 + 44, y0 + 66, 1.0, MUTED, 24, a=k)
    label(cv, 'TWOJA POZYCJA NA LIŚCIE OCZEKUJĄCYCH', x0 + 44, y0 + 150, 1.0, ACCENT, 24, a=k)
    n = int(1 + 1247 * eout((t - o['tc']) / 1.1))
    text(cv, f"#{n:,}".replace(',', ' '), x0 + 40, y0 + 290, font('big', 150), TEXT, k, track=-3, shadow=True)
    pb = P(t, o['tc'] + 1.2, 0.4) * k
    if pb > 0:
        bx0, by = x0 + 44, y0 + 380; bw = (x1 - 44) - bx0
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx0 + bw, by + 14), 7, 7), paint('#FFFFFF', 0.08 * pb))
        fill = 0.02 + 0.03 * clamp((t - o['tc'] - 1.2) / 3)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx0 + bw * fill, by + 14), 7, 7), paint(ACCENT, pb))
        label(cv, 'SZACOWANY CZAS OCZEKIWANIA: ???', bx0, by + 58, P(t, o['tc'] + 1.4, 0.7), MUTED, 22, a=k)
    a = P(t, o['ts'], 0.3)
    label(cv, 'JAK W SALONIE ROLEXA', x0 + 44, y1 - 56, a, ACCENT2, 26, a=k)

def g_comment(cv, t, t0, o):
    k, _ = entrance(t, t0)
    text(cv, 'A Ty, co uważasz?', 540, 200, font('bigi', 104), TEXT, k, align='center', shadow=True)
    y0 = 300; r = skia.RRect.MakeRectXY(skia.Rect(90, y0, 990, y0 + 150), 4, 4)
    cv.drawRRect(r, paint(PANEL, 0.96 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.18 * k, stroke=2))
    cv.drawCircle(165, y0 + 75, 42, paint('#222A40', k)); cv.drawCircle(165, y0 + 75, 42, paint(ACCENT, 0.7 * k, stroke=2))
    text(cv, 'Ty', 165, y0 + 88, font('cap', 34), TEXT, k, align='center')
    s = 'Ponadczasowa elegancja.'
    pr = P(t, o['tt'], 1.2)
    if pr <= 0: text(cv, 'Dodaj komentarz…', 232, y0 + 92, font('bigi', 44), MUTED, 0.8 * k)
    else:
        n = int(len(s) * pr); f = font('bigi', 44)
        w = text(cv, s[:n], 232, y0 + 90, f, TEXT, k) or 0
        if pr < 1 or int(t * 2.5) % 2 == 0: cv.drawRect(skia.Rect(236 + w, y0 + 52, 239 + w, y0 + 100), paint(ACCENT, k))
    cv.drawCircle(925, y0 + 75, 40, paint(ACCENT, (0.35 + 0.65 * (pr >= 1)) * k))
    ar = skia.Path(); ar.moveTo(908, y0 + 75); ar.lineTo(942, y0 + 75); ar.moveTo(928, y0 + 60); ar.lineTo(943, y0 + 75); ar.lineTo(928, y0 + 90)
    cv.drawPath(ar, paint('#070504', k, stroke=5))
    # likes appear after the comment is sent
    lk = P(t, o['tt'] + 0.95, 0.25) * k
    if lk > 0:
        hx, hy = 150, y0 + 230; sc = 0.85 + 0.15 * lk
        hp = skia.Path(); hp.moveTo(hx, hy + 14 * sc)
        hp.cubicTo(hx - 34 * sc, hy - 8 * sc, hx - 16 * sc, hy - 30 * sc, hx, hy - 14 * sc)
        hp.cubicTo(hx + 16 * sc, hy - 30 * sc, hx + 34 * sc, hy - 8 * sc, hx, hy + 14 * sc)
        cv.drawPath(hp, paint('#E0565B', lk))
        n = int(1 + 127 * eout((t - o['tt'] - 1.0) / 0.7)) if t > o['tt'] + 1.0 else 1
        label(cv, f'{n} POLUBIEŃ', hx + 40, hy + 8, 1.0, MUTED, 22, a=lk)

def follow_card(cv, t, t0, o):
    k = clamp((t - t0) / 0.12 + 0.35)
    y0 = 70; r = skia.RRect.MakeRectXY(skia.Rect(80, y0, 1000, y0 + 170), 4, 4)
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 24))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(90, y0 + 18, 990, y0 + 188), 4, 4), sp)
    cv.drawRRect(r, paint(PANEL, 0.96 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.12 * k, stroke=2))
    bp = skia.Path(); bp.addRRect(r); trim_stroke(cv, bp, P(t, t0 + 0.1, 0.9), ACCENT, 3, k)
    cv.drawCircle(165, y0 + 85, 55, paint('#222A40', k)); cv.drawCircle(165, y0 + 85, 55, paint(ACCENT, k, stroke=3))
    text(cv, 'ZD', 165, y0 + 102, font('bigi', 48), ACCENT, k, align='center')
    text(cv, 'Zegarkidawida', 240, y0 + 104, font('big', 58), TEXT, k)
    tap = o['tap']; pr = clamp((t - tap) / 0.24)
    s = 1 - 0.07 * math.sin(math.pi * pr) if 0 < pr < 1 else 1
    done = t >= tap + 0.12
    bx0, bx1, by0, by1 = 712, 966, y0 + 45, y0 + 125; bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
    cv.save(); cv.translate(bcx, bcy); cv.scale(s, s); cv.translate(-bcx, -bcy)
    br = skia.RRect.MakeRectXY(skia.Rect(bx0, by0, bx1, by1), 3, 3)
    if not done:
        cv.drawRRect(br, paint(ACCENT, k)); text(cv, 'Obserwuj', bcx, bcy + 13, font('big', 42), '#0B140F', k, align='center')
    else:
        cv.drawRRect(br, paint(PANEL, k)); cv.drawRRect(br, paint(ACCENT, k, stroke=2))
        text(cv, 'Obserwujesz', bcx, bcy + 13, font('bigi', 38), ACCENT, k, align='center')
    cv.restore()
    if 0 < pr < 1.6:
        rr = 20 + 50 * clamp(pr / 1.6)
        cv.drawCircle(bcx + 40, bcy + 6, rr, paint('#FFFFFF', 0.5 * (1 - clamp(pr / 1.6)) * k, stroke=3))

# ======== Domino's graphics ========
def big_center(cv, s, y, size, col, a, maxw=900):
    while tw(s, font('big', size), -2) > maxw: size -= 3
    text(cv, s, 540, y, font('big', size), col, a, align='center', track=-2, shadow=True)

def g_tag(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    # price tag outline draws itself
    tx0, ty0, tx1, ty1 = 200, y0 + 150, 560, y0 + 400
    tg = skia.Path(); tg.moveTo(tx0 + 70, ty0); tg.lineTo(tx1, ty0); tg.lineTo(tx1, ty1); tg.lineTo(tx0 + 70, ty1); tg.lineTo(tx0, (ty0 + ty1) / 2); tg.close()
    tg.addCircle(tx0 + 62, (ty0 + ty1) / 2, 14)
    trim_stroke(cv, tg, P(t, t0 + 0.1, 0.6), TEXT, 4, k)
    st = skia.Path(); st.moveTo(tx0 + 50, (ty0 + ty1) / 2); st.cubicTo(tx0 - 20, ty0 - 40, tx0 + 60, ty0 - 110, tx0 + 120, ty0 - 120)
    trim_stroke(cv, st, P(t, t0 + 0.55, 0.4), MUTED, 3, k)
    a = P(t, t0 + 0.5, 0.3) * k
    label(cv, 'CENA', tx0 + 120, ty0 + 80, 1.0, MUTED, 26, a=a)
    text(cv, '— zł', tx0 + 116, ty0 + 190, font('big', 96), TEXT, a, track=-2)
    label(cv, 'ROLEX AIR-KING', 610, y0 + 210, P(t, t0 + 0.3, 0.5), ACCENT, 26, a=k)
    label(cv, "EDYCJA DOMINO'S", 610, y0 + 252, P(t, t0 + 0.6, 0.5), MUTED, 22, a=k)
    # red stamp on "kupić"
    pr = P(t, o['tk'], 0.35)
    if pr > 0:
        cv.save(); cv.translate(560, y0 + 330); cv.rotate(-8)
        s_ = 'NIE NA SPRZEDAŻ'; f = font('mono', 30); w = tw(s_, f, 4) + 60
        r = skia.Path(); r.addRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2, -40, w / 2, 40), 12, 12))
        trim_stroke(cv, r, pr, RED, 5)
        label(cv, s_, -w / 2 + 30, 11, 1.0, RED, 30, a=P(t, o['tk'] + 0.3, 0.2), track=4)
        cv.restore()

NODES = ['BULOVA', 'SEIKO', 'AIR-KING', 'OYSTER PERPETUAL']
def timeline(cv, y, lit, t, k, x0=150, x1=930):
    xs = [x0 + (x1 - x0) * i / 3 for i in range(4)]
    cv.drawRect(skia.Rect(x0, y - 1, x1, y + 1), paint('#FFFFFF', 0.16 * k))
    for i, x in enumerate(xs):
        p = P(t, lit[i], 0.35) if lit[i] is not None else 0
        if i > 0 and p > 0:
            cv.drawRect(skia.Rect(xs[i - 1], y - 2, xs[i - 1] + (x - xs[i - 1]) * p, y + 2), paint(ACCENT, k))
        cv.drawCircle(x, y, 14, paint(PANEL, k)); cv.drawCircle(x, y, 14, paint(ACCENT if p > 0 else MUTED, (0.5 + 0.5 * p) * k, stroke=3))
        if p > 0: cv.drawCircle(x, y, 7 * p, paint(ACCENT, k))
        f = font('mono', 20); s_ = NODES[i]
        lines = s_.split(' ') if len(s_) > 10 else [s_]
        for j, ln in enumerate(lines):
            text(cv, ln, x, y + 50 + j * 26, f, TEXT if p > 0 else MUTED, (0.55 + 0.45 * p) * k, align='center')

def g_timeline(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, o['year'], x0 + 44, y0 + 70, P(t, t0 + 0.1, 0.4), ACCENT, 30, a=k)
    if o.get('tp') is not None:
        a = P(t, o['tp'], 0.3) * k
        cv.drawCircle(x0 + 100, y0 + 170, 46, paint('#262A33', a)); cv.drawCircle(x0 + 100, y0 + 170, 46, paint(ACCENT, a, stroke=2))
        text(cv, 'TM', x0 + 100, y0 + 185, font('big', 38), ACCENT, a, align='center')
        text(cv, 'Tom Monaghan', x0 + 170, y0 + 172, font('big', 58), TEXT, a, track=-1)
        label(cv, "WSPÓŁZAŁOŻYCIEL DOMINO'S", x0 + 174, y0 + 212, P(t, o['tp'] + 0.25, 0.6), MUTED, 22, a=k)
    if o.get('title'):
        a = P(t, o['title_t'], 0.3) * k
        text(cv, o['title'], x0 + 44, y0 + 190 + (1 - a) * 16, font('big', 64), TEXT, a, track=-1)
    timeline(cv, y0 + 340, o['lit'], t, k)
    if o.get('queue') is not None:
        label(cv, 'KOLEJKA PO ZEGAREK', x0 + 44, y1 - 92, P(t, o['queue'][0], 0.4), MUTED, 20, a=k)
        for i, tq in enumerate(o['queue']):
            q = P(t, tq, 0.3) * k
            if q <= 0: continue
            cx = x0 + 380 + i * 82; cy = y1 - 92 + (1 - q) * 14
            cv.drawCircle(cx, cy - 18, 13, paint(TEXT if i == 0 else MUTED, q, stroke=3))
            sh = skia.Path(); sh.addArc(skia.Rect(cx - 24, cy, cx + 24, cy + 44), 180, 180)
            cv.drawPath(sh, paint(TEXT if i == 0 else MUTED, q, stroke=3))

def g_chat(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'FRANCZYZOBIORCA  →  TOM MONAGHAN', x0 + 44, y0 + 66, P(t, o['th'], 0.6), MUTED, 22, a=k)
    cv.drawRect(skia.Rect(x0 + 44, y0 + 92, x1 - 44, y0 + 94), paint('#FFFFFF', 0.08 * k))
    # incoming bubble (franchisee)
    cv.drawCircle(x0 + 80, y0 + 190, 30, paint('#222A40', k)); text(cv, 'F', x0 + 80, y0 + 202, font('big', 32), MUTED, k, align='center')
    q = o['q']; pr = P(t, o['tq'], o['dq'])
    bx0, by0 = x0 + 130, y0 + 140
    if pr <= 0:
        a = k * P(t, t0 + 0.2, 0.2)
        r = skia.RRect.MakeRectXY(skia.Rect(bx0, by0, bx0 + 150, by0 + 80), 28, 28); cv.drawRRect(r, paint('#2A2E37', a))
        for i in range(3):
            ph = 0.5 + 0.5 * math.sin(t * 7 - i * 0.9)
            cv.drawCircle(bx0 + 45 + i * 30, by0 + 40, 8, paint(MUTED, a * (0.35 + 0.65 * ph)))
    else:
        f = font('med', 38); n = int(len(q) * pr); s_ = q[:n]
        lines = []; cur = ''
        for wd in s_.split(' '):
            tst = (cur + ' ' + wd).strip()
            if tw(tst, f) > 620 and cur: lines.append(cur); cur = wd
            else: cur = tst
        lines.append(cur)
        full_lines = 2
        bw = 680; bh = 40 + 52 * max(len(lines), 1)
        r = skia.RRect.MakeRectXY(skia.Rect(bx0, by0, bx0 + bw, by0 + bh), 28, 28); cv.drawRRect(r, paint('#2A2E37', k))
        for j, ln in enumerate(lines): text(cv, ln, bx0 + 30, by0 + 62 + j * 52, f, TEXT, k)
    # reply: Tom is typing…
    ra = P(t, o['tr'], 0.35) * k
    if ra > 0 and not o['r']:
        rx1, ry0 = x1 - 44, y0 + 330
        r = skia.RRect.MakeRectXY(skia.Rect(rx1 - 150, ry0, rx1, ry0 + 80), 28, 28); cv.drawRRect(r, paint(ACCENT, ra))
        for i in range(3):
            ph = 0.5 + 0.5 * math.sin(t * 7 - i * 0.9)
            cv.drawCircle(rx1 - 105 + i * 30, ry0 + 40, 8, paint('#0B0C0F', ra * (0.35 + 0.65 * ph)))
        label(cv, 'TOM MONAGHAN PISZE…', rx1 - 330, ry0 + 125, 1.0, MUTED, 20, a=ra)
    if ra > 0 and o['r']:
        rx1, ry0 = x1 - 44, y0 + 330 + (1 - ra) * 20
        s_ = o['r']; f = font('cap', 38); w = tw(s_, f) + 60
        r = skia.RRect.MakeRectXY(skia.Rect(rx1 - w, ry0, rx1, ry0 + 92), 28, 28); cv.drawRRect(r, paint(ACCENT, ra))
        text(cv, s_, rx1 - w + 30, ry0 + 60, f, '#0B0C0F', ra)
        label(cv, 'TOM MONAGHAN', rx1 - w, ry0 + 130, 1.0, MUTED, 20, a=ra)

DAYS = ['PN', 'WT', 'ŚR', 'CZ', 'PT', 'SB', 'ND']
def g_money(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'WYZWANIE · SPRZEDAŻ PIZZY', x0 + 44, y0 + 66, 1.0, MUTED, 22, a=k)
    n = int(round(20000 * eout((t - o['tc']) / 0.9) / 100)) * 100 if t > o['tc'] else 0
    text(cv, f"${n:,}".replace(',', ' '), x0 + 40, y0 + 250, font('big', 170), ACCENT, k, track=-4, shadow=True)
    label(cv, 'CEL NA 1 TYDZIEŃ', x0 + 48, y0 + 305, P(t, o['tw'], 0.4), TEXT, 24, a=k)
    for i, dname in enumerate(DAYS):
        bx = x0 + 44 + i * 115; by = y0 + 360
        p = P(t, o['tw'] + i * 0.13, 0.22) * k
        r = skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + 100, by + 100), 18, 18)
        cv.drawRRect(r, paint('#FFFFFF', 0.06 * k)); cv.drawRRect(r, paint(ACCENT, (0.25 + 0.75 * p) * k, stroke=2))
        if p > 0: cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, by + 100 * (1 - p), bx + 100, by + 100), 18, 18), paint(ACCENT, 0.22 * p))
        text(cv, dname, bx + 50, by + 62, font('mono', 26), TEXT if p > 0.5 else MUTED, k, align='center')

def g_inflate(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'LATA 70.', x0 + 48, y0 + 90, 1.0, MUTED, 24, a=k)
    text(cv, '$20 000', x0 + 44, y0 + 200, font('big', 110), MUTED, k, track=-3)
    ar = skia.Path(); ar.moveTo(x0 + 120, y0 + 235); ar.lineTo(x0 + 120, y0 + 340); ar.moveTo(x0 + 100, y0 + 318); ar.lineTo(x0 + 120, y0 + 342); ar.lineTo(x0 + 140, y0 + 318)
    trim_stroke(cv, ar, P(t, o['ta'], 0.35), ACCENT, 4, k)
    a = P(t, o['tc'], 0.25) * k
    n = int(round(100000 * eout((t - o['tc']) / 0.7) / 1000)) * 1000 if t > o['tc'] else 0
    label(cv, 'DZIŚ', x0 + 48, y0 + 400, 1.0, ACCENT, 24, a=a)
    text(cv, f"${n:,}+".replace(',', ' '), x0 + 44, y0 + 505, font('big', 120), ACCENT, a, track=-3, shadow=True)

def slice_icon(cv, cx, cy, s, a):
    p = skia.Path(); p.moveTo(cx, cy + 40 * s); p.lineTo(cx - 30 * s, cy - 26 * s); p.quadTo(cx, cy - 42 * s, cx + 30 * s, cy - 26 * s); p.close()
    cv.drawPath(p, paint(ACCENT, a, stroke=3))
    for dx, dy_ in ((-8, -10), (9, 4), (-2, 18)):
        cv.drawCircle(cx + dx * s, cy + dy_ * s, 5 * s, paint(RED, a))

def g_pizzas(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'NA NIEGO TRZEBA BYŁO ZAROBIĆ', x0 + 44, y0 + 66, 1.0, MUTED, 22, a=k)
    cols, rows = 9, 3; n = cols * rows
    for i in range(n):
        tt = o['tg0'] + (o['tg1'] - o['tg0']) * i / n
        a = P(t, tt, 0.2) * k
        if a <= 0: continue
        cx = x0 + 90 + (i % cols) * 88; cy = y0 + 150 + (i // cols) * 100
        slice_icon(cv, cx, cy, 0.9, a)
    a = P(t, o['tn'], 0.3) * k
    text(cv, 'TYSIĄCE PIZZ', x0 + 44, y1 - 50, font('big', 82), TEXT, a, track=-2, shadow=True)


# ======== Royal / Patek graphics ========
def crown_icon(cv, cx, cy, s, pr, col=ACCENT, a=1.0):
    if pr <= 0: return
    p = skia.Path()
    p.moveTo(cx - 60 * s, cy + 30 * s); p.lineTo(cx - 70 * s, cy - 35 * s); p.lineTo(cx - 30 * s, cy - 2 * s)
    p.lineTo(cx, cy - 50 * s); p.lineTo(cx + 30 * s, cy - 2 * s); p.lineTo(cx + 70 * s, cy - 35 * s)
    p.lineTo(cx + 60 * s, cy + 30 * s); p.close()
    p.moveTo(cx - 60 * s, cy + 45 * s); p.lineTo(cx + 60 * s, cy + 45 * s)
    trim_stroke(cv, p, pr, col, 4, a)
    if pr >= 1:
        for dx, dy in ((-70, -35), (0, -50), (70, -35)): cv.drawCircle(cx + dx * s, cy + dy * s - 8 * s, 7 * s, paint(col, a))

def star_icon(cv, cx, cy, r, pr, col=ACCENT, a=1.0):
    if pr <= 0: return
    p = skia.Path()
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.42
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    p.close(); trim_stroke(cv, p, pr, col, 4, a)
    if pr >= 1: cv.drawPath(p, paint(col, 0.25 * a))

def g_model(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'PATEK PHILIPPE', x0 + 44, y0 + 80, P(t, o['tb'], 0.45), ACCENT, 34, a=k, track=6)
    label(cv, 'REFERENCJA', x0 + 48, y0 + 150, 1.0, MUTED, 20, a=k)
    parts = [('49', o['t1']), ('75', o['t2']), ('/1', o['t3']), ('G', o['t4'])]
    f = font('big', 190); x = x0 + 40
    for s_, tt in parts:
        a = P(t, tt, 0.22) * k
        w = f.measureText(s_)
        if a > 0: text(cv, s_, x, y0 + 345 + (1 - a) * 20, f, ACCENT if s_ == 'G' else TEXT, a, shadow=True)
        x += w - 4
    ag = P(t, o['t4'] + 0.25, 0.4) * k
    label(cv, 'G  =  ZŁOTO BIAŁE', x0 + 48, y0 + 420, 1.0, ACCENT, 24, a=ag)
    label(cv, 'PERŁY  ·  DIAMENTY', x0 + 48, y0 + 462, 1.0, MUTED, 22, a=ag)

def g_loan(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    text(cv, '2015', x0 + 40, y0 + 190, font('big', 170), ACCENT, k, track=-4, shadow=True)
    label(cv, 'LONDYN', x0 + 470, y0 + 180, P(t, t0 + 0.3, 0.5), MUTED, 24, a=k)
    # Queen -> Patek with arrow
    ya = y0 + 330
    ka = P(t, o['ta'] - 0.3, 0.3) * k
    crown_icon(cv, x0 + 120, ya, 0.6, P(t, o['ta'] - 0.3, 0.5), ACCENT, k)
    label(cv, 'KRÓLOWA', x0 + 70, ya + 80, 1.0, TEXT, 22, a=ka)
    ar = skia.Path(); ar.moveTo(x0 + 220, ya); ar.lineTo(x0 + 560, ya); ar.moveTo(x0 + 535, ya - 18); ar.lineTo(x0 + 562, ya); ar.lineTo(x0 + 535, ya + 18)
    trim_stroke(cv, ar, P(t, o['ta'], 0.5), ACCENT, 4, k)
    label(cv, 'WYPOŻYCZENIE', x0 + 290, ya - 24, P(t, o['ta'] + 0.2, 0.5), MUTED, 20, a=k)
    kp = P(t, o['ta'] + 0.45, 0.3) * k
    text(cv, 'PATEK', x0 + 600, ya + 12, font('big', 54), TEXT, kp)
    label(cv, 'PHILIPPE', x0 + 604, ya + 52, 1.0, MUTED, 20, a=kp)
    pill_a = P(t, o['tw'], 0.3)
    if pill_a > 0: pill(cv, 'WIELKA WYSTAWA · LONDYN', 540, y1 - 60, P(t, o['tw'], 0.5), ACCENT, 26, a=k)

def g_count(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'LONDYN · WYSTAWA PATEK PHILIPPE', x0 + 44, y0 + 66, P(t, t0 + 0.1, 0.5), MUTED, 22, a=k)
    cols, rows = 16, 5; nn = cols * rows
    for i in range(nn):
        tt = o['tg0'] + (o['tg1'] - o['tg0']) * i / nn
        a = P(t, tt, 0.15) * k
        if a <= 0: continue
        cx = x0 + 70 + (i % cols) * 49; cy = y0 + 120 + (i // cols) * 49
        cv.drawCircle(cx, cy, 14, paint(MUTED, 0.75 * a, stroke=2)); cv.drawCircle(cx, cy, 2.5, paint(MUTED, a))
    n = int(round(400 * eout((t - o['tc']) / 0.6))) if t > o['tc'] else 0
    a = P(t, o['tc'] - 0.15, 0.2) * k
    text(cv, f'≈{n}', x0 + 40, y1 - 70, font('big', 140), ACCENT, a, track=-3, shadow=True)
    label(cv, 'ZEGARKÓW', x0 + 360, y1 - 80, 1.0, TEXT, 30, a=a)

def g_rolex_wait(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'ZAMÓWIENIE SPECJALNE', x0 + 44, y0 + 70, 1.0, MUTED, 22, a=k)
    text(cv, 'Rolex  →  Zegarkidawida', x0 + 44, y0 + 175, font('big', 62), TEXT, P(t, o['tr'], 0.3) * k, track=-1)
    pb = P(t, o['tr'] + 0.2, 0.3) * k
    bx0, by = x0 + 44, y0 + 260; bw = x1 - 44 - bx0
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx0 + bw, by + 26), 13, 13), paint('#FFFFFF', 0.08 * pb))
    fill = 0.004 + 0.016 * clamp((t - o['tr'] - 0.3) / 2.5)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, by, bx0 + max(26, bw * fill), by + 26), 13, 13), paint(ACCENT, pb))
    label(cv, f'STATUS: OCZEKIWANIE…  {fill * 100:.1f}%', bx0, by + 72, 1.0, MUTED, 22, a=pb)
    dots = '.' * (1 + int(t * 3) % 3)
    label(cv, 'SZACOWANY CZAS: NIGDY' if t > o['tn'] else 'SZACOWANY CZAS' + dots, bx0, by + 116, 1.0, ACCENT if t > o['tn'] else MUTED, 22, a=pb)

def g_rank(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'NAJDROŻSZY ZEGAREK ŚWIATA', x0 + 44, y0 + 66, 1.0, MUTED, 22, a=k)
    bx0 = x0 + 44; bw = x1 - 44 - bx0
    # current record
    ka = P(t, t0 + 0.2, 0.4) * k
    label(cv, 'REKORD AUKCJI · PATEK GRANDMASTER CHIME 6300A', bx0, y0 + 140, 1.0, TEXT, 18, a=ka)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, y0 + 160, bx0 + bw * 0.62 * ka, y0 + 206), 14, 14), paint(MUTED, 0.85 * ka))
    text(cv, '31 mln $', bx0 + bw * 0.62 + 16, y0 + 196, font('big', 40), TEXT, ka)
    # the queen's watch
    kb = P(t, o['tq'], 0.7) * k
    label(cv, 'PATEK 4975/1G KRÓLOWEJ', bx0, y0 + 290, 1.0, ACCENT, 20, a=P(t, o['tq'] - 0.2, 0.3) * k)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx0, y0 + 310, bx0 + bw * 0.96 * kb, y0 + 356), 14, 14), paint(ACCENT, k * (kb > 0)))
    a2 = P(t, o['tq'] + 0.65, 0.3) * k
    text(cv, '???', bx0 + bw * 0.96 - 120, y0 + 440, font('big', 72), ACCENT, a2, track=-1)
    label(cv, '„W 100 PROCENTACH”', bx0, y0 + 420, 1.0, MUTED, 22, a=a2)

def g_scramble(cv, t, t0, o):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = 100, 60 + dy, 980, 600 + dy
    card(cv, x0, y0, x1, y1, k)
    label(cv, 'KATALOG · LOT I', x0 + 48, y0 + 74, 1.0, MUTED, 22, a=k, track=5)
    text(cv, 'Patek Philippe 4975/1G', x0 + 46, y0 + 160, font('big', 64), TEXT, k)
    text(cv, 'Własność Jej Królewskiej Mości', x0 + 48, y0 + 215, font('bigi', 40), MUTED, k)
    cv.drawRect(skia.Rect(x0 + 48, y0 + 250, x1 - 48, y0 + 251.5), paint(ACCENT, 0.6 * k))
    label(cv, 'ESTYMACJA', x0 + 48, y0 + 315, 1.0, MUTED, 22, a=k, track=5)
    f = font('big', 96); s_ = '£ —'
    text(cv, s_, x0 + 46, y0 + 425, f, TEXT, k)
    ps = P(t, o['ts'], 0.45)
    if ps > 0:
        w = f.measureText(s_)
        cv.drawRect(skia.Rect(x0 + 40, y0 + 388, x0 + 40 + (w + 16) * ps, y0 + 391), paint(ACCENT, k))
    text(cv, 'nie do wycenienia', x0 + 330, y0 + 425, font('bigi', 70), ACCENT, P(t, o['ts'] + 0.3, 0.45) * k)
    crown_icon(cv, x1 - 110, y0 + 110, 0.55, P(t, o['ts'] + 0.5, 0.7), ACCENT, k)

# ---------------- beats ----------------
BEATS = json.load(open('beats_om.json'))
for b in BEATS: b['t0'] = O(b['raw'])
def beat_at(t):
    cur = BEATS[0]
    for b in BEATS:
        if t >= b['t0'] - 1e-6: cur = b
    return cur
def punch_val(t, kw):
    if kw is None: return 1.0
    return 1.0 + 0.06 * ease((t - (O(kw) - 0.12)) / 0.42)

def asset_full(cv, name, t, t0, src_box, top=0, bottom=1400, fade_from=1120):
    k, _ = entrance(t, t0) if t0 >= 0 else (1.0, 0)
    kb = 1 + 0.045 * clamp((t - max(t0, 0)) / 3.5)
    m = draw_cover(cv, name, (0, top, W, bottom), alpha=k, src_box=src_box, zoom=kb, zfocus=((src_box[0] + src_box[2]) / 2, (src_box[1] + src_box[3]) / 2), zfull=2.0)
    if top > 0:
        cv.drawRect(skia.Rect(0, top - 1, W, top + 170), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, top - 1), (0, top + 170)], [C(BG_TOP, 1).toColor(), C(BG_TOP, 0).toColor()])))
    cv.drawRect(skia.Rect(0, fade_from, W, bottom + 2), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, fade_from), (0, bottom)], [C('#0B0806', 0).toColor(), C('#0B0806', 1).toColor()])))
    return m, k

def render(t, cv, hv=None, force=None):
    raw = raw_of(t); fi = min(NRAW - 1, int(round(raw * FPS)))
    cv.drawImage(BG, 0, 0)
    b = force or beat_at(t); L = b['layout']; t0 = b['t0']
    if hv and L == 'hook': L = hv
    if L == 'hook':
        zf = 1 + 0.06 * ease(t / 3.0)
        draw_cover(cv, 'queen_young.jpg', (0, 0, W, 1400), src_box=(0, 0, 739, 958), zoom=zf, zfocus=(330, 300), zfull=2.0)
        cv.drawRect(skia.Rect(0, 820, W, 1402), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 820), (0, 1400)], [C(BG_BOT, 0).toColor(), C(BG_BOT, 0.92).toColor(), C('#060C09', 1).toColor()], [0, 0.55, 1])))
        fr = skia.Path(); fr.addRect(skia.Rect(34, 34, 1046, 1366))
        trim_stroke(cv, fr, P(t, 0.0, 1.1), ACCENT, 1.6, 0.9)
        fr2 = skia.Path(); fr2.addRect(skia.Rect(44, 44, 1036, 1356))
        trim_stroke(cv, fr2, P(t, 0.15, 1.1), ACCENT, 1.0, 0.45)
        mx, my, rx, ry = 840, 760, 118, 150
        ov = skia.Path(); ov.addOval(skia.Rect(mx - rx, my - ry, mx + rx, my + ry))
        sp = paint('#000000', 0.6); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20)); cv.drawOval(skia.Rect(mx - rx, my - ry + 14, mx + rx, my + ry + 14), sp)
        cv.save(); cv.clipPath(ov, True)
        cv.drawRect(skia.Rect(mx - rx, my - ry, mx + rx, my + ry), paint('#F4F1EA', 1))
        draw_cover(cv, 'watch_white.jpg', (mx - rx, my - ry, mx + rx, my + ry), src_box=(45, 330, 485, 890))
        cv.restore()
        cv.drawOval(skia.Rect(mx - rx, my - ry, mx + rx, my + ry), paint(ACCENT, 1, stroke=3))
        cv.drawOval(skia.Rect(mx - rx - 10, my - ry - 10, mx + rx + 10, my + ry + 10), paint(ACCENT, 0.5, stroke=1.2))
        label(cv, 'PATEK PHILIPPE  ·  RÉF. 4975/1G', 540, 1072, 1.0, ACCENT, 24, align='center', track=6)
        text(cv, 'Zegarek Królowej', 540, 1196, font('big', 128), TEXT, 1, align='center', shadow=True)
        text(cv, 'stworzony wyłącznie dla Niej', 540, 1278, font('bigi', 62), ACCENT, 1, align='center', shadow=True)
        circle_me(cv, fi, 925, 190, 190, t, -1)
    elif L == 'hookB':
        draw_cover(cv, 'watch_black.jpg', (0, 0, W, 1400), src_box=(0, 150, 484, 778), zoom=1 + 0.07 * ease(t / 3.0), zfocus=(242, 470), zfull=2.0)
        cv.drawRect(skia.Rect(0, 880, W, 1402), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 880), (0, 1400)], [C('#000000', 0).toColor(), C('#000000', 0.9).toColor(), C('#060C09', 1).toColor()], [0, 0.55, 1])))
        hairframe(cv, 34, 34, 1046, 1366, 0.9, ACCENT, r=1, inset=10)
        label(cv, 'ZEGAREK KRÓLOWEJ ELŻBIETY II', 540, 1090, 1.0, ACCENT, 24, align='center', track=6)
        text(cv, 'Bezcenny.', 540, 1240, font('bigi', 170), TEXT, 1, align='center', shadow=True)
        text(cv, 'Nie da się go kupić.', 540, 1310, font('bigi', 54), ACCENT, P(t, 0.4, 0.6), align='center')
        circle_me(cv, fi, 925, 190, 190, t, -1)
    elif L == 'hookC':
        text(cv, 'Jedna Królowa.', 540, 175, font('big', 112), TEXT, 1, align='center', shadow=True)
        text(cv, 'Jeden zegarek.', 540, 285, font('bigi', 104), ACCENT, 1, align='center', shadow=True)
        for (nm, bx, lab_) in (('queen_fur.jpg', (150, 0, 560, 525), 'JEJ KRÓLEWSKA MOŚĆ'), ('watch_white.jpg', (30, 300, 500, 903), 'RÉF. 4975/1G')):
            x0 = 80 if nm == 'queen_fur.jpg' else 570; x1 = x0 + 430; y0, y1 = 360, 910
            sp = paint('#000000', 0.55); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26)); cv.drawRect(skia.Rect(x0 + 6, y0 + 22, x1 - 6, y1 + 22), sp)
            draw_cover(cv, nm, (x0, y0, x1, y1), src_box=bx, zoom=1 + 0.05 * ease(t / 3), zfocus=((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2), zfull=2.0)
            hairframe(cv, x0 - 16, y0 - 16, x1 + 16, y1 + 16, 1.0, ACCENT, r=1, inset=7)
            label(cv, lab_, (x0 + x1) / 2, y1 + 70, 1.0, ACCENT, 20, align='center', track=5)
        circle_me(cv, fi, 540, 1195, 230, t, -1)
    elif L == 'full':
        pv = punch_val(t, b.get('punch'))
        draw_full(cv, fi, pv)
        if b.get('follow'): follow_card(cv, t, t0, dict(tap=O(b['tap'])))
        else: top_word(cv, b['big'], t, t0, b.get('kw'), b.get('lab'), fi, b.get('size', 118), b.get('accent'), b.get('strikes'))
    elif L == 'circle':
        src = vid(b['vid'], b['v0'] + (t - t0)) if b.get('vid') else b['img']
        m, k = asset_full(cv, src, t, t0, tuple(b['box']), top=b.get('top', 0))
        if b.get('ring'):
            cx, cy = m[0](*b['ring'][:2]); rr = b['ring'][2] * m[1]
            pth = skia.Path(); pth.addCircle(cx, cy, rr)
            trim_stroke(cv, pth, P(t, O(b['ring_t']), 0.55), ACCENT, 6)
        for j, (ps, pt) in enumerate(b.get('pills', [])):
            if t >= O(pt) - 0.01:
                pill(cv, ps, b.get('pill_x', 540), b.get('pill_y', 150) + j * 92, P(t, O(pt), 0.5), ACCENT, 28)
        if b.get('icon'):
            ic, ix, iy, it = b['icon']
            if ic == 'crown': crown_icon(cv, ix, iy, 0.8, P(t, O(it), 0.6))
            else: star_icon(cv, ix, iy, 46, P(t, O(it), 0.6))
        circle_me(cv, fi, b.get('cx', 180), b.get('cy', 1180), b.get('cd', 250), t, t0)
    else:
        bokeh(cv, t)
        draw_window(cv, fi)
        if L == 'card':
            m, k = img_card(cv, b['img'], t, t0, tuple(b['box']), tuple(b.get('cbox', (110, 70, 970, 600))), None, None)
            if b.get('lab'): label(cv, b['lab'], 540, b.get('cbox', (110, 70, 970, 600))[3] + 46, P(t, O(b['lab_t']), 0.6), b.get('lab_col', ACCENT), 24, align='center', a=k)
            if b.get('ring'):
                cx, cy = m[0](*b['ring'][:2]); rr = b['ring'][2] * m[1]
                pth = skia.Path(); pth.addCircle(cx, cy, rr)
                trim_stroke(cv, pth, P(t, O(b['ring_t']), 0.5), b.get('ring_col', ACCENT), 5)
            if b.get('icon'):
                ic, ix, iy, it = b['icon']
                if ic == 'crown': crown_icon(cv, ix, iy, 0.6, P(t, O(it), 0.6))
                else: star_icon(cv, ix, iy, 40, P(t, O(it), 0.6))
        elif L == 'model': g_model(cv, t, t0, dict(tb=O(b['tb']), t1=O(b['t1']), t2=O(b['t2']), t3=O(b['t3']), t4=O(b['t4'])))
        elif L == 'loan': g_loan(cv, t, t0, dict(ty=O(b['ty']), ta=O(b['ta']), tw=O(b['tw'])))
        elif L == 'count': g_count(cv, t, t0, dict(tg0=O(b['tg0']), tg1=O(b['tg1']), tc=O(b['tc'])))
        elif L == 'rwait': g_rolex_wait(cv, t, t0, dict(tr=O(b['tr']), tn=O(b['tn'])))
        elif L == 'rank': g_rank(cv, t, t0, dict(tq=O(b['tq'])))
        elif L == 'scramble': g_scramble(cv, t, t0, dict(ts=O(b['ts'])))
        elif L == 'timeline':
            g_timeline(cv, t, t0, dict(year=b['year'], tp=O(b['tp']) if b.get('tp') else None,
                       lit=[O(x) if x is not None else None for x in b['lit']],
                       queue=[O(x) for x in b['queue']] if b.get('queue') else None,
                       title=b.get('title'), title_t=O(b['title_t']) if b.get('title_t') else 0))
        elif L == 'chat': g_chat(cv, t, t0, dict(th=O(b['th']), q=b['q'], tq=O(b['tq']), dq=O(b['tq_end']) - O(b['tq']), tr=O(b['tr']), r=b['r']))
        elif L == 'money': g_money(cv, t, t0, dict(tc=O(b['tc']), tw=O(b['tw'])))
        elif L == 'inflate': g_inflate(cv, t, t0, dict(ta=O(b['ta']), tc=O(b['tc'])))
        elif L == 'pizzas': g_pizzas(cv, t, t0, dict(tg0=O(b['tg0']), tg1=O(b['tg1']), tn=O(b['tn'])))
        elif L == 'comment': g_comment(cv, t, t0, dict(tt=O(b['tt'])))
    caption(cv, t)

TR = 0.45
def _snap(t, hv, force=None):
    s_ = skia.Surface(W, H); cv = s_.getCanvas(); render(t, cv, hv, force)
    return s_.makeImageSnapshot().toarray()
def frame_rgba(t, hv=None):
    global BG
    if BG is None: BG = make_bg()
    b = beat_at(t); i = BEATS.index(b)
    a = _snap(t, hv)
    if i > 0 and b['layout'] != 'hook' and t - b['t0'] < TR and not (BEATS[i - 1]['layout'] == 'full' and b['layout'] == 'full') and not (hv and i - 1 == 0):
        prev = _snap(t, hv, BEATS[i - 1]).astype(np.float32)
        p = ease((t - b['t0']) / TR)
        a = np.clip(prev * (1 - p) + a.astype(np.float32) * p, 0, 255).astype(np.uint8)
    return np.ascontiguousarray(a[..., [2, 1, 0, 3]])

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        out = sys.argv[2]; hv = None
        for tt in sys.argv[3:]:
            if tt.startswith('hv='): hv = tt[3:]; continue
            Image.fromarray(frame_rgba(float(tt), hv)[..., :3]).save(f"{out}_{float(tt):06.2f}.jpg", quality=92)
    elif mode == 'range':
        a, b, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        hv = sys.argv[5] if len(sys.argv) > 5 else None
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709',
                               '-color_primaries', 'bt709', '-color_trc', 'bt709', outp], stdin=subprocess.PIPE)
        for f in range(a, b): ff.stdin.write(frame_rgba(f / FPS, hv).tobytes())
        ff.stdin.close(); ff.wait()
    elif mode == 'info':
        print('DUR', DUR, 'NFRAMES', NFRAMES)
        for b in BEATS: print(round(b['t0'], 2), b['layout'], b.get('big', ''))
