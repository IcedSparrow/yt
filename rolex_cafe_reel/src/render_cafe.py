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
BG_TOP, BG_BOT = '#1A130F', '#070504'
ACCENT = '#D9B36C'     # gold
ACCENT2 = '#4FB58A'    # green
TEXT = '#F6F1EA'
MUTED = '#A99B8C'
PANEL = '#1E1612'
FD = '/usr/share/fonts/opentype/inter/'; FJ = '/usr/share/fonts/truetype/jetbrains-mono/'
TF = {'big': skia.Typeface.MakeFromFile(FD + 'InterDisplay-Bold.otf'),
      'cap': skia.Typeface.MakeFromFile(FD + 'Inter-SemiBold.otf'),
      'med': skia.Typeface.MakeFromFile(FD + 'Inter-Medium.otf'),
      'mono': skia.Typeface.MakeFromFile(FJ + 'JetBrainsMono-Medium.ttf')}
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

# ---------------- footage (real camera frame, never cut out) ----------------
FR = np.load('frames.npy', mmap_mode='r'); NRAW = FR.shape[0]
SW, SH = 436, 778
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

WIN = dict(y0=660, y1=1420, src_top=60, scale=1.6)
def draw_window(cv, fi, t=0, t0=-1):
    s = WIN['scale']; h = WIN['y1'] - WIN['y0']
    sy0 = WIN['src_top']; sy1 = int(sy0 + h / s)
    img = foot_img(fi, (0, sy0, SW, sy1), s)
    w = img.width(); x0 = (W - w) / 2
    r = skia.RRect.MakeRectXY(skia.Rect(x0, WIN['y0'], x0 + w, WIN['y0'] + img.height()), 34, 34)
    sp = paint('#000000', 0.6); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 8, WIN['y0'] + 24, x0 + w - 8, WIN['y0'] + img.height() + 24), 34, 34), sp)
    cv.save(); cv.clipRRect(r, True); cv.drawImage(img, x0, WIN['y0']); cv.restore()
    cv.drawRRect(r, paint(ACCENT, 0.38, stroke=2))
    f = font('mono', 18); tag = 'ZEGARKIDAWIDA'; tw_ = tw(tag, f, 3)
    tr = skia.RRect.MakeRectXY(skia.Rect(x0 + 22, WIN['y0'] + 22, x0 + 22 + tw_ + 52, WIN['y0'] + 62), 20, 20)
    cv.drawRRect(tr, paint('#070504', 0.62))
    cv.drawCircle(x0 + 44, WIN['y0'] + 42, 5, paint(ACCENT, 0.95))
    text(cv, tag, x0 + 58, WIN['y0'] + 49, f, TEXT, 0.9, track=3)

def bokeh(cv, t, a=1.0):
    for i in range(12):
        sx = (i * 397 % 1000) / 1000; sy = (i * 619 % 1000) / 1000
        x = 60 + sx * 960 + math.sin(t * 0.35 + i) * 30
        y = (sy * 2100 - t * (14 + i % 5 * 6)) % 2100 - 90
        r = 26 + (i * 37 % 50)
        p = paint(ACCENT if i % 3 else ACCENT2, (0.045 + 0.03 * ((i * 13) % 3)) * a)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.45))
        cv.drawCircle(x, y, r, p)

def circle_me(cv, fi, cx, cy, d, t, t0):
    k = ease((t - t0 - 0.30) / 0.30) if t0 >= 0 else 1.0
    if k <= 0: return
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
    cv.drawCircle(cx, cy, r, paint(ACCENT, 0.55 * k, stroke=3))

def make_bg():
    s = skia.Surface(W, H); cv = s.getCanvas()
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C(BG_TOP).toColor(), C(BG_BOT).toColor()])))
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial((160, -100), 950, [C(ACCENT, 0.10).toColor(), C(ACCENT, 0).toColor()])))
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial((1000, 1100), 800, [C('#1E4A3A', 0.16).toColor(), C('#1E4A3A', 0).toColor()])))
    return s.makeImageSnapshot()
