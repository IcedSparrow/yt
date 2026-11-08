# Vacheron Constantin reel renderer (skia + ffmpeg)
import math, os, sys, json, subprocess
import numpy as np, cv2, skia

W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
UP = os.environ.get("VC_ASSETS", "/root/.claude/uploads/d39590b1-32f9-5337-8bd8-ff80190cfa08/")
FONTS = os.path.join(BASE, "..", "fonts")
FR = os.path.join(BASE, "frames", "%05d.jpg")

# ---------------- brand ----------------
INK = (14, 12, 10); PANEL = (27, 24, 21); CREAM = (245, 237, 225)
GOLD = (201, 164, 106); GOLDL = (224, 196, 146); OX = (150, 62, 56); MUTED = (168, 157, 143)

def col(c, a=1.0): return skia.Color(c[0], c[1], c[2], int(max(0, min(1, a)) * 255))

TF = {
    "serif": skia.Typeface.MakeFromFile(os.path.join(FONTS, "Cormorant-600.ttf")),
    "serif5": skia.Typeface.MakeFromFile(os.path.join(FONTS, "Cormorant-500.ttf")),
    "serifi": skia.Typeface.MakeFromFile(os.path.join(FONTS, "Cormorant-500i.ttf")),
    "semi": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"),
    "med": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Medium.otf"),
    "bold": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
    "xb": skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"),
}
_fc = {}
def font(k, s):
    key = (k, s)
    if key not in _fc:
        f = skia.Font(TF[k], s); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); _fc[key] = f
    return _fc[key]

def P(c, a=1.0, stroke=0, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def tw(text, f, track=0):
    return f.measureText(text) + track * max(0, len(text) - 1)

def text(c, s, x, y, f, paint, align="l", track=0):
    w = tw(s, f, track)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    if track == 0:
        c.drawString(s, x, y, f, paint)
    else:
        for ch in s:
            c.drawString(ch, x, y, f, paint); x += f.measureText(ch) + track
    return w

# ---------------- easing / timing ----------------
def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v
def eio(t): t = clamp(t); return 4*t*t*t if t < .5 else 1 - (-2*t+2)**3/2
def eout(t): t = clamp(t); return 1 - (1-t)**3
def eback(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
YEL = (255, 206, 84)
def prog(t, t0, d, fn=eio): return fn((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def lerp(a, b, k): return a + (b - a) * k

# keep segments (source frame index ranges, [a,b) )
KEEP_S = [(0, 3.00), (3.12, 15.62), (15.92, 20.26), (20.50, 30.36), (30.50, 45.52),
          (45.90, 53.60), (53.88, 57.68), (57.84, 61.54), (61.74, 63.15)]
KEEP = [(int(round(a*FPS)), min(1895, int(round(b*FPS)))) for a, b in KEEP_S]
SRC = []
for a, b in KEEP: SRC += list(range(a, b))
NF = len(SRC)
CUM = []; acc = 0
for a, b in KEEP: CUM.append(acc); acc += (b - a)

def O(raw):
    """raw seconds -> output seconds"""
    for (a, b), cu in zip(KEEP, CUM):
        if raw < a / FPS: return cu / FPS
        if raw < b / FPS: return (cu + raw * FPS - a) / FPS
    return NF / FPS
CUTS = [CUM[i] / FPS for i in range(1, len(KEEP))]

SFX = []  # (out_time, kind)
TRANS = []; SHAKE = []
def sfx(t, k): SFX.append((round(t, 3), k))
def trans(t): sfx(t, "whoosh"); TRANS.append(t + 0.14)
def shake(t, amp=10): SHAKE.append((t, amp))

def shine(c, r, p):
    if p <= 0 or p >= 1: return
    x = lerp(r.left() - 260, r.right() + 260, p)
    sh = skia.GradientShader.MakeLinear([skia.Point(x - 150, r.top()), skia.Point(x + 150, r.top() + 120)],
                                        [skia.Color(255, 255, 255, 0), skia.Color(255, 255, 255, 80), skia.Color(255, 255, 255, 0)])
    c.drawRect(r, skia.Paint(Shader=sh, BlendMode=skia.BlendMode.kPlus))

# ---------------- images ----------------
_img = {}
def IMG(name):
    if name not in _img:
        im = skia.Image.MakeFromEncoded(skia.Data.MakeFromFileName(UP + name))
        _img[name] = im.withDefaultMipmaps()
    return _img[name]
SMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
CUB = skia.SamplingOptions(skia.CubicResampler.Mitchell())

def cover_src(crop, dw, dh):
    x0, y0, x1, y1 = crop; cw, ch = x1-x0, y1-y0
    r = dw / dh
    if cw / ch > r: nw = ch * r; x0 += (cw - nw) / 2; cw = nw
    else: nh = cw / r; y0 += (ch - nh) / 2; ch = nh
    return (x0, y0, cw, ch)

# ---------------- layout constants ----------------
CIRC = (190, 1235, 130)       # cx, cy, r
CAP_Y = 1468                  # caption pill centre
LT_X = 360                    # lower third x

# ---------------- footage ----------------
def load_frame(i):
    im = cv2.imread(FR % i, cv2.IMREAD_COLOR)
    return im

def keys_val(keys, t):
    """keys: list of (t0, t1, v0, v1) transitions; returns value"""
    v = keys[0][2]
    for t0, t1, v0, v1 in keys:
        if t >= t1: v = v1
        elif t >= t0: v = lerp(v0, v1, eio((t - t0) / (t1 - t0))); break
        else: break
    return v

def draw_footage(c, bgr, m, z):
    cx, cy, r = CIRC
    # full rect (zoomed, anchored top-centre)
    fw, fh = W / z, H / z
    S0 = ((W - fw) / 2, 700 - 700 / z, fw, fh); D0 = (0, 0, W, H)
    S1 = (0, 244, 1080, 1080); D1 = (cx - r, cy - r, 2*r, 2*r)
    if m <= 0.001:
        img = skia.Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA), colorType=skia.kRGBA_8888_ColorType)
        c.drawImageRect(img, skia.Rect.MakeXYWH(*S0), skia.Rect.MakeXYWH(*D0), CUB, None, skia.Canvas.kStrict_SrcRectConstraint)
        return
    D = tuple(lerp(a, b, m) for a, b in zip(D0, D1))
    rad = lerp(0, r, m) if m < 1 else r
    sw = lerp(S0[2], S1[2], m); sh = sw * D[3] / D[2]
    scy = lerp(S0[1] + S0[3]/2, S1[1] + S1[3]/2, m)
    S = ((W - sw) / 2, scy - sh / 2, sw, sh)
    if m >= 0.999:
        x, y = int(S1[0]), int(S1[1])
        sub = cv2.resize(bgr[y:y+1080, x:x+1080], (2*r*2, 2*r*2), interpolation=cv2.INTER_AREA)
        img = skia.Image.fromarray(cv2.cvtColor(sub, cv2.COLOR_BGR2RGBA), colorType=skia.kRGBA_8888_ColorType)
        S = (0, 0, 4*r, 4*r); smp = CUB
    else:
        img = skia.Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA), colorType=skia.kRGBA_8888_ColorType).withDefaultMipmaps()
        smp = SMP
    dr = skia.Rect.MakeXYWH(*D); rr = skia.RRect.MakeRectXY(dr, rad, rad)
    # shadow + ring fade in with m
    sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.55 * m), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    c.save(); c.translate(0, 12); c.drawRRect(rr, sp); c.restore()
    c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
    c.drawImageRect(img, skia.Rect.MakeXYWH(*S), dr, smp, None, skia.Canvas.kStrict_SrcRectConstraint)
    c.restore()
    if m > 0.5:
        a = (m - 0.5) * 2
        c.drawRRect(rr, P(GOLD, a, 2.5))
        c.drawRRect(skia.RRect.MakeRectXY(dr.makeOutset(5, 5), rad + 5, rad + 5), P(GOLD, 0.25 * a, 1))

# ---------------- generic window ----------------
def win(t, t_in, t_out, fin=0.45, fout=0.3):
    if t < t_in or t > t_out + fout: return 0.0, 0.0
    pin = prog(t, t_in, fin, eout)
    pout = 1 - prog(t, t_out, fout, eio)
    return pin * pout, pin

