# Patek Philippe 4975/1G Królowej Elżbiety II — reel (Zegarkidawida)

## Pliki
| Plik | Co to |
|---|---|
| `Krolowa_Patek_reel_v1.mp4` | Wersja główna: 1080x1920, 30 fps, 48,8 s, H.264 CRF 14, głos −14 LUFS |
| `Krolowa_Patek_reel_v2_SFX.mp4` | Ten sam obraz + subtelne efekty (swoosh / tick / klik / niski hit na „obserwuj”) |
| `hooks/hook_B_czarne_tlo.mp4` | Alternatywny hook (4 s): zegarek na czarnym tle + „Zegarek Królowej” |
| `hooks/hook_C_ty_pelny_kadr.mp4` | Alternatywny hook (4 s): Ty na pełnym kadrze + „BEZCENNY ZEGAREK” |
| `src/` | Silnik renderu, lista cięć, beaty, napisy, transkrypcja |

Hooki mają ten sam dźwięk co pierwsze 4 s wersji głównej — podmieniasz 1:1.

## Branding (motyw królewski, ten sam system co poprzednie filmy)
- Tło: granat #131A2C → #05070D, złote światło z lewej góry (10%), bokeh 4–7%
- Panel: #161D30, złota obwódka 30–38%, rogi 28 px, połysk u góry kart
- Akcent: #D9B36C (złoto), drugi: #EDE6D8 (perła), czerwień #D2555A tylko do przekreślenia wyceny
- Tekst #F5F2EC, wyciszony #9AA3B5
- Fonty: Inter Display Bold / Inter SemiBold / JetBrains Mono

## Ustawienia
- Surówka 464x826 → stałe 30 fps wg znaczników czasu; 0 zatrzymanych klatek, obraz 48,77 s = dźwięk 48,75 s.
- Prawdziwy kadr kamery (bez wycinania). Kadry: FULL (x2,33) i OKNO (x1,4, y 660–1420). Duże słowa skalowane do najwyższego punktu włosów w beacie.
- Napisy: Inter SemiBold 60 px, karaoke (pierwsza linia od razu pełna), słowo-klucz złote, y=1500.
- Cięcia: cisza < −38 dB ≥ 0,22 s → ~0,15 s, 10 ms fade (51,6 s → 48,8 s); koniec ~0,2 s po „więcej”.
- Przejścia: 0,3 s wipe od góry ze złotą linią przy zmianie układu. Spokojny styl (Twoje zasady: jedna rzecz naraz, bez bounce).
- Audio: highpass 70 Hz + loudnorm 2-pass; v2 −14,8 LUFS, szczyt −1,5 dBFS, głos sprawdzony co 2 s (bez odchyleń > 2 dB).

## Status
- Runda 1: spokojna wersja (pliki w głównym folderze) — zostaje jako alternatywa.
- **Runda 2: wersja w stylu MrBeasta + nowy hook** — folder `mrbeast/` (v1, v2 SFX, 3 hooki). Silnik: `src/render_qb.py`, `src/audio_qb.py`, beaty `src/beats_qb.json`.

## Runda 2 — styl MrBeast + nowy hook
**Nowy hook (główny, wbudowany w film, 0–2,7 s):** miniaturowy układ „twarz + przedmiot + krótki tekst + strzałka”: dwa przechylone zdjęcia w białych ramkach (uśmiechnięta królowa w koronie | Patek 4975/1G), delikatnie się kołyszą; złote promienie światła w tle; iskry migoczące na diamentach lunety; od pierwszej klatki napis „ZROBIONY / TYLKO DLA NIEJ 👑” (biały + żółty, gruby obrys); czerwona strzałka do zegarka; na „niesamowita kobieta” żółta ramka na zdjęciu królowej + 😍 + wstrząs; pod spodem Ty w kółku + „PATEK PHILIPPE 4975/1G”.
**Alternatywne hooki (4 s, podmiana 1:1):**
- `hook_A_tylko_dla_niej.mp4` — powyższy (taki jak w filmie),
- `hook_B_ile_jest_wart.mp4` — zegarek na czerni z iskrami, „ILE JEST WART?”, cyfry ceny kręcą się jak w automacie i na 1,35 s zatrzymują się czerwoną pieczątką „BEZCENNY”,
- `hook_C_zegarek_dla_krolowej.mp4` — zdjęcie królowej w żółtej ramce, „ZEGAREK TYLKO DLA KRÓLOWEJ”, 👑 💎, Ty w oknie.