BG = None

def entrance(t, t0, d=0.34):
    k = ease((t - t0) / d); return k, (1 - k) * 48

def top_word(cv, lines, t, t0, kw=None, lab=None, fi=0, size=118, accent=None):
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
        fnt = font('big', f_); lw = tw(ln, fnt, -2); xx = 540 - lw / 2
        col = ACCENT if accent == i else TEXT
        nch = max(1, len(ln))
        for ci, ch in enumerate(ln):
            if d <= 0.02: kc = 1.0
            else:
                st = t0 + d * 0.55 * ci / nch
                kc = ease((t - st) / (d * 0.45 + 1e-6))
            if kc > 0 and ch != ' ':
                text(cv, ch, xx, y + (1 - kc) * 22, fnt, col, kc, shadow=True)
            xx += fnt.measureText(ch) - 2
    pu = P(t, t0 + max(d, 0.02) + 0.06, 0.38)
    if pu > 0 and y + 22 < limit:
        half = lw * 0.5 * pu
        cv.drawRect(skia.Rect(540 - half, y + 16, 540 + half, y + 20), paint(ACCENT, 0.95))

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
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 28, 28)
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 6, y0 + 18, x1 - 6, y1 + 18), 28, 28), sp)
    cv.drawRRect(r, paint(PANEL, 0.95 * k))
    cv.save(); cv.clipRRect(r, True)
    cv.drawRect(skia.Rect(x0, y0, x1, y0 + 90), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y0), (0, y0 + 90)], [C('#FFFFFF', 0.06 * k).toColor(), C('#FFFFFF', 0).toColor()])))
    cv.restore()
    cv.drawRRect(r, paint(border, ba * k, stroke=2))