# ---------------- elements ----------------
class El:
    z = 0
    def __init__(s, t_in, t_out, fin=0.45, fout=0.3):
        s.t_in, s.t_out, s.fin, s.fout = t_in, t_out, fin, fout
    def alive(s, t): return s.t_in <= t <= s.t_out + s.fout
    def draw(s, c, t): pass

def kb_scale(t, t_in, t_out, amt=0.03):
    return 1 + amt * clamp((t - t_in) / max(0.1, (t_out - t_in + 0.3)))

class Card(El):
    """floating rounded card with an image (L2) – pops in, light sweep"""
    z = 10
    def __init__(s, name, crop, rect, t_in, t_out, kids=(), radius=26, fin=0.4, fout=0.25, rise=0, kb=0.06):
        super().__init__(t_in, t_out, fin, fout)
        s.name, s.crop, s.rect, s.kids, s.radius, s.rise, s.kb = name, crop, rect, kids, radius, rise, kb
        if t_in > 0: sfx(t_in + 0.05, "pop")
    def geom(s, t):
        x, y, w, h = s.rect
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        sx, sy, sw, sh = cover_src(s.crop, w, h)
        k = kb_scale(t, s.t_in, s.t_out, s.kb)
        nsw, nsh = sw / k, sh / k
        src = (sx + (sw - nsw) / 2, sy + (sh - nsh) / 2, nsw, nsh)
        return a, (x, y, w, h), src
    def img2scr(s, t, px, py):
        a, (x, y, w, h), (sx, sy, sw, sh) = s.geom(t)
        return x + (px - sx) * w / sw, y + (py - sy) * h / sh
    def draw(s, c, t):
        a, (x, y, w, h), src = s.geom(t)
        if a <= 0: return
        pp = clamp((t - s.t_in) / 0.38)
        sc = lerp(0.8, 1.0, eback(pp)) if s.t_in > 0 else 1.0
        c.saveLayerAlpha(None, int(clamp(a * 1.6 if t < s.t_out else a) * 255))
        c.save(); c.translate(x + w / 2, y + h / 2); c.scale(sc, sc); c.translate(-(x + w / 2), -(y + h / 2))
        r = skia.Rect.MakeXYWH(x, y, w, h); rr = skia.RRect.MakeRectXY(r, s.radius, s.radius)
        sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.6), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
        c.save(); c.translate(0, 24); c.drawRRect(rr, sp); c.restore()
        c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
        c.drawImageRect(IMG(s.name), skia.Rect.MakeXYWH(*src), r, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
        shine(c, r, prog(t, s.t_in + 0.3, 0.7, eio))
        c.restore()
        c.drawRRect(rr, P(CREAM, 0.16, 1.5))
        c.restore()
        for k in s.kids: k.draw(c, t, s)
        c.restore()

class Bleed(El):
    """edge-to-edge image at top fading into ink (L3)"""
    z = 10
    def __init__(s, name, crop, t_in, t_out, kids=(), fin=0.3, fout=0.3, kb=0.07, y0=0):
        super().__init__(t_in, t_out, fin, fout)
        s.name, s.crop, s.kids, s.kb, s.y0 = name, crop, kids, kb, y0
        x0, y0_, x1, y1 = crop; s.hb = W * (y1 - y0_) / (x1 - x0)
    def geom(s, t):
        k = kb_scale(t, s.t_in, s.t_out, s.kb)
        x0, y0, x1, y1 = s.crop; cw, ch = x1 - x0, y1 - y0
        nw, nh = cw / k, ch / k
        return (x0 + (cw - nw) / 2, y0 + (ch - nh) / 2, nw, nh)
    def img2scr(s, t, px, py):
        sx, sy, sw, sh = s.geom(t)
        return (px - sx) * W / sw, s.y0 + (py - sy) * s.hb / sh
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        r = skia.Rect.MakeXYWH(0, s.y0, W, s.hb)
        c.drawImageRect(IMG(s.name), skia.Rect.MakeXYWH(*s.geom(t)), r, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
        g0 = s.y0 + s.hb - 400
        sh = skia.GradientShader.MakeLinear([skia.Point(0, g0), skia.Point(0, s.y0 + s.hb)], [col(INK, 0), col(INK, 1)])
        c.drawRect(skia.Rect.MakeLTRB(0, g0, W, s.y0 + s.hb + 1), skia.Paint(Shader=sh))
        for k in s.kids: k.draw(c, t, s)
        c.restore()

def stroke_partial(c, path, p, paint):
    if p <= 0: return
    if p >= 1: c.drawPath(path, paint); return
    pm = skia.PathMeasure(path, False); L = pm.getLength(); d = skia.Path()
    pm.getSegment(0, L * p, d, True); c.drawPath(d, paint)

class Outline:
    """rounded rectangle (image coords) that draws itself"""
    def __init__(s, box, t0, d=0.5, pad=10, color=GOLDL, w=3.5, radius=10, quad=None):
        s.box, s.t0, s.d, s.pad, s.color, s.w, s.radius, s.quad = box, t0, d, pad, color, w, radius, quad
        sfx(t0, "tick")
    def draw(s, c, t, parent):
        p = prog(t, s.t0, s.d, eio)
        if p <= 0: return
        if s.quad:
            pts = [parent.img2scr(t, *q) for q in s.quad]
            path = skia.Path(); path.moveTo(*pts[0])
            for q in pts[1:]: path.lineTo(*q)
        else:
            x0, y0 = parent.img2scr(t, s.box[0], s.box[1]); x1, y1 = parent.img2scr(t, s.box[2], s.box[3])
            r = skia.Rect.MakeLTRB(x0 - s.pad, y0 - s.pad, x1 + s.pad, y1 + s.pad)
            path = skia.Path(); path.addRRect(skia.RRect.MakeRectXY(r, s.radius, s.radius))
        stroke_partial(c, path, p, P(INK, 0.35, s.w + 3))
        stroke_partial(c, path, p, P(s.color, 1, s.w))

class Strike:
    def __init__(s, x0, x1, y, t0, d=0.35, color=OX):
        s.x0, s.x1, s.y, s.t0, s.d, s.color = x0, x1, y, t0, d, color
    def draw(s, c, t, parent=None):
        p = prog(t, s.t0, s.d, eio)
        if p > 0: c.drawLine(s.x0, s.y, lerp(s.x0, s.x1, p), s.y, P(s.color, 1, 5))

class Pill:
    """small tracked label pill placed in screen coords relative to parent card origin"""
    def __init__(s, txt, x, y, t0, d=0.35, fill=GOLD, fg=INK):
        s.txt, s.x, s.y, s.t0, s.d, s.fill, s.fg = txt, x, y, t0, d, fill, fg; sfx(t0, "pop")
    def draw(s, c, t, parent=None):
        p = prog(t, s.t0, s.d, eout)
        if p <= 0: return
        f = font("xb", 32); w = tw(s.txt, f, 3) + 48
        y = s.y
        sc = lerp(0.3, 1.0, eback(clamp((t - s.t0) / 0.32)))
        c.saveLayerAlpha(None, int(p * 255))
        c.translate(s.x + w / 2, y + 29); c.rotate(-4); c.scale(sc, sc); c.translate(-(s.x + w / 2), -(y + 29))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(s.x, y, w, 58), 29, 29), P(s.fill))
        text(c, s.txt, s.x + 22, y + 40, f, P(s.fg), track=3)
        c.restore()

class LowerThird(El):
    z = 20
    def __init__(s, label, name, t_in, t_out, strike=None, fout=0.3):
        super().__init__(t_in, t_out, 0.4, fout); s.label, s.name, s.strike = label, name, strike
        sfx(t_in, "tick")
        if strike: sfx(strike[1], "tick")
    def draw(s, c, t):
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        dx = (1 - pin) * 24
        c.saveLayerAlpha(None, int(a * 255))
        text(c, s.label, LT_X + dx, 1203, font("med", 25), P(GOLD), track=4.5)
        fn = font("serif", 56)
        text(c, s.name, LT_X + dx, 1268, fn, P(CREAM))
        if s.strike:
            word, t0 = s.strike
            pre = s.name[:s.name.index(word)]
            x0 = LT_X + dx + fn.measureText(pre) - 4; x1 = x0 + fn.measureText(word) + 8
            Strike(x0, x1, 1250, t0).draw(c, t)
        c.restore()