**W całym filmie doszło:** napisy MrBeast (gruby obrys, żółte słowa-klucze, pop każdej linii); duże słowa wyskakują; jump-zoom co linię (zakotwiczony na czubku głowy — duże słowa mają pełne miejsce, usta nigdy nie wchodzą pod napisy); 11 wstrząsów z błyskiem (G w numerze, 400, gwiazd, tak ważni, „nigdy”, na sprzedaż, ???, wycenić, bezcenny, obserwuj); 21 emoji na słowo; czerwone strzałki (zegarek na ręce królowej, zegarek w kolażu); najazdy na szczegóły (zegarek królowej x1,55, perły x1,45); iskry na diamentach przy obu zdjęciach zegarka; szybkie przejścia whip z rozmyciem (napisy ostre); 146 efektów dźwiękowych (whoosh, pop, ding, „ka-ching” przy rekordzie, boom przy wstrząsach, klikanie przy liczeniu i losowaniu ceny).
Świadomie łamie Twoje zasady „bez bounce” i „jedna rzecz naraz” — poprosiłeś o styl MrBeasta. Twarz, kadr, pozycja napisów i czysty obraz bez zmian.

**Przegląd rundy 2:** hook C — napis zasłaniał twarz królowej → przeniesiony pod zdjęcie; hook B/C — złe przekazanie wariantu przy podglądzie → poprawione; duże słowa („JEDEN ZEGAREK”, „TAK WAŻNI?”) były malutkie, bo jump-zoom podnosił głowę → zoom zakotwiczony na czubku głowy, punch-in złagodzony do 3,5% (usta zawsze nad napisami); sprawdzone: 0 zatrzymanych klatek, obraz 48,77 s = dźwięk 48,75 s, v2 −14,4 LUFS, głos bez odchyleń > 2 dB.

## Wybory podjęte bez pytania
1. Od razu pełny render (bez czekania na OK beatów/stillsów), bo prosiłeś „wykonaj mi to”.
2. Styl spokojny/premium (wg Twojego briefu), nie MrBeast — temat królewski; jeśli chcesz wersję MrBeast jak przy Domino's, zrobię ją na tym samym materiale.
3. Napisy wg tego, co mówisz: „Ja czekam, aż **Rolex** zrobi coś takiego dla mnie” (w skrypcie Casio), „najdroższym zegarkiem **na świecie**” (w skrypcie „w historii”), „na zawsze zostanie”.
4. **Nie użyłem fotomontażu**, na którym zegarek jest wklejony obok królowej w futrze (zdjęcie 4) — wygląda, jakby go nosiła, a to nie jest prawdziwe zdjęcie. Użyłem natomiast kolażu „królowa | zegarek” (zdjęcie 5), bo wyraźnie są to dwa osobne zdjęcia.
5. Na zdjęciu królowej w perłach obrysowuję jej **własny złoty zegarek** na ręce (pod „uwielbiała zegarki”), nie sugerując, że to 4975/1G.
6. Dodane w grafikach: „ELŻBIETA II · 1926–2022”, „G = złoto białe”, „perły · diamenty”, „Wielka wystawa · Londyn”, rekord aukcji „Patek Grandmaster Chime 6300A · 31 mln $” (2019), żartobliwy pasek „Rolex → Zegarkidawida: szacowany czas: nigdy”, losujące się cyfry wyceny, przykładowy komentarz „Najpiękniejszy zegarek świata”. Sprawdź fakty przed publikacją.
7. Bez muzyki.

