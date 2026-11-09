# Rolex Deepsea Challenge — reel (Zegarkidawida)

## Pliki
| Plik | Co to |
|---|---|
| `Deepsea_Challenge_reel_v1.mp4` | Wersja główna: 1080x1920, 30 fps, 83,4 s, H.264 CRF 14, głos AAC 256k, −14 LUFS |
| `Deepsea_Challenge_reel_v2_SFX.mp4` | Ten sam obraz + subtelne efekty dźwiękowe (swoosh / tick / klik / niski hit na „obserwuj”) |
| `hooks/hook_B_licznik_glebokosci.mp4` | Alternatywny hook (4,8 s): Ty na pełnym kadrze + licznik „−10 935 m” |
| `hooks/hook_C_split_przezyje_dno.mp4` | Alternatywny hook (4,8 s): split – zegarek w snopie światła + „Przeżyje dno oceanu.” |
| `src/` | Silnik renderu (Python + Skia), lista cięć, beaty, napisy, transkrypcja |

Hooki B i C mają dokładnie tę samą długość i audio co pierwsze 4,83 s wersji głównej – można je podmienić 1:1 w montażu.

## Branding (zaproponowany – nie dostałem Twojego)
- Tło: gradient #0B1A29 → #03070C (głębia oceanu), delikatne światło od góry-lewej (10% krycia, tylko krawędzie)
- Panel: #0D1A26, obramowanie: biały 12–16% / 1–2 px, rogi 28–40 px
- Akcent główny: #7FE3F0 (lodowy błękit – kolor lume Chromalight z Twoich zdjęć)
- Akcent drugi: #D9BC84 (szampański – tylko „WRÓCIŁ” i przekreślenie „STAL”)
- Tekst: #F3F6F8, wyciszony: #8FA3B3
- Fonty: Inter Display Bold (duże słowa), Inter SemiBold (napisy), JetBrains Mono Medium (etykiety)

## Ustawienia
- Surowy materiał: 352x626 (plik „compressed”), już wycięty na białym tle → klucz białego tła, dekontaminacja krawędzi, miękkie wygaszenie boków i dołu wycinka, upscale Lanczos + delikatny unsharp. Brak ziarna, glow, tintu. Skóra: +4% kontrastu, +5% nasycenia, bez zmiany balansu.
- Kadr: 2 stałe ustawienia – FULL (szczyt włosów y=380, górna 1/5) i LOW (szczyt włosów y=846 pod panelem 800 px). Rozmiar głowy znormalizowany między 8 fragmentami surówki, szczyt liczony z najwyższego punktu głowy w każdym fragmencie.
- Napisy: Inter SemiBold 60 px, biały, słowo-klucz #7FE3F0, linia bazowa y=1492 (nad dolnymi 20%), środek x=500 (odsunięte od prawej krawędzi), 2–4 słowa.
- Cięcia: cisza < −38 dB dłuższa niż 0,22 s skracana do ~0,15 s; 10 ms fade na każdym cięciu; koniec 0,35 s po ostatnim słowie.
- Audio: highpass 70 Hz, loudnorm 2-pass → −14,2 LUFS, TP −1,5 dB.

## Status
- Runda 1: pełny render v1 + v2 SFX + 2 alternatywne hooki – czeka na Twoją akceptację.

## Wybory podjęte bez pytania
1. Przeszedłem od razu do pełnego renderu (bez czekania na akceptację tabeli beatów i stillsów), bo w wiadomości prosiłeś „wykonaj mi to”. Tabela beatów jest niżej jako cue sheet.
2. Branding (kolory/fonty) – zaproponowałem własny „deep sea”, bo pola były puste.
3. Tło za Tobą: ciemny gradient oceanu. Twoje nagranie było już wycięte na białym tle, więc tylko podmieniłem biel – nic nie wycinałem z normalnego pokoju.
4. Napisy wg tego, co faktycznie mówisz, nie wg skryptu: „lżej niż niejeden **telefon**” (nie „smartfon”), CTA: „Co sądzisz o tym zegarku? Napisz w komentarzu i obserwuj po więcej!”. Tam, gdzie transkrypcja była niepewna, przyjąłem brzmienie ze skryptu („Dno Rowu Mariańskiego”, „którego doświadczasz”, „prawdopodobnie nigdy nie dotrzesz”).
5. Liczby dodane w grafikach: dno Rowu 10 935 m, ciśnienie ≈1 086 bar, nurkowanie Camerona 10 908 m (2012), rekreacyjne 40 m, typowy zegarek nurkowy 300 m, rekord nurkowania 332 m, produkcja 2022. Proszę o szybką weryfikację, jeśli chcesz mieć 100% pewności.
6. Bez muzyki (nie podałeś; nie mam licencjonowanej biblioteki). Wersja v2 ma tylko SFX syntetyzowane w kodzie.
7. Zdjęcie z ramką „CH24.PL” – kadrowane tak, że znak wodny jest poza kadrem. Nie użyłem zdjęcia starszego Deepsea 3900 m (inny model – mylący) ani małego duplikatu hero.
8. Animacje rysowane w edycji (linie, karty, liczniki) – nie generowałem żadnych obrazów.
9. Hook główny: zdjęcie hero na pełnym ekranie + Ty w kółku + nagłówek „Wrzuć go na dno oceanu.” widoczny od pierwszej klatki.