class BigWord(El):
    """me full frame, big word above head (L1): slams in or counts up"""
    z = 30
    def __init__(s, label, word, t_in, t_out, count=False):
        super().__init__(t_in, t_out, 0.2, 0.2); s.label, s.word, s.count = label, word, count
        s.land = t_in + (0.45 if count else 0.2)
        sfx(t_in, "swoosh_s"); sfx(s.land, "hit"); shake(s.land, 12)
    def draw(s, c, t):
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 430)], [col(INK, 0.66 * a), col(INK, 0)])
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 430), skia.Paint(Shader=sh))
        c.saveLayerAlpha(None, int(a * 255))
        text(c, s.label, W / 2, 168, font("xb", 27), P(YEL), "c", track=5)
        word = s.word; sc = 1.0
        if s.count and t < s.land:
            q = eout((t - s.t_in) / 0.45); v = int(round(lerp(int(word) - 90, int(word), q))); word = str(v)
        elif s.count:
            sc = 1 + 0.22 * (1 - eout((t - s.land) / 0.28))
        else:
            q = clamp((t - s.t_in) / 0.2); sc = lerp(1.9, 1.0, eout(q)) if q < 1 else 1 + 0.05 * (1 - eout((t - s.land) / 0.25))
        c.save(); c.translate(W / 2, 250); c.scale(sc, sc)
        f = font("serif", 136)
        sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.55), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        text(c, word, 0, 48, f, sp, "c")
        text(c, word, 0, 42, f, P(CREAM), "c")
        c.restore()
        c.restore()

# ---------- captions ----------
CAPS_RAW = [
 (0.00, "Oto fascynująca historia", []), (1.34, "Vacheron Constantin", ["Vacheron", "Constantin"]),
 (3.12, "Pierwszy warsztat", []), (3.80, "otworzył się w Genewie", ["Genewie"]),
 (4.72, "w 1755 roku,", ["1755"]), (6.44, "Jean-Marc Vacheron,", ["Jean-Marc", "Vacheron,"]),
 (7.70, "mający zaledwie 24 lata.", ["24", "lata."]),
 (9.18, "Dzięki temu marka", []), (9.84, "uznawana jest za", []),
 (11.02, "najstarszego producenta", ["najstarszego"]), (11.94, "zegarków na świecie,", []),
 (12.82, "który nieprzerwanie", ["nieprzerwanie"]), (13.62, "prowadzi swoją", []), (14.28, "działalność.", []),
 (15.94, "Przetrwali rewolucję", ["rewolucję"]), (16.78, "francuską", ["francuską"]),
 (17.28, "i dwie wojny światowe", ["dwie", "wojny", "światowe"]),
 (18.24, "i ani razu", []), (18.86, "nie przestali", ["nie", "przestali"]), (19.28, "produkować zegarków.", []),
 (20.56, "Nazwa, którą znamy", []), (21.36, "dzisiaj, pojawiła się", []), (22.06, "w 1819 roku,", ["1819"]),
 (23.60, "gdy przedsiębiorca", []), (24.56, "François Constantin", ["François", "Constantin"]),
 (25.48, "nawiązał współpracę", []), (26.48, "z wnukiem założyciela.", ["wnukiem"]),
 (27.36, "Firma przyjęła nazwę", []), (28.64, "Vacheron Constantin.", ["Vacheron", "Constantin."]),
 (30.50, "Kolejny przełom", ["przełom"]), (31.04, "nastąpił w 1839 roku,", ["1839"]),
 (33.34, "gdy do firmy dołączył", []), (34.20, "Georges-Auguste Leschot", ["Georges-Auguste", "Leschot"]),
 (35.42, "i wprowadził pantograf,", ["pantograf,"]), (36.60, "maszynę pozwalającą", []),
 (37.54, "na precyzyjne kopiowanie", ["precyzyjne"]), (38.66, "elementów zegarka.", []),
 (40.14, "To rozwiązanie", []), (40.60, "zrewolucjonizowało", ["zrewolucjonizowało"]), (41.44, "produkcję", []),
 (41.86, "i pozwoliło marce", []), (42.74, "ruszyć na podbój", ["podbój"]), (43.76, "światowych rynków.", ["światowych"]),
 (45.90, "Dziś Vacheron Constantin", ["Dziś"]), (47.16, "to część tak zwanej", []),
 (48.32, "Wielkiej Trójki", ["Wielkiej", "Trójki"]), (49.04, "szwajcarskiego", []), (49.66, "zegarmistrzostwa,", []),
 (50.64, "obok Patek Philippe", ["Patek", "Philippe"]), (51.68, "i Audemars Piguet.", ["Audemars", "Piguet."]),
 (53.88, "A jaki jest", []), (54.38, "wasz ulubiony model", ["ulubiony"]), (55.20, "Vacheron Constantin?", ["Vacheron", "Constantin?"]),
 (56.40, "Dajcie znać", []), (56.98, "w komentarzach.", ["komentarzach."]),
 (57.92, "Moim jest to zdecydowanie", ["zdecydowanie"]), (59.04, "Overseas", ["Overseas"]),
 (59.96, "i Historiques American.", ["Historiques", "American."]),
 (61.74, "Obserwuj po więcej.", ["Obserwuj"]),
]
CAPS = []
for i, (r, s_, k) in enumerate(CAPS_RAW):
    t0 = O(r) - 1 / FPS
    t1 = O(CAPS_RAW[i + 1][0]) - 1 / FPS if i + 1 < len(CAPS_RAW) else NF / FPS + 1
    CAPS.append((max(0, t0), t1, s_, k))
CAPF = font("xb", 64)

def draw_caption(c, t):
    for t0, t1, s_, keys in CAPS:
        if t0 <= t < t1:
            q = 1.0 if t0 <= 0.001 else clamp((t - t0) / 0.17)
            sc = lerp(0.72, 1.0, eback(q)); al = clamp(q * 3)
            words = s_.split(" "); size = 64
            f = font("xb", size)
            tot = sum(f.measureText(w_) for w_ in words) + f.measureText(" ") * (len(words) - 1)
            while tot > 880 and size > 44:
                size -= 2; f = font("xb", size)
                tot = sum(f.measureText(w_) for w_ in words) + f.measureText(" ") * (len(words) - 1)
            sp = f.measureText(" ")
            cx = 520; x0 = cx - tot / 2
            by = CAP_Y + size * 0.36
            c.save(); c.translate(cx, CAP_Y); c.scale(sc, sc); c.translate(-cx, -CAP_Y)
            c.saveLayerAlpha(None, int(255 * al))
            shp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.6), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
            stp = P((0, 0, 0), 1, 12)
            for pass_ in range(3):
                x = x0
                for w_ in words:
                    ww = f.measureText(w_)
                    if pass_ == 0: c.drawString(w_, x, by + 7, f, shp)
                    elif pass_ == 1: c.drawString(w_, x, by, f, stp)
                    else: c.drawString(w_, x, by, f, P(YEL if w_ in keys else (255, 255, 255)))
                    x += ww + sp
            c.restore(); c.restore()
            return

# ---------- special graphics ----------
def yx(year): return 120 + (year - 1755) / (2026 - 1755) * 840

