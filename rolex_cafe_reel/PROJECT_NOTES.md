# Rolex Cafe — reel (Zegarkidawida)

## Pliki
| Plik | Co to |
|---|---|
| `Rolex_Cafe_reel_v1.mp4` | Wersja główna: 1080x1920, 30 fps, 55,3 s, H.264 CRF 14, głos −14,1 LUFS, szczyt −1,5 dBFS |
| `Rolex_Cafe_reel_v2_SFX.mp4` | Ten sam obraz + ciche efekty (swoosh / tick / klik / niski hit na „obserwuj”), −14,4 LUFS |
| `hooks/hook_B_twoja_okladka.mp4` | Alternatywny hook (4 s): Twoja okładka „KAWA OD ROLEXA?!” + Ty w kółku |
| `hooks/hook_C_ty_pelny_kadr.mp4` | Alternatywny hook (4 s): Ty na pełnym kadrze + „ROLEX CAFE?” nad głową |
| `src/` | Silnik renderu (Python + Skia), lista cięć, beaty, napisy, transkrypcja, detekcja twarzy |

Hooki mają ten sam dźwięk co pierwsze 4 s wersji głównej i podmieniają się 1:1.

## Branding (zaproponowany — pola były puste)
- Tło: gradient #1A130F → #070504 (espresso), delikatne złote światło z lewej góry (10%)
- Panel: #1E1612, obramowanie złote 30–35% / 2 px, rogi 28–34 px
- Akcent główny: #D9B36C (złoto), drugi: #4FB58A (zieleń Rolexa — klasa 43, „pierwszy zegarek”)
- Tekst: #F6F1EA, wyciszony: #A99B8C
- Fonty: Inter Display Bold (duże słowa), Inter SemiBold (napisy), JetBrains Mono (etykiety) — ten sam system co film Deepsea, dla spójności kanału

## Ustawienia
- Surówka: 436x778, normalny pokój → **bez wycinania**: zawsze prawdziwy kadr kamery.
- Kadry: FULL (cały kadr x2,48) i OKNO (cały kadr x1,6 w zaokrąglonej ramce, y 660–1420, pod grafiką u góry). Pozycje głowy i ust mierzone detekcją twarzy w każdej klatce. Duże słowa skalowane do najwyższego punktu włosów w danym beacie, więc nigdy nie wchodzą na głowę.
- Grade: +6% kontrastu, +3% nasycenia, bez zmiany balansu bieli. Krawędzie (góra/dół kadru FULL) przyciemnione gładkim gradientem, tylko pod tekst.
- Napisy: Inter SemiBold 60 px, biały, słowo-klucz złote, linia bazowa y=1500 (nad dolnymi 20%), środek x=500, mocny cień dla czytelności na bluzie.
- Cięcia: cisza < −36 dB dłuższa niż 0,22 s skracana do ~0,15 s, 10 ms fade na każdym cięciu (pauzy w surówce były już krótkie: 57,3 s → 55,3 s).
- Audio: highpass 70 Hz + loudnorm 2-pass; wersja SFX miksowana bezpośrednio (gotowy głos + efekty), sprawdzona co 2 s: głos nigdzie nie różni się o więcej niż 2 dB od czystego głosu.