## Cue sheet
| Wyjście | Układ | Na ekranie | Animacja | Napisy |
|---|---|---|---|---|
| 0:00.00–0:01.20 | Zdjęcie na pełny ekran + Ty w kółku | Patek 4975/1G + „Zegarek Królowej” | statyczny pierwszy kadr, czytelny bez dźwięku | Królowa Elżbieta II. |
| 0:01.20–0:02.80 | Pływająca karta u góry + Ty w oknie | portret młodej królowej z tiarą | karta wjeżdża, etykieta pod kartą: ELŻBIETA II · 1926–2022 + korona | Co za niesamowita / kobieta. |
| 0:02.80–0:04.30 | Zdjęcie na pełny ekran + Ty w kółku | królowa w perłach (złoty zegarek na ręce) | etykieta: UWIELBIAŁA ZEGARKI + obrys wokół zegarka na ręce | Królowa uwielbiała / zegarki. |
| 0:04.30–0:06.46 | Ty na pełnym kadrze + duże słowo nad głową | „JEDEN ZEGAREK” / CHCĘ WAM POKAZAĆ | litery wjeżdżają kaskadowo, złote podkreślenie | Jest jeden zegarek, / który chcę wam pokazać. |
| 0:06.46–0:09.89 | Karta u góry + Ty w oknie | numer referencji | PATEK PHILIPPE pisze się samo, cyfry 49 · 75 · /1 · G pojawiają się dokładnie gdy je mówisz, potem „G = złoto białe” | Patek Philippe / 4975/1G. |
| 0:09.89–0:12.44 | Zdjęcie na pełny ekran + Ty w kółku | Patek 4975/1G na czarnym tle | etykieta: PERŁOWA BRANSOLETA | Absolutnie szalony zegarek / z perłową bransoletą. |
| 0:12.44–0:15.25 | Zdjęcie na pełny ekran + Ty w kółku | królowa w futrze i koronie | etykieta: DLA JEJ KRÓLEWSKIEJ MOŚCI + rysuje się korona | Powstał specjalnie / dla Jej Królewskiej Mości. |
| 0:15.25–0:19.26 | Karta u góry + Ty w oknie | 2015 · Królowa → Patek Philippe | korona rysuje się, strzałka „wypożyczenie”, pill „Wielka wystawa · Londyn” | W 2015 roku / Królowa wypożyczyła go / Patkowi / na wielką wystawę. |
| 0:19.26–0:21.96 | Karta u góry + Ty w oknie | siatka 80 tarcz + licznik | tarcze pojawiają się po kolei, licznik 0 → ≈400 na „400” | W Londynie / pokazano tam około / 400 zegarków. |
| 0:21.96–0:24.25 | Zdjęcie na pełny ekran + Ty w kółku | Patek 4975/1G na białym tle | etykieta: JEDNA Z NAJWIĘKSZYCH GWIAZD + rysuje się gwiazda | A ten był jedną / z największych gwiazd. |
| 0:24.25–0:26.21 | Ty na pełnym kadrze + duże słowo nad głową | „TAK WAŻNI?” / WYOBRAŹCIE SOBIE | litery wjeżdżają kaskadowo, złote podkreślenie | Wyobraźcie sobie, / że jesteście tak ważni, |
| 0:26.21–0:29.13 | Pływająca karta u góry + Ty w oknie | szkic projektu zegarka | karta wjeżdża, etykieta pod kartą: PROJEKT SPECJALNIE DLA NIEJ | że Patek Philippe / robi zegarek / specjalnie dla was. |
| 0:29.13–0:32.76 | Karta u góry + Ty w oknie | „Rolex → Zegarkidawida” + pasek ładowania | pasek prawie stoi, potem „SZACOWANY CZAS: NIGDY” | Ja czekam, / aż Rolex zrobi / coś takiego dla mnie. |
| 0:32.76–0:34.92 | Ty na pełnym kadrze + duże słowo nad głową | „NA SPRZEDAŻ?” / GDYBY TRAFIŁ | litery wjeżdżają kaskadowo, złote podkreślenie | Gdyby ten zegarek / kiedyś trafił na sprzedaż, |
| 0:34.92–0:37.84 | Karta u góry + Ty w oknie | rekord aukcji 31 mln $ vs zegarek królowej | złoty pasek rośnie poza rekord, „???” | w 100 procentach / stałby się najdroższym / zegarkiem na świecie. |
| 0:37.84–0:40.08 | Pływająca karta u góry + Ty w oknie | królowa + zegarek obok siebie | karta wjeżdża, etykieta pod kartą: NA ZAWSZE W RODZINIE KRÓLEWSKIEJ + korona | Ale myślę, że / na zawsze zostanie / w rodzinie królewskiej. |
| 0:40.08–0:41.76 | Karta u góry + Ty w oknie | wycena: losujące się cyfry | cyfry kręcą się, na „wycenić” zatrzymują się na ???, czerwone przekreślenie, „NIE DA SIĘ WYCENIĆ” + korona | Tego zegarka / nie da się wycenić. |
| 0:41.76–0:43.72 | Ty na pełnym kadrze + duże słowo nad głową | „BEZCENNY” | litery wjeżdżają kaskadowo, złote podkreślenie, punch-in | Jest po prostu / bezcenny. |
| 0:43.72–0:45.75 | Karta u góry + Ty w oknie | „Co uważasz?” + pole komentarza | pole pisze się samo, serce i polubienia | A ty co uważasz / na temat tego zegarka? |
| 0:45.75–0:48.78 | Ty na pełnym kadrze + duże słowo nad głową | karta @zegarkidawida + „Obserwuj” | złota obwódka, tap → „Obserwujesz” | Napisz w komentarzu / i obserwuj / po więcej. |