class Timeline(El):
    z = 10
    def __init__(s, t_in, t_out, ev):
        super().__init__(t_in, t_out, 0.35, 0.3); s.ev = ev
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        e = s.ev; c.saveLayerAlpha(None, int(a * 255))
        LY = 720
        p = prog(t, e["lbl"], 0.35, eout)
        if p > 0:
            c.saveLayerAlpha(None, int(p * 255))
            text(c, "1755", 120, 676 + (1 - p) * 14, font("serif", 84), P(CREAM))
            text(c, "NIEPRZERWANIE OD 1755", W / 2, 260 + (1 - p) * 14, font("med", 25), P(GOLD), "c", track=5)
            c.restore()
        p = prog(t, e["line"], 1.0, eio)
        if p > 0:
            c.drawLine(120, LY, lerp(120, 960, p), LY, P(CREAM, 0.85, 3))
            c.drawCircle(120, LY, 8, P(GOLD))
            if p >= 1: c.drawCircle(960, LY, 8, P(GOLD))
            else: c.drawCircle(lerp(120, 960, p), LY, 6, P(GOLDL))
        p = prog(t, e["end"], 0.35, eout)
        if p > 0:
            c.saveLayerAlpha(None, int(p * 255)); text(c, "2026", 960, 676 + (1 - p) * 14, font("serif", 84), P(CREAM), "r"); c.restore()
        p = prog(t, e["big"], 0.15, eout)
        if p > 0:
            q = eout((t - e["big"]) / 0.7); v = int(round(271 * q))
            sc = 1 + 0.2 * (1 - eout((t - e["big"] - 0.7) / 0.3)) if q >= 1 else 1.0
            c.saveLayerAlpha(None, int(p * 255))
            c.save(); c.translate(W / 2, 420); c.scale(sc, sc)
            text(c, f"{v} lat", 0, 50, font("serif", 180), P(GOLDL), "c")
            c.restore(); c.restore()
        ticks = [("t1789", 1789, 1789, 810, "1789", "REWOLUCJA"),
                 ("t1914", 1914, 1918, 810, "1914–1918", "I WOJNA"),
                 ("t1939", 1939, 1945, 930, "1939–1945", "II WOJNA")]
        for key, y0, y1, ly, l1, l2 in ticks:
            p = prog(t, e[key], 0.4, eout)
            if p <= 0: continue
            xa, xb = yx(y0), yx(y1); xm = (xa + xb) / 2
            c.drawRect(skia.Rect.MakeLTRB(xa - 1.5, LY - 7, max(xb, xa + 3) + 1.5, LY + 7), P(OX, p))
            c.drawLine(xm, LY + 10, xm, LY + 10 + (ly - LY - 52) * p, P(CREAM, 0.6 * p, 2))
            c.saveLayerAlpha(None, int(p * 255))
            al = "l" if key == "t1789" else "c"
            xx = xm - 14 if al == "l" else xm
            text(c, l1, xx, ly + (1 - p) * 10, font("semi", 36), P(CREAM), al)
            text(c, l2, xx, ly + 38 + (1 - p) * 10, font("med", 24), P(MUTED), al, track=3.5)
            c.restore()
        c.restore()

def gear_path(cx, cy, R, n=14, h=0.13, ang=0.0, N=720):
    pts = []
    for i in range(N + 1):
        th = 2 * math.pi * i / N
        ph = (th * n / (2 * math.pi)) % 1.0
        # smooth trapezoid tooth profile
        if ph < 0.2: v = ph / 0.2
        elif ph < 0.5: v = 1
        elif ph < 0.7: v = 1 - (ph - 0.5) / 0.2
        else: v = 0
        v = 0.5 - 0.5 * math.cos(math.pi * v)
        r = R * (1 - h) + R * h * v
        pts.append((cx + r * math.cos(th + ang), cy + r * math.sin(th + ang)))
    return pts

def path_from(pts, close=False):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p

class Pantograph(El):
    z = 10
    def __init__(s, t_in, t_out, tr0, tr1):
        super().__init__(t_in, t_out, 0.35, 0.3); s.tr0, s.tr1 = tr0, tr1
        s.O = (150, 500); s.CT = (720, 860); s.R = 165; s.k = 0.5; s.L = 480
        s.tpl = gear_path(*s.CT, s.R, ang=-math.pi / 2)
        s.cc = (s.O[0] + s.k * (s.CT[0] - s.O[0]), s.O[1] + s.k * (s.CT[1] - s.O[1]))
        s.cp = gear_path(*s.cc, s.R * s.k, ang=-math.pi / 2)
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        text(c, "WYNALAZEK LESCHOTA · 1839", 120, 250, font("med", 25), P(GOLD), track=5)
        text(c, "Pantograf", 120, 345, font("serif", 96), P(CREAM))
        dash = skia.Paint(AntiAlias=True, Color=col(CREAM, 0.38), Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                          PathEffect=skia.DashPathEffect.Make([10, 8], 0))
        c.drawPath(path_from(s.tpl, True), dash)
        c.drawCircle(*s.CT, 12, P(CREAM, 0.38, 2))
        text(c, "WZÓR", s.CT[0], s.CT[1] + s.R + 62, font("med", 24), P(MUTED), "c", track=5)
        text(c, "KOPIA", s.cc[0], s.cc[1] + s.R * s.k + 56, font("med", 24), P(GOLD), "c", track=5)
        u = clamp((t - s.tr0) / (s.tr1 - s.tr0)); u = eio(u)
        n = len(s.tpl) - 1; i = int(u * n)
        T = s.tpl[i]
        if i > 0:
            c.drawPath(path_from(s.cp[:i + 1]), P(GOLDL, 1, 3.5))
        if u >= 1: c.drawCircle(*s.cc, 6 * s.k * 2, P(GOLDL, 1, 2.5))
        # linkage
        O_ = s.O; dx, dy = T[0] - O_[0], T[1] - O_[1]; d = math.hypot(dx, dy)
        h = math.sqrt(max(0, s.L ** 2 - (d / 2) ** 2))
        mx, my = O_[0] + dx / 2, O_[1] + dy / 2
        A = (mx - h * dy / d, my + h * dx / d)   # elbow below
        k = s.k
        D = (O_[0] + k * (A[0] - O_[0]), O_[1] + k * (A[1] - O_[1]))
        Pp = (O_[0] + k * dx, O_[1] + k * dy)
        E = (A[0] + k * (T[0] - A[0]), A[1] + k * (T[1] - A[1]))
        bar = P(CREAM, 0.82, 4)
        for p1, p2 in [(O_, A), (A, T), (D, Pp), (Pp, E)]:
            c.drawLine(*p1, *p2, bar)
        for j in (O_, A, D, E):
            c.drawCircle(*j, 8, P(INK)); c.drawCircle(*j, 8, P(GOLD, 1, 2.5))
        c.drawCircle(*O_, 13, P(GOLD, 1, 2))
        c.drawCircle(*T, 11, P(INK)); c.drawCircle(*T, 11, P(CREAM, 1, 2.5))
        c.drawCircle(*Pp, 7, P(GOLDL))
        c.restore()

class MapFX:
    def __init__(s, g, t_pulse, arcs):
        s.g, s.tp, s.arcs = g, t_pulse, arcs; sfx(t_pulse, "tick")
        for _, t0 in arcs: sfx(t0, "tick")
    def draw(s, c, t, parent):
        gx, gy = parent.img2scr(t, *s.g)
        p = prog(t, s.tp, 0.5, eout)
        if p <= 0: return
        c.drawCircle(gx, gy, 9, P(GOLDL, p)); c.drawCircle(gx, gy, 9, P(INK, 0.5 * p, 1.5))
        rp = prog(t, s.tp, 0.9, eout)
        if rp < 1: c.drawCircle(gx, gy, 9 + 46 * rp, P(GOLDL, (1 - rp) * 0.9, 2.5))
        c.saveLayerAlpha(None, int(p * 255))
        f = font("semi", 26); wpx = tw("GENÈVE", f, 3) + 30
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(gx - wpx / 2, gy - 72, wpx, 44), 22, 22), P(INK, 0.82))
        text(c, "GENÈVE", gx, gy - 41, f, P(GOLDL), "c", track=3)
        c.restore()
        for (ex, ey), t0 in s.arcs:
            q = prog(t, t0, 0.5, eio)
            if q <= 0: continue
            mx, my = (gx + ex) / 2, (gy + ey) / 2; dx, dy = ex - gx, ey - gy; L = math.hypot(dx, dy)
            cx_, cy_ = mx + dy / L * L * 0.22, my - dx / L * L * 0.22
            path = skia.Path(); path.moveTo(gx, gy); path.quadTo(cx_, cy_, ex, ey)
            stroke_partial(c, path, q, P(INK, 0.4, 7))
            stroke_partial(c, path, q, P(GOLDL, 1, 3.5))
            if q >= 1: c.drawCircle(ex, ey, 7, P(GOLDL)); c.drawCircle(ex, ey, 7, P(INK, 0.5, 1.5))