## Status
- Runda 1: pełny render v1 + v2 SFX + 2 alternatywne hooki.
- **Runda 2 (Twoja prośba: więcej animacji, bardziej dynamicznie)** — podmienione wszystkie 4 pliki. Poprzednia wersja silnika: brak (zastąpiona w \`src/\`).

## Runda 2 — co doszło
1. Napisy karaoke: każde słowo rozjaśnia się (42% → 100%) w momencie wypowiedzenia; styl i pozycja bez zmian.
2. Złote podkreślenie rysuje się od środka pod każdym dużym słowem, po tym jak słowo się pojawi.
3. Wniosek o znak: karta pojawia się już na „złożył w USA wniosek”, pieczątka „ZŁOŻONO · USPTO” rysuje się na słowie „wniosek”, potem pisze się „ROLEX CAFE”, potem zielony obrys „usługi kawiarniane”.
4. Nowa karta-mapa (zamiast dużego słowa „F.P. JOURNE”): rysuje się Jezioro Genewskie, pinezka opada na Genewę (bez odbicia) z falą, potem „GENEWA”, a na „F.P. Journe” pisze się nazwa.
5. Para nad cappuccino z koroną — trzy cienkie linie unoszące się nad filiżanką.
6. Powolny najazd (Ken Burns, +4,5–5% w 3,5 s) na wszystkie zdjęcia i karty ze zdjęciami.
7. Ikona zegarka rysuje się przy „PIERWSZY ZEGAREK”.
8. Lista oczekujących: pod licznikiem pasek postępu, który prawie stoi, i „SZACOWANY CZAS OCZEKIWANIA: ???”.
9. Karty wjeżdżają mocniej (48 px zamiast 26 px, 0,34 s, ease in-out).
10. Karty marek: złote puste ramki widoczne od początku beatu, wypełniają się na nazwę marki.
11. Punch-in dodany też na „Zostaje jedno pytanie” (razem 3: „nie przypadek”, „genialny”, „jedno pytanie”, + „jak w salonie”).
12. SFX (wersja v2): dodany klik pieczątki i pinezki.

Świadome odstępstwo: powolny najazd na zdjęcia trwa w tle, gdy rysuje się pierścień/etykieta — to bardzo wolny ruch tła, a nie drugi efekt; jeśli chcesz ściśle „jedna rzecz naraz”, mogę go wyłączyć jedną linijką.

Przegląd rundy 2: pieczątka nachodziła na „ROLEX CAFE”, a potem na „30 września” → mniejsza, przesunięta obok „Rolex SA”; jezioro wyglądało jak uśmiech → pełniejszy, wypełniony kształt; puste ramki kart marek były niewidoczne → złote, 22% krycia. Miks v2 sprawdzony co 2 s: głos nigdzie nie różni się o więcej niż 2 dB od czystego głosu.

## Wybory podjęte bez pytania
1. Od razu pełny render (bez czekania na OK tabeli beatów i stillsów), bo prosiłeś „wykonaj mi to”.
2. Branding espresso + złoto + zieleń Rolexa.
3. **Napisy wg tego, co faktycznie mówisz**, nie wg skryptu. Różnice, które warto sprawdzić:
   - mówisz „To nie przypadek, **tylko** zabezpieczenie na zapas” (skrypt: „ani zabezpieczenie”) — zmienia sens zdania; jeśli to przejęzyczenie, warto dograć,
   - „Nie każdego stać na Rolexa za **100 tysięcy złotych**” (skrypt: 15 000 dolarów),
   - „ma **również** zegarmistrz”, „To może **wydarzyć się** naprawdę”, dodane „Tak jak w salonie Rolexa”,
   - CTA: „Co sądzisz o takiej kawiarni? Czy do niej byś poszedł? Napisz w komentarzu i obserwuj po więcej.”
4. Zdjęcie Domino's / „Rolex za pizzę” pominięte — inny temat i cudza marka.
5. Twoja okładka AI (Rolex Cafe) użyta tylko jako wycinek szyldu z podpisem „WIZUALIZACJA · KONCEPT, NIE ZDJĘCIE KAWIARNI” oraz w hooku B — bez tego widz mógłby uznać, że kawiarnia już istnieje.
6. Etykiety dodane w grafikach: „USPTO”, „Rolex SA”, „Klasa 43 — usługi kawiarniane” (klasa nicejska dla usług gastronomicznych), „KAWA za kilkanaście złotych”, licznik #1 248 (żart, nie dane), przykładowy komentarz „Tak, byle bez listy oczekujących”. Szczegóły wniosku warto zweryfikować przed publikacją.
7. Bez muzyki (nie podałeś; brak licencjonowanej biblioteki).
8. Zdjęcia w niskiej rozdzielczości (latte 640 px, ziarna 554 px) tylko jako mniejsze karty, nie na pełny ekran.

## Cue sheet
| Wyjście | Układ | Na ekranie | Animacja | Napisy |
|---|---|---|---|---|
| 0:00.00–0:03.02 | Zdjęcie na pełny ekran + Ty w kółku | Submariner + espresso, „Kawa od Rolexa?” | statyczny pierwszy kadr, czytelny bez dźwięku | Kawa od Rolexa? / To może wydarzyć się / naprawdę. |
| 0:03.02–0:05.82 | Ty na pełnym kadrze + duże słowo nad głową | „30 WRZEŚNIA” / ROLEX · USA | fade + lekki wjazd | 30 września Rolex / złożył w USA wniosek |
| 0:05.82–0:10.63 | Grafika u góry + Ty w oknie | karta wniosku USPTO: znak / zgłaszający / data / klasa 43 | „ROLEX CAFE” pisze się samo, zielony obrys wokół „usługi kawiarniane” | o rejestrację / znaku towarowego / „Rolex Cafe”, / i to konkretnie / dla usług kawiarnianych. |
| 0:10.63–0:13.55 | Ty na pełnym kadrze + duże słowo nad głową | „NIE PRZYPADEK” / ROLEX CAFE | fade + lekki wjazd, punch-in 6% | To nie przypadek, / tylko zabezpieczenie na zapas. |
| 0:13.55–0:17.12 | Pływająca karta u góry + Ty w oknie | Day-Date / Datejust w ziarnach kawy | karta wjeżdża, etykieta pisze się sama | Ale po co / luksusowej marce zegarków / sprzedawać kawę? |
| 0:17.12–0:23.32 | Grafika u góry + Ty w oknie | „Inne marki już to robią” + 3 karty | karty wypełniają się na nazwę marki | Inne luksusowe marki / już to robią: / Saint Laurent, / Louis Vuitton, / a nawet Prada / mają swoje kawiarnie / i restauracje. |
| 0:23.32–0:26.97 | Ty na pełnym kadrze + duże słowo nad głową | „F.P. JOURNE” / ZEGARMISTRZ · RESTAURACJA W GENEWIE | fade + lekki wjazd | Własną restaurację / w Genewie ma również / zegarmistrz F.P. Journe. |
| 0:26.97–0:29.35 | Ty na pełnym kadrze + duże słowo nad głową | „GENIALNY RUCH” / MARKETING | fade + lekki wjazd, punch-in 6% | I to genialny / ruch marketingowy. |
| 0:29.35–0:32.25 | Zdjęcie na pełny ekran + Ty w kółku | Rolex Submariner na rysunku patentowym | złoty pierścień rysuje się wokół Rolexa, pill „≈ 100 000 zł” | Nie każdego stać / na Rolexa / za 100 tysięcy złotych, |
| 0:32.25–0:34.52 | Pływająca karta u góry + Ty w oknie | cappuccino z koroną | karta wjeżdża, etykieta pisze się sama | ale na filiżankę kawy / stać prawie każdego. |
| 0:34.52–0:36.12 | Pływająca karta u góry + Ty w oknie | szyld „ROLEX CAFE” (wizualizacja) | karta wjeżdża, obrys wokół korony | Siadasz w miejscu / z koroną na szyldzie, |
| 0:36.12–0:38.77 | Ty na pełnym kadrze + duże słowo nad głową | „CZĘŚĆ ŚWIATA” / ESPRESSO Z KORONĄ | fade + lekki wjazd | pijesz espresso / i przez chwilę / czujesz się częścią / tego świata. |
| 0:38.77–0:43.52 | Grafika u góry + Ty w oknie | KAWA → LOJALNOŚĆ → PIERWSZY ZEGAREK | linia rysuje się od węzła do węzła | Właśnie tak buduje się / lojalność wobec marki, / zanim klient kupi / pierwszy zegarek. |
| 0:43.52–0:44.75 | Ty na pełnym kadrze + duże słowo nad głową | „JEDNO PYTANIE” | fade + lekki wjazd | Zostaje jedno pytanie. |
| 0:44.75–0:48.16 | Grafika u góry + Ty w oknie | karta rezerwacji, pozycja na liście | licznik #1 → #1 248 | Czy na stolik też / trzeba będzie czekać / na liście oczekujących? / Tak jak w salonie |
| 0:48.16–0:49.79 | Ty na pełnym kadrze + duże słowo nad głową | „JAK W SALONIE” / ROLEX | fade + lekki wjazd, punch-in 6% | Rolexa. |
| 0:49.79–0:51.94 | Grafika u góry + Ty w oknie | „Poszedłbyś?” + pole komentarza | pole pisze „Tak, byle bez listy oczekujących” | Co sądzisz / o takiej kawiarni? / Czy do niej byś poszedł? |
| 0:51.94–0:55.28 | Ty na pełnym kadrze + duże słowo nad głową | karta @zegarkidawida + „Obserwuj” | tap → „Obserwujesz”, niski hit w wersji SFX | Napisz w komentarzu / i obserwuj / po więcej. |

## Lista cięć (surowy materiał → wideo)
| # | Surowy IN | Surowy OUT | Wideo IN | Wideo OUT | Słowa |
|---|---|---|---|---|---|
| 1 | 0.00 | 2.11 | 0.00 | 2.11 | Kawa od Rolexa to może wydarzyć się. |
| 2 | 2.19 | 8.07 | 2.11 | 7.99 | Naprawdę. 30 września Rolex złożył w USA wniosek o rejestrację znaku towarowego Rolex Kofi |
| 3 | 8.14 | 10.78 | 7.99 | 10.63 | i to konkretne dla usług kawiarnianych. |
| 4 | 10.93 | 11.76 | 10.63 | 11.46 | To nie przypadek, |
| 5 | 11.87 | 13.01 | 11.46 | 12.60 | zabezpieczenie na |
| 6 | 13.10 | 14.05 | 12.60 | 13.55 | zapas. |
| 7 | 14.33 | 17.90 | 13.55 | 17.12 | Ale po co luxuriousowej marce Zegarków sprzedawać kawy? |
| 8 | 18.00 | 29.07 | 17.12 | 28.19 | Inne luxuriousowe marki już to robią Saint Laurent, Louis Vuitton, a nawet Prada mają swoje kawiarnie i restauracje. własną restaurację w Genewa ma również zegarmiść, F .P. Journe i to genialny ruch marketingowy. |
| 9 | 29.14 | 33.02 | 28.19 | 32.07 | Każdego jest stać na Rolexa za 100 tysięcy złotych, |
| 10 | 33.10 | 35.55 | 32.07 | 34.52 | ale na friżankę kawy stać prawie każdego. |
| 11 | 35.70 | 43.78 | 34.52 | 42.60 | Siadać w miejscu z koronką na shieldzie, pijesz espresso i przez chwilę czuje się cięższą tego. Świata właśnie tak buduje zlojalność wobec marki, zanim klient kupi pierwszy zegarek. |
| 12 | 43.93 | 44.85 | 42.60 | 43.52 |  |
| 13 | 45.07 | 49.71 | 43.52 | 48.16 | Zostaje jedno pytanie. Czy na stolik też trzeba będzie czekać na liście ociekujących? Tak |
| 14 | 49.84 | 50.76 | 48.16 | 49.08 | jak w salonie Rolexa. |
| 15 | 50.84 | 54.84 | 49.08 | 53.08 | Co sądzić o takie kawiarni czy do niebyś poszedł? Napisz w komentarzu |
| 16 | 54.91 | 56.01 | 53.08 | 54.18 | i obserwuj, |
| 17 | 56.14 | 57.24 | 54.18 | 55.28 | powięcej. |

## Co poprawiłem w przeglądach
**Pass 1 (stillsy):** szyld Rolex Cafe miał podpis „WIZUALIZACJA” na napisie → przeniesiony pod kartę; pill z ceną zasłaniał zegarek Tudor → przesunięty na rysunek; złoty pierścień wokół Rolexa za cienki → grubszy; okno z Tobą stykało się z napisami → kończy się 20 px wyżej.
**Pass 2 (cały film co 0,5 s):** złote słowa-klucze w napisach ginęły na brązowej bluzie → mocniejszy cień i ciemniejszy dół kadru; pusta góra przez ~1,3 s przed kartami marek → nagłówek „Inne marki już to robią” + puste ramki kart od początku; „CZĘŚCIĄ TEGO ŚWIATA” było za małe (mało miejsca nad głową) → „CZĘŚĆ ŚWIATA” w jednej linii; widoczne „schodki” na krawędziach gradientów → gładkie wielostopniowe gradienty; hook B nie miał Twojego ujęcia → dodane kółko z Tobą (zasłania też twarz AI z okładki).

## Ograniczenia
- Surówka ma 436x778 px („compressed”), więc twarz w 1080x1920 jest miękka. Oryginał w 1080p/4K da wyraźnie ostrzejszy obraz bez zmian w montażu.
- Brak referencji strukturalnej/efektów, więc nie zestawiłem klatek obok wzorca.