def img_card(cv, name, t, t0, src_box, box=(110, 70, 970, 600), lab=None, lab_t=None, white=False):
    k, dy = entrance(t, t0)
    x0, y0, x1, y1 = box; y0 += dy; y1 += dy
    r = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 34, 34)
    sp = paint('#000000', 0.55 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 28))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 6, y0 + 24, x1 - 6, y1 + 24), 34, 34), sp)
    cv.save(); cv.clipRRect(r, True)
    kb = 1 + 0.05 * clamp((t - t0) / 3.5)
    m = draw_cover(cv, name, (x0, y0, x1, y1), alpha=k, src_box=src_box, zoom=kb, zfocus=((src_box[0] + src_box[2]) / 2, (src_box[1] + src_box[3]) / 2), zfull=2.0)
    if lab:
        g = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y1 - 170), (0, y1)], [C('#000000', 0).toColor(), C('#070504', 0.8 * k).toColor()]))
        cv.drawRect(skia.Rect(x0, y1 - 170, x1, y1), g)
    cv.restore()
    cv.drawRRect(r, paint('#FFFFFF', 0.14 * k, stroke=2))
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
    text(cv, 'Poszedłbyś?', 540, 200, font('big', 112), TEXT, k, align='center', track=-2, shadow=True)
    y0 = 300; r = skia.RRect.MakeRectXY(skia.Rect(90, y0, 990, y0 + 150), 75, 75)
    cv.drawRRect(r, paint(PANEL, 0.96 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.18 * k, stroke=2))
    cv.drawCircle(165, y0 + 75, 42, paint('#2A1F18', k)); cv.drawCircle(165, y0 + 75, 42, paint(ACCENT, 0.7 * k, stroke=2))
    text(cv, 'Ty', 165, y0 + 88, font('cap', 34), TEXT, k, align='center')
    s = 'Tak, byle bez listy oczekujących'
    pr = P(t, o['tt'], 1.2)
    if pr <= 0: text(cv, 'Dodaj komentarz…', 232, y0 + 90, font('med', 38), MUTED, 0.8 * k)
    else:
        n = int(len(s) * pr); f = font('med', 38)
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
    y0 = 70; r = skia.RRect.MakeRectXY(skia.Rect(80, y0, 1000, y0 + 170), 85, 85)
    sp = paint('#000000', 0.5 * k); sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 24))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(90, y0 + 18, 990, y0 + 188), 85, 85), sp)
    cv.drawRRect(r, paint(PANEL, 0.96 * k)); cv.drawRRect(r, paint('#FFFFFF', 0.12 * k, stroke=2))
    bp = skia.Path(); bp.addRRect(r); trim_stroke(cv, bp, P(t, t0 + 0.1, 0.9), ACCENT, 3, k)
    cv.drawCircle(165, y0 + 85, 55, paint('#2A1F18', k)); cv.drawCircle(165, y0 + 85, 55, paint(ACCENT, k, stroke=3))
    text(cv, 'ZD', 165, y0 + 100, font('big', 42), ACCENT, k, align='center')
    text(cv, '@zegarkidawida', 240, y0 + 101, font('cap', 44), TEXT, k)
    tap = o['tap']; pr = clamp((t - tap) / 0.24)
    s = 1 - 0.07 * math.sin(math.pi * pr) if 0 < pr < 1 else 1
    done = t >= tap + 0.12
    bx0, bx1, by0, by1 = 712, 966, y0 + 45, y0 + 125; bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
    cv.save(); cv.translate(bcx, bcy); cv.scale(s, s); cv.translate(-bcx, -bcy)
    br = skia.RRect.MakeRectXY(skia.Rect(bx0, by0, bx1, by1), 40, 40)
    if not done:
        cv.drawRRect(br, paint(ACCENT, k)); text(cv, 'Obserwuj', bcx, bcy + 12, font('cap', 34), '#070504', k, align='center')
    else:
        cv.drawRRect(br, paint(PANEL, k)); cv.drawRRect(br, paint(ACCENT, k, stroke=2))
        text(cv, 'Obserwujesz', bcx, bcy + 12, font('cap', 30), ACCENT, k, align='center')
    cv.restore()
    if 0 < pr < 1.6:
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
        m, k = asset_full(cv, 'sub_coffee.jpg', t, -1, (0, 250, 1512, 1594), top=440)
        label(cv, 'ROLEX CAFE  ·  ZNAK TOWAROWY', 540, 150, 1.0, ACCENT, 26, align='center', track=4)
        text(cv, 'Kawa od', 540, 262, font('big', 112), TEXT, 1, align='center', track=-2, shadow=True)
        text(cv, 'Rolexa?', 540, 380, font('big', 112), ACCENT, 1, align='center', track=-2, shadow=True)
        circle_me(cv, fi, 185, 650, 250, t, -1)
    elif L == 'hookB':   # user's own cover (concept) + circle
        m, k = asset_full(cv, 'cafe_concept.png', t, -1, (0, 0, 916, 1188), top=0, bottom=1400, fade_from=1150)
        label(cv, 'WIZUALIZACJA', 60, 1375, 1.0, MUTED, 20)
        circle_me(cv, fi, 830, 1215, 300, t, -1)
    elif L == 'hookC':   # me full + big word
        draw_full(cv, fi)
        top_word(cv, ['ROLEX CAFE?'], t, -1, None, 'KAWA OD ROLEXA', fi, 120, accent=0)
    elif L == 'full':
        pv = punch_val(t, b.get('punch'))
        draw_full(cv, fi, pv)
        if b.get('follow'): follow_card(cv, t, t0, dict(tap=O(b['tap'])))
        else: top_word(cv, b['big'], t, t0, b.get('kw'), b.get('lab'), fi, b.get('size', 118), b.get('accent'))
    elif L == 'circle':
        m, k = asset_full(cv, b['img'], t, t0, tuple(b['box']))
        if b.get('ring'):
            cx, cy = m[0](*b['ring'][:2]); rr = b['ring'][2] * m[1]
            pth = skia.Path(); pth.addCircle(cx, cy, rr)
            trim_stroke(cv, pth, P(t, O(b['ring_t']), 0.55), ACCENT, 6)
        if b.get('count'):
            pc = P(t, O(b['pill_t']), 0.25)
            if pc > 0:
                n = int(round(100000 * eout((t - O(b['pill_t'])) / 0.8) / 1000)) * 1000
                pill(cv, f"ROLEX  ≈ {n:,} zł".replace(',', ' '), b.get('pill_x', 540), b.get('pill_y', 1290), 1.0, ACCENT, 28, a=pc)
        elif b.get('pill'): pill(cv, b['pill'], b.get('pill_x', 540), b.get('pill_y', 1290), P(t, O(b['pill_t']), 0.5), ACCENT, 28)
        circle_me(cv, fi, b.get('cx', 180), b.get('cy', 1180), 250, t, t0)
    else:
        bokeh(cv, t)
        draw_window(cv, fi)
        if L == 'card':
            m, k = img_card(cv, b['img'], t, t0, tuple(b['box']), tuple(b.get('cbox', (110, 70, 970, 600))), b.get('lab'),
                            O(b['lab_t']) if b.get('lab_t') else None)
            if b.get('ring'):
                cx, cy = m[0](*b['ring'][:2]); rr = b['ring'][2] * m[1]
                pth = skia.Path(); pth.addCircle(cx, cy, rr)
                trim_stroke(cv, pth, P(t, O(b['ring_t']), 0.5), ACCENT, 5)
            if b.get('steam'):
                sx, sy = m[0](*b['steam']); steam(cv, sx, sy, sy - 120, t, P(t, t0 + 0.4, 0.5))
            if b.get('under'):
                label(cv, b['under'], 540, b['cbox'][3] + 70, P(t, t0 + 0.35, 0.6), MUTED, 24, align='center', a=k)
        elif L == 'doc': g_doc(cv, t, t0, dict(td=O(b['td']), tr=O(b['tr']), tm=O(b['tm']), tc=O(b['tc']), ts=O(b['ts'])))
        elif L == 'pin': g_pin(cv, t, t0, dict(tp=O(b['tp']), tn=O(b['tn'])))
        elif L == 'brands': g_brands(cv, t, t0, dict(tt=[O(x) for x in b['tt']]))
        elif L == 'funnel': g_funnel(cv, t, t0, dict(t1=O(b['t1']), t2=O(b['t2']), t3=O(b['t3'])))
        elif L == 'wait': g_wait(cv, t, t0, dict(tc=O(b['tc']), ts=O(b['ts'])))
        elif L == 'comment': g_comment(cv, t, t0, dict(tt=O(b['tt'])))
    caption(cv, t)