class BigThree(El):
    z = 10
    def __init__(s, t_in, t_out, tc, t_hero):
        super().__init__(t_in, t_out, 0.2, 0.3); s.tc, s.th = tc, t_hero
        sfx(t_in, "riser_end"); sfx(t_in + 0.18, "hit"); shake(t_in + 0.18, 14)
        for x in tc: sfx(x, "swoosh_s"); sfx(x + 0.3, "hit"); shake(x + 0.3, 11); sfx(x + 0.85, "tick")
        sfx(t_hero, "pop"); shake(t_hero + 0.1, 6)
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        # rotating light rays
        ra = prog(t, s.t_in, 0.6, eout)
        c.save(); c.translate(540, 740); c.rotate((t - s.t_in) * 9)
        rp = P(GOLD, 0.07 * ra)
        for i in range(16):
            th = math.radians(i * 22.5); dth = math.radians(5.5)
            pth = skia.Path(); pth.moveTo(0, 0)
            pth.lineTo(1300 * math.cos(th - dth), 1300 * math.sin(th - dth)); pth.lineTo(1300 * math.cos(th + dth), 1300 * math.sin(th + dth)); pth.close()
            c.drawPath(pth, rp)
        c.restore()
        vg = skia.GradientShader.MakeRadial(skia.Point(540, 740), 760, [col(INK, 0), col(INK, 0.9)])
        c.drawRect(skia.Rect.MakeWH(W, 1100), skia.Paint(Shader=vg))
        # title slam
        q = clamp((t - s.t_in) / 0.2); sc = lerp(2.0, 1.0, eout(q)) if q < 1 else 1 + 0.06 * (1 - eout((t - s.t_in - 0.2) / 0.3))
        text(c, "SZWAJCARSKIE ZEGARMISTRZOSTWO", W / 2, 228, font("xb", 26), P(YEL, clamp(q * 2)), "c", track=5)
        c.save(); c.translate(W / 2, 320); c.scale(sc, sc)
        c.saveLayerAlpha(None, int(clamp(q * 2) * 255))
        text(c, "Wielka Trójka", 0, 44, font("serif", 128), P(CREAM), "c")
        c.restore(); c.restore()
        cards = [("I", "Vacheron", "Constantin", 1755, "GENÈVE", True),
                 ("II", "Patek", "Philippe", 1839, "GENÈVE", False),
                 ("III", "Audemars", "Piguet", 1875, "LE BRASSUS", False)]
        cw, ch, y0 = 316, 560, 455
        for i, ((num, n1, n2, yr, city, hero), t0) in enumerate(zip(cards, s.tc)):
            pl = clamp((t - t0) / 0.4)
            if pl <= 0: continue
            x = 32 + i * 342
            yoff = -760 * (1 - eback(pl))
            land = t - t0 - 0.3
            sq = 1 - 0.05 * (1 - eout(land / 0.18)) if 0 <= land < 0.18 else 1.0
            c.save(); c.translate(x + cw / 2, y0 + ch + yoff); c.scale(1 / sq if sq < 1 else 1, sq); c.translate(-(x + cw / 2), -(y0 + ch))
            c.translate(0, yoff)
            c.saveLayerAlpha(None, int(clamp(pl * 4) * 255))
            r = skia.Rect.MakeXYWH(x, y0, cw, ch); rr = skia.RRect.MakeRectXY(r, 26, 26)
            sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.7), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 28))
            c.save(); c.translate(0, 26); c.drawRRect(rr, sp); c.restore()
            g = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y0 + ch)], [col((44, 38, 31)), col((17, 15, 13))])
            c.drawRRect(rr, skia.Paint(AntiAlias=True, Shader=g))
            c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
            shine(c, r, prog(t, t0 + 0.45, 0.6, eio))
            c.restore()
            c.drawRRect(rr, P(GOLD if hero else CREAM, 1 if hero else 0.22, 3 if hero else 1.5))
            cx = x + cw / 2
            text(c, num, cx, y0 + 100, font("serif", 74), P(GOLD), "c")
            c.drawLine(cx - 50, y0 + 128, cx + 50, y0 + 128, P(GOLD, 0.6, 2))
            text(c, n1, cx, y0 + 212, font("serif", 54), P(CREAM), "c")
            text(c, n2, cx, y0 + 266, font("serif", 54), P(CREAM), "c")
            text(c, "OD ROKU", cx, y0 + 352, font("xb", 22), P(MUTED), "c", track=4)
            cq = eout((t - t0 - 0.3) / 0.55); v = int(round(lerp(yr - 150, yr, cq)))
            text(c, str(v), cx, y0 + 436, font("xb", 74), P(YEL), "c")
            text(c, city, cx, y0 + 500, font("med", 22), P(MUTED), "c", track=4)
            c.restore(); c.restore()
        hp = clamp((t - s.th) / 0.35)
        if hp > 0:
            x = 32; sc = lerp(0.2, 1, eback(hp))
            pulse = 0.5 + 0.5 * math.sin((t - s.th) * 6)
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 6, y0 - 6, cw + 12, ch + 12), 30, 30)
            c.drawRRect(rr, P(YEL, 0.35 + 0.4 * pulse, 4))
            c.save(); c.translate(x + cw / 2, y0); c.rotate(-5); c.scale(sc, sc)
            f = font("xb", 30); w = tw("NAJSTARSZA", f, 3) + 50
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -30, w, 60), 30, 30), P(YEL))
            text(c, "NAJSTARSZA", 0, 11, f, P(INK), "c", track=3)
            c.restore()
        c.restore()