## Cue sheet
| Wyjście | Układ | Na ekranie | Animacja | Napisy |
|---|---|---|---|---|
| 0:00.00–0:02.88 | Zdjęcie na pełny ekran + Ty w kółku | Hero zegarka pod wodą, „Wrzuć go na dno oceanu.” | statyczny pierwszy kadr (czytelny bez dźwięku), kółko wjeżdża po 0,3 s | To zegarek, / który mógłbyś wrzucić / w najgłębsze miejsce / na Ziemi, |
| 0:02.88–0:04.84 | Ty na pełnym kadrze + duże słowo nad głową | „NADAL DZIAŁA” + etykieta „PO WYCIĄGNIĘCIU Z DNA” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | a po wyciągnięciu / nadal by działał. |
| 0:04.84–0:07.04 | Pływająca karta (góra) + Ty pod spodem |  | karta wjeżdża, etykieta pisze się sama | To Rolex / Deepsea Challenge. |
| 0:07.04–0:11.11 | Grafika (góra) + Ty | skala głębokości 0–11 km | znacznik schodzi, licznik 0 → 10 935 m | Dno Rowu Mariańskiego / znajduje się na głębokości / niespełna 11 tysięcy metrów. |
| 0:11.11–0:15.18 | Ty na pełnym kadrze + duże słowo nad głową | „×1000” + etykieta „CIŚNIENIE NA DNIE” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | Panuje tam ciśnienie / ponad tysiąc razy większe / niż to, którego / doświadczasz w tej chwili — |
| 0:15.18–0:19.44 | Grafika (góra) + Ty | puszka (linie) + „≈1 086 bar” | puszka rysuje się, na „puszkę” zostaje zgnieciona, strzałki ciśnienia | zmiótłby pod nim / kadłub łodzi podwodnej / niczym aluminiową puszkę. |
| 0:19.44–0:22.52 | Split: zdjęcie tarczy / Ty | zbliżenie tarczy | obrys rysuje się wokół „36090ft = 11000m”, pill „ZAPROJEKTOWANY NA 11 000 m” | Ten zegarek jest przystosowany / do dokładnie takiej głębokości. |
| 0:22.52–0:26.12 | Ty na pełnym kadrze + duże słowo nad głową | „0 miejsc” + etykieta „POZA JEGO ZASIĘGIEM” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | Oznacza to, że / nie ma na tej / planecie miejsca, / do którego mógłbyś / go zabrać |
| 0:26.12–0:28.82 | Grafika (góra) + Ty | skala 10 800–11 080 m | linia „najgłębszy punkt 10 935 m”, potem linia „limit zegarka 11 000 m” | i osiągnąć jego / granicę wytrzymałości. |
| 0:28.82–0:32.39 | Ty na pełnym kadrze + duże słowo nad głową | „2012” + etykieta „SPRAWDZONE W PRAKTYCE” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | Sam pomysł / został już wcześniej sprawdzony. / W 2012 roku |
| 0:32.39–0:37.45 | Split: zdjęcie Camerona / Ty | łódź Deepsea Challenger | zoom na zegarek na ramieniu robota + obrys, powrót, pill „JAMES CAMERON” | eksperymentalną wersję zegarka / przymocowano do ramienia / robota łodzi podwodnej / Jamesa Camerona. |
| 0:37.45–0:40.80 | Grafika (góra) + Ty | tor zanurzenia 2012 | kropka schodzi do 10 908 m z licznikiem i wraca – „WRÓCIŁ” | Zegarek dotarł / na samo dno / Rowu Mariańskiego / i wrócił stamtąd, |
| 0:40.80–0:42.54 | Ty na pełnym kadrze + duże słowo nad głową | „NADAL DZIAŁA” + etykieta „PO POWROCIE Z DNA” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | nadal działając. |
| 0:42.54–0:44.88 | Ty na pełnym kadrze + duże słowo nad głową | „STALOWY POTWÓR” + etykieta „PROTOTYP · 2012” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | Tamten model był / prawdziwym stalowym potworem. |
| 0:44.88–0:47.45 | Pływająca karta (góra) + Ty pod spodem |  | karta wjeżdża, etykieta pisze się sama | Ten jest jego / produkcyjną wersją — / z kopertą i bransoletą |
| 0:47.45–0:51.35 | Grafika (góra) + Ty | karty STAL vs TYTAN RLX | druga karta wjeżdża, przekreślenie „STAL” | wykonaną z autorskiego / tytanu RLX / firmy Rolex. |
| 0:51.35–0:55.28 | Ty na pełnym kadrze + duże słowo nad głową | „PIERWSZY RAZ” + etykieta „TYTAN RLX · DEBIUT” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | To pierwszy raz, / kiedy marka zastosowała / ten materiał / w takim zegarku. |
| 0:55.28–0:59.34 | Grafika (góra) + Ty | paski masy | pasek kurczy się o 30%, „−30%” | Dzięki temu jest / o 30 procent lżejszy / od modelu eksperymentalnego, |
| 0:59.34–1:02.15 | Split: zdjęcie frontu / Ty | front zegarka | linia wymiaru rysuje się od środka, pill „⌀ 50 mm” | a mimo koperty / o średnicy aż / 50 milimetrów |
| 1:02.15–1:04.89 | Split: zbliżenie / Ty | tarcza i szkło | elipsa rysuje się wokół szkła, pill „SZKŁO SZAFIROWE · 9,5 mm” | i szafirowego szkła / grubości 9,5 milimetra, |
| 1:04.89–1:07.94 | Ty na pełnym kadrze + duże słowo nad głową | „≈250 g” + etykieta „CAŁY ZEGAREK” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | cały zegarek waży / zaledwie około / 250 gramów. |
| 1:07.94–1:10.38 | Grafika (góra) + Ty | kontur telefonu vs „≈250 g” | telefon rysuje się, potem waga | Lżej niż niejeden / telefon! |
| 1:10.38–1:13.24 | Grafika (góra) + Ty | 40 m / 300 m / 332 m | karty wjeżdżają po kolei | Każdy inny zegarek nurkowy / jest przystosowany / do głębokości, |
| 1:13.24–1:15.08 | Ty na pełnym kadrze + duże słowo nad głową | „NIGDY” + etykieta „TAM NIE DOTRZESZ” | słowo: fade + 18 px w górę; punch-in 6,5% na słowie-kluczu | do których prawdopodobnie / nigdy nie dotrzesz. |
| 1:15.08–1:18.58 | Zdjęcie na pełny ekran + Ty w kółku | zegarek w snopie światła | „11 000 m · GŁĘBOKOŚCI BEZ POWROTU” | Ten jest przystosowany / do głębokości, / z których nikt / nie jest w stanie / wrócić. |
| 1:18.58–1:20.71 | Grafika (góra) + Ty | „Co sądzisz?” + pole komentarza | pole pisze się samo | Co sądzisz / o tym zegarku? / Napisz w komentarzu |
| 1:20.71–1:23.41 | Ty na pełnym kadrze + duże słowo nad głową | karta profilu @zegarkidawida + przycisk Obserwuj | tap w „Obserwuj” → „Obserwujesz”, niski hit (wersja SFX), punch-in | i obserwuj / po więcej! |