TR = 0.30
_ramp = None
def _snap(t, hv, force=None):
    s = skia.Surface(W, H); cv = s.getCanvas(); render(t, cv, hv, force)
    return s.makeImageSnapshot().toarray()
def frame_rgba(t, hv=None):
    global BG
    if BG is None: BG = make_bg()
    b = beat_at(t); i = BEATS.index(b)
    a = _snap(t, hv)
    if i > 0 and b['layout'] != 'hook' and t - b['t0'] < TR and BEATS[i - 1]['layout'] != b['layout'] and not (hv and i - 1 == 0):
        prev = _snap(t, hv, BEATS[i - 1]).astype(np.float32)
        p = ease((t - b['t0']) / TR)
        front = -140 + p * (H + 280)
        y = np.arange(H, dtype=np.float32)
        m = np.clip((front - y) / 140.0, 0, 1)[:, None, None]
        out = prev * (1 - m) + a.astype(np.float32) * m
        # thin gold light at the wipe front
        ly = int(front - 70)
        if 0 <= ly < H - 3:
            gold = np.array([108, 179, 217, 255], np.float32)  # BGRA of ACCENT
            out[ly:ly + 3] = out[ly:ly + 3] * 0.35 + gold * 0.65
        a = np.clip(out, 0, 255).astype(np.uint8)
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