class Picks(El):
    """end: my two favourites"""
    z = 10
    def __init__(s, t_in, t_out, ta, tb):
        super().__init__(t_in, t_out, 0.2, 0.25); s.ta, s.tb = ta, tb
        for x in (ta, tb): sfx(x, "swoosh_s"); sfx(x + 0.25, "hit"); shake(x + 0.25, 10)
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        hp = prog(t, s.ta, 0.3, eout)
        text(c, "MOJE FAWORYTY", W / 2, 352, font("xb", 28), P(YEL, hp), "c", track=6)
        items = [("a4676376-image.jpg", (0, 0, 961, 1357), "VACHERON CONSTANTIN", "Overseas", 100, -3.5, s.ta),
                 ("708f5a33-image.webp", (0, 0, 768, 960), "HISTORIQUES", "American 1921", 570, 3.5, s.tb)]
        cw, ch, y0 = 410, 560, 400
        for name, crop, l1, l2, x, rot, t0 in items:
            pl = clamp((t - t0) / 0.38)
            if pl <= 0: continue
            sc = lerp(0.4, 1, eback(pl))
            c.save(); c.translate(x + cw / 2, y0 + ch / 2); c.rotate(rot * eout(pl)); c.scale(sc, sc); c.translate(-(x + cw / 2), -(y0 + ch / 2))
            c.saveLayerAlpha(None, int(clamp(pl * 4) * 255))
            r = skia.Rect.MakeXYWH(x, y0, cw, ch); rr = skia.RRect.MakeRectXY(r, 24, 24)
            sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.65), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
            c.save(); c.translate(0, 22); c.drawRRect(rr, sp); c.restore()
            c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
            k = 1 + 0.05 * clamp((t - t0) / 3)
            sx, sy, sw, sh_ = cover_src(crop, cw, ch); nsw, nsh = sw / k, sh_ / k
            c.drawImageRect(IMG(name), skia.Rect.MakeXYWH(sx + (sw - nsw) / 2, sy + (sh_ - nsh) / 2, nsw, nsh), r, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
            g = skia.GradientShader.MakeLinear([skia.Point(0, y0 + ch - 220), skia.Point(0, y0 + ch)], [col(INK, 0), col(INK, 0.94)])
            c.drawRect(r, skia.Paint(Shader=g))
            shine(c, r, prog(t, t0 + 0.4, 0.6, eio))
            text(c, l1, x + 28, y0 + ch - 86, font("xb", 21), P(YEL), track=3.5)
            text(c, l2, x + 26, y0 + ch - 32, font("serif", 50), P(CREAM))
            c.restore()
            c.drawRRect(rr, P(GOLD, 0.8, 2))
            c.restore(); c.restore()
        c.restore()

class Fan(El):
    z = 10
    def __init__(s, names, t_in, t_out, tdeal):
        super().__init__(t_in, t_out, 0.4, 0.25); s.names, s.td = names, tdeal
        for x in tdeal: sfx(x, "swoosh_s"); sfx(x + 0.3, "pop"); shake(x + 0.3, 5)
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, 0.01, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        slots = [(320, 640, -8), (760, 640, 8), (540, 610, 0)]
        for name, (cx, cy, rot), t0 in zip(s.names, slots, s.td):
            p = prog(t, t0, 0.5, eout)
            if p <= 0: continue
            w_, h_ = 440, 550
            c.save(); c.saveLayerAlpha(None, int(p * 255))
            pb = eback(clamp((t - t0) / 0.42)); c.translate(cx, cy + (1 - pb) * 260); c.rotate(rot * pb - (1 - pb) * 12)
            r = skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_); rr = skia.RRect.MakeRectXY(r, 22, 22)
            sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.6), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
            c.save(); c.translate(0, 20); c.drawRRect(rr, sp); c.restore()
            c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
            c.drawImageRect(IMG(name), skia.Rect.MakeXYWH(*cover_src((0, 0, 1280, 1600), w_, h_)), r, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
            c.restore(); c.drawRRect(rr, P(CREAM, 0.18, 1.5))
            c.restore(); c.restore()
        p = prog(t, s.td[-1] + 0.6, 0.35, eout)
        if p > 0:
            c.saveLayerAlpha(None, int(p * 255))
            text(c, "KTÓRY WYBIERASZ?", W / 2, 1010 + (1 - p) * 10, font("med", 26), P(GOLDL), "c", track=6)
            c.restore()
        c.restore()

class Duo(El):
    """two cards dealing in: portrait + text card"""
    z = 10
    def __init__(s, t_in, t_out, ta, tb):
        super().__init__(t_in, t_out, 0.35, 0.3); s.ta, s.tb = ta, tb; sfx(ta, "tick"); sfx(tb, "tick")
    def draw(s, c, t):
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        text(c, "1819 · NOWA SPÓŁKA", W / 2, 232 + (1 - pin) * 12, font("med", 25), P(GOLD), "c", track=5)
        cw, ch, y = 400, 540, 290
        for which, t0 in (("a", s.ta), ("b", s.tb)):
            p = prog(t, t0, 0.5, eout)
            if p <= 0: continue
            x = 110 if which == "a" else 570
            yy = y + (1 - p) * 50
            c.saveLayerAlpha(None, int(p * 255))
            r = skia.Rect.MakeXYWH(x, yy, cw, ch); rr = skia.RRect.MakeRectXY(r, 24, 24)
            sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.6), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
            c.save(); c.translate(0, 20); c.drawRRect(rr, sp); c.restore()
            c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
            if which == "a":
                c.drawImageRect(IMG("9163fee0-image.jpg"), skia.Rect.MakeXYWH(*cover_src((20, 650, 620, 1280), cw, ch)), r, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
                sh = skia.GradientShader.MakeLinear([skia.Point(0, yy + ch - 210), skia.Point(0, yy + ch)], [col(INK, 0), col(INK, 0.92)])
                c.drawRect(r, skia.Paint(Shader=sh))
                text(c, "PRZEDSIĘBIORCA", x + 30, yy + ch - 92, font("med", 21), P(GOLDL), track=4)
                text(c, "François Constantin", x + 28, yy + ch - 38, font("serif", 42), P(CREAM))
            else:
                c.drawRect(r, P(PANEL))
                text(c, "V", x + cw / 2, yy + 300, font("serif", 260), P(GOLD), "c")
                text(c, "WNUK ZAŁOŻYCIELA", x + 30, yy + ch - 92, font("med", 21), P(GOLDL), track=4)
                text(c, "J.-B. Vacheron", x + 28, yy + ch - 38, font("serif", 42), P(CREAM))
            c.restore()
            c.drawRRect(rr, P(GOLD if which == "b" else CREAM, 0.7 if which == "b" else 0.18, 1.5))
            c.restore()
        p = prog(t, s.tb, 0.5, eout)
        if p > 0:
            c.drawCircle(W / 2 + 0, y + ch / 2, 34, P(INK, p)); c.drawCircle(W / 2, y + ch / 2, 34, P(GOLD, p, 2))
            text(c, "&", W / 2, y + ch / 2 + 17, font("serif", 52), P(GOLDL, p), "c")
        c.restore()

class Comment(El):
    z = 30
    def __init__(s, t_in, t_out, typing):
        super().__init__(t_in, t_out, 0.35, 0.25); s.typing = typing
        for x in typing: sfx(x[0], "type")
    def draw(s, c, t):
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 420)], [col(INK, 0.55 * a), col(INK, 0)])
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 420), skia.Paint(Shader=sh))
        c.saveLayerAlpha(None, int(a * 255))
        y = 150 + (1 - pin) * 20
        r = skia.Rect.MakeXYWH(100, y, 880, 118); rr = skia.RRect.MakeRectXY(r, 59, 59)
        sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.45), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20))
        c.save(); c.translate(0, 10); c.drawRRect(rr, sp); c.restore()
        c.drawRRect(rr, P(PANEL, 0.94)); c.drawRRect(rr, P(GOLD, 0.55, 1.5))
        c.drawCircle(170, y + 59, 34, P(GOLD)); text(c, "Ty", 170, y + 69, font("semi", 28), P(INK), "c")
        full = "".join(x[2] for x in s.typing)
        typed = ""
        for t0, t1, seg in s.typing:
            if t >= t1: typed += seg
            elif t >= t0: typed += seg[:int(len(seg) * (t - t0) / (t1 - t0))]; break
        f = font("med", 40)
        if not typed:
            text(c, "Dodaj komentarz…", 230, y + 73, f, P(MUTED))
        else:
            wv = text(c, typed, 230, y + 73, f, P(CREAM))
            if len(typed) < len(full): c.drawLine(236 + wv, y + 38, 236 + wv, y + 84, P(GOLDL, 1, 3))
        # send icon
        ac = GOLDL if typed else MUTED
        path = skia.Path(); path.moveTo(912, y + 59); path.lineTo(880, y + 42); path.lineTo(886, y + 59); path.lineTo(880, y + 76); path.close()
        c.drawPath(path, P(ac))
        c.restore()

class CTA(El):
    z = 30
    def __init__(s, t_in, t_out, t_tap):
        super().__init__(t_in, t_out, 0.4, 0.2); s.tt = t_tap; sfx(t_tap, "hit"); sfx(t_tap, "click")
    def draw(s, c, t):
        a, pin = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        x, y, w, h = 150, 210 + (1 - pin) * 40, 780, 840
        r = skia.Rect.MakeXYWH(x, y, w, h); rr = skia.RRect.MakeRectXY(r, 30, 30)
        sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), 0.6), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
        c.save(); c.translate(0, 24); c.drawRRect(rr, sp); c.restore()
        c.drawRRect(rr, P(PANEL))
        c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
        ir = skia.Rect.MakeXYWH(x, y, w, 400)
        c.drawImageRect(IMG("9163fee0-image.jpg"), skia.Rect.MakeXYWH(*cover_src((660, 700, 1280, 1240), w, 400)), ir, SMP, None, skia.Canvas.kStrict_SrcRectConstraint)
        sh = skia.GradientShader.MakeLinear([skia.Point(0, y + 250), skia.Point(0, y + 400)], [col(PANEL, 0), col(PANEL, 1)])
        c.drawRect(ir, skia.Paint(Shader=sh))
        c.restore()
        c.drawRRect(rr, P(GOLD, 0.6, 1.5))
        text(c, "ZEGARKI · HISTORIA · MANUFAKTURY", W / 2, y + 470, font("med", 22), P(GOLD), "c", track=4.5)
        text(c, "@zegarkidawida", W / 2, y + 560, font("serif", 76), P(CREAM), "c")
        # button
        tp = t - s.tt
        sc = 1.0
        if 0 <= tp < 0.12: sc = 1 - 0.05 * eio(tp / 0.12)
        elif 0.12 <= tp < 0.32: sc = 0.95 + 0.05 * eio((tp - 0.12) / 0.2)
        done = tp >= 0.12
        bw, bh = 460, 104; bx, by = W / 2, y + 690
        c.save(); c.translate(bx, by); c.scale(sc, sc)
        br = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2, bw, bh), 52, 52)
        if not done:
            c.drawRRect(br, P(GOLD)); text(c, "Zaobserwuj", 0, 14, font("semi", 40), P(INK), "c")
        else:
            c.drawRRect(br, P(INK)); c.drawRRect(br, P(GOLD, 1, 2))
            text(c, "Obserwujesz", 14, 14, font("semi", 40), P(GOLDL), "c")
            ck = skia.Path(); ck.moveTo(-178, 0); ck.lineTo(-166, 12); ck.lineTo(-144, -12)
            c.drawPath(ck, P(GOLDL, 1, 4))
        c.restore()
        if 0 <= tp < 0.6:   # tap ripple
            q = eout(tp / 0.6)
            c.drawCircle(bx + 120, by + 10, 20 + 60 * q, P(CREAM, 0.45 * (1 - q), 3))
        c.restore()