## Lista cięć (surowy materiał → wideo)
| # | Surowy IN | Surowy OUT | Wideo IN | Wideo OUT | Słowa |
|---|---|---|---|---|---|
| 1 | 0.12 | 4.96 | 0.00 | 4.84 | zegarek, który mógłbyś wrzucić najgłębsze miejsce na ziemi, a po wyciągnięciu nadal by działał |
| 2 | 5.08 | 6.43 | 4.84 | 6.19 | to Rolex Deepsea Challenge. |
| 3 | 6.62 | 7.47 | 6.19 | 7.04 |  |
| 4 | 7.91 | 19.41 | 7.04 | 18.54 | W norowo -marianskiego znajduje się na głębokości niespełna 11 tysięcy metrów, panuje tam ciśnienie ponad tysiąc razy większe niż to, które doświadczysz w tej chwili, zmiotłoby pod nim kadłup łoż i podwodnej niczym aluminiową puszkę. |
| 5 | 19.55 | 20.45 | 18.54 | 19.44 |  |
| 6 | 20.72 | 30.12 | 19.44 | 28.84 | Ten zegarek jest przystosowany do dokładnie takiej głębokości, oznacza to, że nie ma na tej planecie miejsca do którego mógłbyś go zabrać i osiągnąć jego granice, by trzymałości. |
| 7 | 30.25 | 37.76 | 28.84 | 36.35 | pomysł został już wcześniej sprawdzony w 2012 roku. eksperymentalną wersję Zegarka przymocowano do ramienia robota Łodzi podwodnej Jamesa |
| 8 | 37.93 | 39.03 | 36.35 | 37.45 | Cameron 'a. |
| 9 | 39.12 | 41.35 | 37.45 | 39.68 | Zegarek dotarł na samodnorowo -marianskiego i |
| 10 | 41.47 | 42.59 | 39.68 | 40.80 | wrócił z tamtąd, |
| 11 | 42.76 | 43.34 | 40.80 | 41.38 | nadal działając. |
| 12 | 43.45 | 44.61 | 41.38 | 42.54 |  |
| 13 | 45.24 | 47.58 | 42.54 | 44.88 | model był prawdziwy instalowym potworem, |
| 14 | 47.73 | 54.23 | 44.88 | 51.38 | ten jest jego produkcyjną wersą skopertą i branzletą wykonaną z autoeskiego tytanu RLX firmy Rolex. |
| 15 | 54.38 | 57.13 | 51.38 | 54.13 | pierwszy raz, kiedy marka zastosowała ten materiał w |
| 16 | 57.32 | 58.47 | 54.13 | 55.28 | takim zegarku. Dzięki |
| 17 | 58.69 | 68.30 | 55.28 | 64.89 | temu jest od 30 % rzej się od modelu eksperymentalnego, a mimo koperty o średnicy aż 50 milimetrów i szaf kierowego szkła grubości 9 ,5 milimetra, |
| 18 | 68.43 | 72.74 | 64.89 | 69.20 | cały zegarek waży zaledwie około 250 gramów, żej niż nie jeden. |
| 19 | 72.84 | 74.02 | 69.20 | 70.38 | Telefon! |
| 20 | 74.24 | 78.94 | 70.38 | 75.08 | Każdy inny zegarek nurkowy jest przystosowany do głębokości, do których rada podobnie nikt nie dotrzesz. |
| 21 | 79.16 | 81.74 | 75.08 | 77.66 | Ten jest przystosowany do głębokości, z których nikt nie jest w stanie wrócić. |
| 22 | 81.85 | 82.77 | 77.66 | 78.58 |  |
| 23 | 83.12 | 86.66 | 78.58 | 82.12 | Co sądzić o tym zegarku, napisz w komentarzu i obserwuj. Po |
| 24 | 86.81 | 88.10 | 82.12 | 83.41 | więcej! |

