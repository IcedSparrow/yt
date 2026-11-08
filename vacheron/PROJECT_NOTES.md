# Vacheron Constantin: rolka 9:16, notatki projektu

## Pliki
| Plik | Co to jest |
|---|---|
| `VC_reel_v1_glos.mp4` | Gotowy film 1080×1920, 30 fps, 61,3 s, tylko głos (-14,8 LUFS) |
| `VC_reel_v2_glos_sfx.mp4` | Ten sam obraz plus subtelne efekty dźwiękowe (ok. 22 dB ciszej niż głos) |
| `hooks/hook_A_najstarsza_marka.mp4` | Hook użyty w filmie (pierwsze 4 s) |
| `hooks/hook_B_starsza_niz_USA.mp4` | Alternatywny hook, 4 s, wymiana 1:1 z pierwszymi 4 s filmu |
| `hooks/hook_C_271_lat.mp4` | Alternatywny hook, 4 s, wymiana 1:1 z pierwszymi 4 s filmu |
| `stills/` | Klatki kontrolne |
| `cut_and_cue.md` | Lista cięć, tabela napisów, lista efektów dźwiękowych |
| `src/render.py`, `src/audio.py` | Silnik montażu (Skia + ffmpeg) i obróbka audio, do ponownego renderu |

## Branding (zaproponowany, bo nie było podanego)
- Tło (ink) `#0E0C0A`, panele `#1B1815`, cienka ramka w kremie z 16% krycia
- Akcent główny: szampańskie złoto `#C9A46A` / jasne `#E0C492`. Drugi akcent: bordo `#963E38` (przekreślenie, wojny na osi czasu)
- Tekst `#F5EDE1` (krem), tekst wyciszony `#A89D8F`
- Duże słowa: Cormorant Garamond SemiBold. Napisy: Inter SemiBold 54 px. Małe etykiety: Inter Medium, wersaliki, rozstrzelone

## Układy (tylko 3, na zmianę)
- **L1 Pełny kadr**: ja w całym kadrze, duże słowo albo komentarz nad głową (głowa nigdy nie jest przycięta)
- **L2 Karta**: zaokrąglona karta ze zdjęciem u góry, ja w kółku (d = 260 px) w lewym dolnym rogu, podpis obok kółka
- **L3 Spad**: zdjęcie albo grafika na pełną szerokość, wtapia się w tło, kółko w tym samym miejscu
- Napisy zawsze na wysokości y = 1468 (nad dolnymi 20%), wyśrodkowane na x = 520 (z dala od prawej krawędzi)

## Cue sheet (czas w filmie)
| Czas | Układ | Na ekranie | Animacja |
|---|---|---|---|
| 0,0–2,9 | L3 HOOK | Kamienica Vacheron & Constantin + tytuł „Najstarsza marka zegarków na świecie” | Tytuł czytelny od 1. klatki, złota linia rysuje się pod tytułem |
| 2,9–4,3 | L2 | Narzędzia i grawerowany mechanizm („warsztat”) | Karta wjeżdża, podpis „Pierwszy warsztat · Genewa” |
| 4,2–5,9 | L3 | Archiwum Genewy 1755 + pierwszy zegarek | Złota ramka rysuje się wokół „1755”, podpis „17 września 1755” |
| 5,9–8,9 | L2 | Portret Jean-Marca Vacherona | Podpis „Założyciel”, plakietka „24 LATA” |
| 8,9–11,8 | L1 | Ja + „Najstarsza” | Morph kółko → pełny kadr, słowo nad głową, punch-in na „najstarszego” |
| 11,8–17,7 | L3 | Oś czasu 1755 → 2026, „271 lat” | Linia rysuje się na „nieprzerwanie”, potem po kolei: 1789, 1914–1918, 1939–1945 |
| 17,7–19,8 | L2 | Zegarek Vacheron & Constantin z lat 40. | Przenikanie karty |
| 19,8–22,6 | L3 | Kieszonkowy „Vacheron Chossat & Comp.” | Ramka wokół sygnatury na tarczy, przekreślenie „Chossat” |
| 22,6–26,4 | L2 | François Constantin & J.-B. Vacheron | Karty wchodzą po kolei, złote „&” |
| 26,4–29,7 | L3 | Szyld na fasadzie | Ramka wokół szyldu narożnego, podkreślenie „VACHERON & CONSTANTIN” |
| 29,7–32,2 | L1 | Ja + „1839” | Morph, duże „1839” nad głową |
| 32,2–34,4 | L2 | Portret Leschota | Podpis „Inżynier · 1839” |
| 34,4–39,0 | L3 | Pantograf (grafika) | Mechanizm przerysowuje koło zębate ze wzoru na kopię |
| 39,0–40,9 | L2 | Montaż mechanizmu | Przenikanie |
| 40,9–44,7 | L3 | Emaliowana mapa | Puls na Genewie, 3 łuki „na podbój rynków” |
| 44,7–46,6 | L2 | Manufaktura w Plan-les-Ouates | Podpis „Dziś” |
| 46,6–52,5 | L3 | „Wielka Trójka” | Karty I/II/III wchodzą na nazwy |
| 52,5–55,0 | L2 | Wachlarz 3 modeli | Karty rozdawane jedna po drugiej, „Który wybierasz?” |
| 55,0–59,5 | L1 | Ja + pole komentarza | Wpisuje się „Overseas i Historiques American”, punch-in na cięciu |
| 59,5–61,3 | CTA | Karta @zegarkidawida | Przycisk „Zaobserwuj” zostaje kliknięty na „więcej” i zmienia się w „Obserwujesz ✓” |

Pełna tabela napisów i lista cięć: `cut_and_cue.md`.

## Ustawienia
- Surowe nagranie: 420×746 (skompresowane). Odszumienie hqdn3d 1.5, skalowanie lanczos do 1080×1920, unsharp 0.45, kontrast 1.05, nasycenie 1.03. Bez ziarna, bez poświaty, bez tintu.
- Wideo: x264 CRF 16, yuv420p, BT.709. Audio: AAC 256k, 48 kHz.
- Głos: highpass 75 Hz, lekkie afftdn, kompresor 2.5:1, dwuprzebiegowy loudnorm do -14 (wyszło -14,8 LUFS, TP -1,5). Każde cięcie ma fade 10 ms.

## Przeglądy
- **Przegląd 1 (klatki):** ramka „1755” była przesunięta w lewo; podpis w archiwum leżał na jasnym tle (słaba czytelność); ramię pantografu wchodziło na tytuł; oś czasu była zbyt mała i miała pustą połowę; ptaszek „Obserwujesz” nachodził na tekst. Wszystko poprawione.
- **Przegląd 2 (przejścia i audio):** sprawdzone morphy i każde cięcie audio (brak trzasków, maks. skok na cięciu ok. 5% skali); przejście jasnych zdjęć w ciemne tło wydłużone z 300 do 400 px; w hooku C karta dotykała tytułu, przesunięta niżej.

## Status
Runda 1 wyrenderowana, czeka na uwagi.