class Title(El):
    """hook title, visible from frame 0"""
    z = 30
    def __init__(s, label, lines, y0, t_out, t_line, size=96, dark=False):
        super().__init__(-1, t_out, 0.01, 0.3); s.label, s.lines, s.y0, s.tl, s.size, s.dark = label, lines, y0, t_line, size, dark
        sfx(t_line, "tick")
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255))
        text(c, s.label, W / 2, s.y0, font("med", 26), P(GOLD if s.dark else GOLDL), "c", track=5)
        f = font("serif", s.size); y = s.y0 + s.size * 1.02
        for ln in s.lines:
            text(c, ln, W / 2, y, f, P(INK if s.dark else CREAM), "c"); y += s.size * 0.98
        p = prog(t, s.tl, 0.6, eio)
        if p > 0:
            yl = y - s.size * 0.98 + 30; half = 140 * p
            c.drawLine(W / 2 - half, yl, W / 2 + half, yl, P(GOLD, 1, 3))
        c.restore()

# =================== TIMELINE ===================
def build(hook="A"):
    global SFX, TRANS, SHAKE
    SFX = []; TRANS = []; SHAKE = []
    E = []
    # ---- footage mode keys (m: 0 full, 1 circle) ----
    Mk = [(O(9.10), O(9.10) + 0.4, 1, 0), (O(11.90), O(11.90) + 0.4, 0, 1),
          (O(30.50), O(30.50) + 0.4, 1, 0), (O(32.95), O(32.95) + 0.4, 0, 1),
          (O(56.22), O(56.22) + 0.4, 1, 0), (O(58.62), O(58.62) + 0.4, 0, 1)]
    for t0, t1, a, b in Mk: trans(t0)
    # hard zoom jumps on key words (full-frame segments only), reset after the morph out
    def Z(t, a, b): return (t, t + 0.001, a, b)
    Zk = [Z(O(9.84), 1.0, 1.05), Z(O(11.02), 1.05, 1.10), Z(O(11.90) + 0.45, 1.10, 1.0),
          Z(O(31.04), 1.0, 1.05), Z(O(31.86), 1.05, 1.10), Z(O(32.95) + 0.45, 1.10, 1.0),
          Z(O(56.98), 1.0, 1.05), Z(O(57.70), 1.05, 1.10), Z(O(58.62) + 0.45, 1.10, 1.0)]
    for z_ in (O(9.84), O(11.02), O(31.04), O(56.98), O(57.70)): sfx(z_, "swoosh_s")
    # ---- HOOK ----
    T_H = O(2.92)
    if hook == "A":
        E.append(Bleed("4b841112-image.jpg", (0, 0, 1280, 1600), -1, T_H, fin=0.01, kb=0.08))
        E.append(Title("VACHERON CONSTANTIN · OD 1755", ["Najstarsza marka", "zegarków na świecie"], 196, T_H - 0.25, O(1.30), size=94))
    elif hook == "B":
        E.append(Card("6f6bfa21-image.jpg", (0, 0, 1280, 1280), (230, 470, 620, 620), -1, T_H, fin=0.01, kb=0.08))
        E.append(Title("VACHERON CONSTANTIN · OD 1755", ["Starsza niż", "Stany Zjednoczone"], 196, T_H - 0.25, O(1.30), size=94))
    else:
        E.append(Card("bd6f2976-image.jpg", (0, 0, 1280, 1600), (306, 488, 468, 585), -1, T_H, fin=0.01, kb=0.08))
        E.append(Title("NAJSTARSZA MANUFAKTURA ŚWIATA", ["271 lat", "bez przerwy"], 196, T_H - 0.25, O(1.30), size=104))
    E.append(PillEl("GENÈVE · 1755", 580, 1150, O(0.75), T_H))
    # ---- 2: workshop card ----
    trans(O(2.85))
    t_out2 = O(4.30)
    E.append(Card("a1bcdbaf-image.jpg", (0, 560, 1280, 2160), (168, 150, 744, 930), O(2.85), t_out2))
    E.append(LowerThird("PIERWSZY WARSZTAT", "Genewa", O(3.55), t_out2))
    # ---- 3: archive 1755 bleed ----
    trans(O(4.30))
    t_out3 = O(6.00)
    E.append(Bleed("6ea7afd9-image.jpg", (0, 0, 1280, 1340), O(4.30), t_out3,
                   kids=[Outline((258, 302, 442, 343), O(4.62), 0.45)]))
    E.append(LowerThird("ARCHIWUM GENEWY", "17 września 1755", O(5.20), t_out3))
    # ---- 3b: Jean-Marc portrait ----
    trans(O(6.00))
    t_out3b = O(8.95)
    E.append(Card("9163fee0-image.jpg", (0, 0, 640, 640), (130, 190, 820, 820), O(5.98), t_out3b,
                  kids=[Pill("24 LATA", 160, 220, O(7.95))]))
    E.append(LowerThird("ZAŁOŻYCIEL", "Jean-Marc Vacheron", O(6.38), t_out3b, fout=0.2))
    shake(O(7.95) + 0.25, 6)
    # ---- 4: full frame "Najstarsza" ----
    E.append(BigWord("MARKA ZEGARKÓW", "Najstarsza", O(10.40), O(11.70)))
    # ---- 5: timeline ----
    ev = dict(lbl=O(12.38), line=O(12.70), end=O(13.72), big=O(13.95), t1789=O(15.98), t1914=O(17.12), t1939=O(17.52))
    for k_ in ("lbl", "end", "t1789", "t1914", "t1939"): sfx(ev[k_], "pop")
    for k_ in ("t1789", "t1914", "t1939"): shake(ev[k_] + 0.1, 6)
    sfx(ev["line"], "swoosh_s"); sfx(ev["big"] + 0.7, "hit"); shake(ev["big"] + 0.7, 12)
    E.append(Timeline(O(12.36), O(18.10), ev))
    # ---- 6: vintage watch card ----
    trans(O(18.10))
    E.append(Card("c75a7c85-image.jpg", (0, 0, 1280, 1600), (168, 150, 744, 930), O(18.12), O(20.15),
                  kids=[Pill("BEZ PRZERWY", 198, 182, O(18.75))]))
    # ---- 7: Chossat bleed ----
    trans(O(20.15))
    t7 = O(23.30)
    E.append(Bleed("e52abe31-image.jpg", (0, 0, 1280, 1280), O(20.15), t7,
                   kids=[Outline((668, 897, 932, 949), O(20.62), 0.45, radius=12)]))
    E.append(LowerThird("DAWNA NAZWA", "Vacheron Chossat", O(21.20), t7, strike=("Chossat", O(21.75))))
    shake(O(21.75) + 0.3, 7)
    # ---- 8: Constantin duo ----
    trans(O(23.30))
    E.append(Duo(O(23.30), O(27.10), O(23.62), O(26.05)))
    shake(O(23.62) + 0.4, 6); shake(O(26.05) + 0.4, 8); sfx(O(26.05) + 0.35, "hit")
    # ---- 9: building, name on the facade ----
    trans(O(27.10))
    E.append(Bleed("4b841112-image.jpg", (180, 500, 1280, 1600), O(27.10), O(30.36),
                   kids=[Outline((226, 1128, 336, 1218), O(27.55), 0.45, radius=8),
                         Outline(None, O(28.12), 0.5, quad=[(470, 1104), (1290, 1160)], w=4)]))
    sfx(O(28.62), "hit"); shake(O(28.62), 9)
    # ---- 10: full frame 1839 ----
    E.append(BigWord("KOLEJNY PRZEŁOM", "1839", O(31.05), O(32.72), count=True))
    # ---- 11: Leschot ----
    E.append(Card("9163fee0-image.jpg", (640, 0, 1280, 640), (130, 190, 820, 820), O(33.36), O(35.20)))
    E.append(LowerThird("INŻYNIER · 1839", "Georges-Auguste Leschot", O(33.80), O(35.20)))
    # ---- 12: pantograph ----
    trans(O(35.22))
    E.append(Pantograph(O(35.22), O(39.85), O(36.0), O(39.45)))
    sfx(O(39.45), "pop"); shake(O(39.45), 6)
    # ---- 13: production card ----
    trans(O(39.85))
    E.append(Card("a4c89abc-image.jpg", (0, 0, 1280, 1280), (130, 190, 820, 820), O(39.85), O(41.72),
                  kids=[Pill("REWOLUCJA", 160, 220, O(40.50))]))
    # ---- 14: map ----
    trans(O(41.72))
    E.append(Bleed("04cb4576-image.jpg", (0, 40, 1280, 1400), O(41.72), O(45.45), kb=0.09,
                   kids=[MapFX((258, 724), O(42.25), [((880, 300), O(42.85)), ((990, 760), O(43.30)), ((760, 1130), O(43.75))])]))
    # ---- 15: today ----
    trans(O(45.45))
    E.append(Card("f7e61e8c-image.jpg", (0, 0, 1280, 1600), (168, 150, 744, 930), O(45.45), O(47.52),
                  kids=[Pill("DZIŚ", 198, 182, O(45.85))]))
    E.append(LowerThird("PLAN-LES-OUATES · GENEWA", "Manufaktura dziś", O(46.05), O(47.52)))
    # ---- 16: big three ----
    trans(O(47.40))
    E.append(BigThree(O(47.52), O(53.45), [O(48.62), O(50.52), O(51.34)], O(52.15)))
    # ---- 17: fan ----
    trans(O(53.45))
    E.append(Fan(["7c3ff056-image.jpg", "78bddd74-image.jpg", "1c499380-image.jpg"], O(53.62), O(56.05),
                 [O(53.95), O(54.35), O(54.75)]))
    # ---- 18: comment + my picks ----
    E.append(Comment(O(56.68), O(61.10), [(O(58.55), O(58.95), "Overseas"), (O(59.55), O(60.10), " i Historiques American")]))
    E.append(Picks(O(58.80), O(61.10), O(58.84), O(59.74)))
    # ---- 19: CTA ----
    trans(O(61.15))
    E.append(CTA(O(61.25), NF / FPS + 1, O(62.42)))
    shake(O(62.42) + 0.05, 14)
    E.sort(key=lambda e: e.z)
    return E, Mk, Zk