## Co poprawiłem w przeglądach
**Pass 1 (stillsy kluczowych beatów):** odwrócone kanały kolorów (BGRA) – cały obraz był złoty; nagłówek hooka nachodził na zegarek → zdjęcie przesunięte pod nagłówek; kółko z Tobą ucinało brodę → mniejsza skala; dwuliniowe słowa („STALOWY POTWÓR”, „PIERWSZY RAZ”, „NADAL DZIAŁA”) dotykały włosów → mniejszy rozmiar; linia wymiaru 50 mm wypadała poza panel; etykieta „−30%” nachodziła na opis; „11 000 m” przy prawej krawędzi (strefa przycisków) → przesunięte w lewo; przycisk „Obserwuj” wystawał z karty; „TYTAN” wychodził poza kartę; pusty pill przed animacją Camerona; zoom na zegarek na ramieniu robota źle centrował.
**Pass 2 (cały film co 0,5 s):** pole komentarza pisało się za wolno (nie kończyło przed cięciem) → szybciej i wcześniej; karta „Obserwuj” pojawiała się z opóźnieniem zostawiając pustkę nad głową → natychmiast; zanurzenie 2012 miało ~2 s „pustej” grafiki → dodany żywy licznik głębokości; wiersz „Deepsea Challenge: 11 000 m” nie zdążał się pokazać → usunięty; hook B startował od „−0 m” → startuje od dużej liczby.

**Runda 2 (Twoje zgłoszenie: „v2 – dźwięk psuje się pod koniec”):** w miksie ffmpeg (loudnorm + amix w jednym łańcuchu) głos urywał się ok. 80,5 s – zostawały same efekty, a od 82,5 s cisza. Teraz miks liczony bezpośrednio: gotowy głos −14 LUFS + efekty −6 dB (niski hit dodatkowo −4 dB). Sprawdzone automatycznie co 2 s na całej długości: głos w finalnym pliku różni się od czystego głosu o mniej niż 1 dB. Wynik: −14,7 LUFS, szczyt −1,5 dBFS.

## Ograniczenia
- Surówka ma tylko 352x626 px, więc twarz w 1080x1920 jest miękka (upscale ~4x). Jeśli wyślesz oryginał 4K/1080p (nie „compressed”), podmienię źródło – reszta montażu zostaje bez zmian.
- Brak referencji strukturalnej/efektów (pola były puste), więc nie mogłem zestawić klatek obok wzorca.