## Lista cięć
| # | Surowy IN | Surowy OUT | Wideo IN | Wideo OUT | Słowa |
|---|---|---|---|---|---|
| 1 | 0.00 | 4.30 | 0.00 | 4.30 | Królowa Elżbieta II. Co za niesamowita kobieta. Królowa uwielbiała zegarki. |
| 2 | 4.42 | 8.55 | 4.30 | 8.43 | Jest jeden zegarek, który chce Wam pokazać. Patek Philippe 49751G. |
| 3 | 8.69 | 9.32 | 8.43 | 9.06 |  |
| 4 | 9.53 | 10.36 | 9.06 | 9.89 |  |
| 5 | 10.59 | 14.93 | 9.89 | 14.23 | Absolutnie szalony zegarek z perłową branzoletą. Powstał specjalnie dla J. Królewskiej Mości. |
| 6 | 15.07 | 16.09 | 14.23 | 15.25 |  |
| 7 | 16.19 | 24.38 | 15.25 | 23.44 | W 2015 roku Królowa wypożyczyła Gopatkowi na wielką wystawę. W Londynie pokazano tam około 400 zegarków. A ten był jedną z największych gwiazd. |
| 8 | 24.54 | 25.35 | 23.44 | 24.25 |  |
| 9 | 25.62 | 33.08 | 24.25 | 31.71 | Wyobraźcie sobie, że jesteście tak ważni, że Patek Philippe robi zegarek specjalnie dla Was. Ja czekam, aż Rolex zrobi coś takiego dla |
| 10 | 33.18 | 34.23 | 31.71 | 32.76 | mnie. |
| 11 | 34.42 | 36.58 | 32.76 | 34.92 | Gdyby ten zegarek kiedyś trafił nasz przedaż, |
| 12 | 36.70 | 41.86 | 34.92 | 40.08 | stu procentach stałby się najdroższym zegarkiem na świecie. Ale myślę, że nas zawsze zostanie w rodzinie Królewskiej. |
| 13 | 41.98 | 43.66 | 40.08 | 41.76 | Tego zegarka nie da się wycenić. |
| 14 | 43.76 | 44.64 | 41.76 | 42.64 | Jest po prostu bezcenny. |
| 15 | 44.76 | 45.84 | 42.64 | 43.72 |  |
| 16 | 46.13 | 46.54 | 43.72 | 44.13 | A ty co |
| 17 | 46.62 | 49.23 | 44.13 | 46.74 | uważasz na temat tego zegarka? Napisz komentarzu |
| 18 | 49.34 | 50.30 | 46.74 | 47.70 | i obserwuj. |
| 19 | 50.50 | 51.58 | 47.70 | 48.78 | Po więcej. |

## Co poprawiłem w przeglądach
**Pass 1 (stillsy):** etykiety na zdjęciach królowej leżały na jej głowie → przeniesione w ciemny pas pod zdjęciem; przy zegarkach etykiety i kółko z Tobą przeniesione w pas nad zdjęciem (nic nie zasłania zegarka); kółko w hooku przeniesione na zapięcie bransolety; kółko z Tobą widoczne od pierwszej klatki ujęcia (wcześniej wjeżdżało z opóźnieniem).
**Pass 2 (cały film co 0,5 s):** licznik roku 1990 → 2015 docierał do „2015” po tym, jak to powiedziałeś → „2015” stoi od razu; hook B: kółko nachodziło na kopertę → przeniesione w górny pas; sprawdzone: ruch do ostatniej klatki, głos w v2.

## Ograniczenia
- Surówka 464x826 („compressed”) i część zdjęć małych (szkic 409 px, kolaż 447 px) — używam ich jako mniejszych kart. Oryginał nagrania w 1080p/4K da ostrzejszą twarz.