class PillEl(El):
    z = 30
    def __init__(s, txt, x, y, t_in, t_out):
        super().__init__(t_in, t_out, 0.3, 0.2); s.p = Pill(txt, x, y, t_in)
    def draw(s, c, t):
        a, _ = win(t, s.t_in, s.t_out, s.fin, s.fout)
        if a <= 0: return
        c.saveLayerAlpha(None, int(a * 255)); s.p.draw(c, t); c.restore()

# =================== RENDER ===================
def render_frame(c, fi, E, Mk, Zk, cache=None):
    t = fi / FPS
    bgr = load_frame(SRC[fi])
    m = keys_val(Mk, t) if Mk else 1
    z = keys_val(Zk, t)
    if t < Mk[0][0]: m = 1
    c.clear(col(INK))
    # subtle warm lift in the middle of the ink background
    if m > 0:
        sh = skia.GradientShader.MakeRadial(skia.Point(540, 700), 900, [col((32, 27, 22)), col(INK)])
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    if m < 0.999: draw_footage(c, bgr, m, z)
    for e in E:
        if e.z < 20 and e.alive(t): e.draw(c, t)
    for e in E:
        if e.z == 20 and e.alive(t): e.draw(c, t)
    if m >= 0.999: draw_footage(c, bgr, m, z)
    for e in E:
        if e.z >= 30 and e.alive(t): e.draw(c, t)
    draw_caption(c, t)

def post(a, t):
    k = 1.0; blur = 0.0
    for T in TRANS:
        d = abs(t - T)
        if d < 0.16: v = (1 - d / 0.16) ** 2; k = max(k, 1 + 0.08 * v); blur = max(blur, v)
    dx = dy = 0.0
    for T, amp in SHAKE:
        d = t - T
        if 0 <= d < 0.32:
            e = (1 - d / 0.32) ** 2; dx += amp * e * math.sin(2 * math.pi * 24 * d); dy += amp * 0.7 * e * math.cos(2 * math.pi * 19 * d)
    if k == 1.0 and dx == 0 and dy == 0: return a
    sc = k + (abs(dx) + abs(dy)) / 450
    def warp(z_):
        M = np.float32([[z_, 0, (1 - z_) * W / 2 + dx], [0, z_, (1 - z_) * H / 2 + dy]])
        return cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if blur > 0.08:
        o = warp(sc).astype(np.float32) * 0.4 + warp(sc * (1 + 0.025 * blur)).astype(np.float32) * 0.3 + warp(sc * (1 + 0.05 * blur)).astype(np.float32) * 0.3
        return o.astype(np.uint8)
    return warp(sc)

def worker(args):
    hook, f0, f1, out = args
    E, Mk, Zk = build(hook)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        render_frame(c, fi, E, Mk, Zk)
        pr.stdin.write(np.ascontiguousarray(post(surf.makeImageSnapshot().toarray(), fi / FPS)).tobytes())
    pr.stdin.close(); pr.wait()
    return out

def still(hook, t, path):
    E, Mk, Zk = build(hook)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    render_frame(c, min(NF - 1, int(round(t * FPS))), E, Mk, Zk)
    a = post(surf.makeImageSnapshot().toarray(), min(NF - 1, int(round(t * FPS))) / FPS)
    cv2.imwrite(path, a[..., :3])

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "info":
        print("frames", NF, "dur", NF / FPS, "cuts", [round(x, 2) for x in CUTS])
        for t0, t1, s_, k in CAPS:
            w = CAPF.measureText(s_)
            if w > 820: print("WIDE", round(w), s_)
        build("A"); print(json.dumps(sorted(SFX)))
    elif mode == "still":
        hook = sys.argv[2]
        for t in sys.argv[3:]:
            still(hook, float(t), os.path.join(BASE, "stills", f"s_{hook}_{float(t):05.2f}.png"))
    elif mode == "render":
        from multiprocessing import Pool
        hook = sys.argv[2]; f0 = int(sys.argv[3]); f1 = int(sys.argv[4]); outp = sys.argv[5]; nw = 4
        os.makedirs(os.path.join(BASE, "parts"), exist_ok=True)
        step = math.ceil((f1 - f0) / nw)
        jobs = [(hook, f0 + i * step, min(f1, f0 + (i + 1) * step), os.path.join(BASE, "parts", f"{hook}_{i}.mp4")) for i in range(nw)]
        jobs = [j for j in jobs if j[1] < j[2]]
        with Pool(nw) as p: parts = p.map(worker, jobs)
        lst = os.path.join(BASE, "parts", f"{hook}.txt")
        open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", outp], check=True)
        print("done", outp)
