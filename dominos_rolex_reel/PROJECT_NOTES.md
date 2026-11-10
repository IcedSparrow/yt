# Rolex × Domino's — reel (Zegarkidawida)

## Pliki
| Plik | Co to |
|---|---|
| `Dominos_Rolex_reel_v1.mp4` | Wersja główna: 1080x1920, 30 fps, 62,9 s, H.264 CRF 14, głos −14 LUFS |
| `Dominos_Rolex_reel_v2_SFX.mp4` | Ten sam obraz + ciche efekty (swoosh / tick / klik / niski hit na „obserwuj”) |
| `hooks/hook_B_wideo_tarcza.mp4` | Alternatywny hook (4 s): ruchome wideo czerwono-niebieskiej tarczy + nagłówek + Ty w kółku |
| `hooks/hook_C_ty_pelny_kadr.mp4` | Alternatywny hook (4 s): Ty na pełnym kadrze + „ROLEX ZA PIZZĘ?” |
| `src/` | Silnik renderu, lista cięć, beaty, napisy, transkrypcja |

Hooki mają ten sam dźwięk co pierwsze 4 s wersji głównej — podmieniasz 1:1.

## Branding
- Tło: grafit #15171C → #060708, złote światło z lewej góry (10%), bokeh 4–7%
- Panel: #1A1D23, złota obwódka 30–38%, rogi 28 px, połysk u góry kart
- Akcent: #D9B36C (złoto kanału); kolory z tarczy jako drugie akcenty: czerwony #E5484D (przekreślenia, pieczątka, wersja czerwono-niebieska), niebieski #3D9BE0
- Tekst #F4F2EE, wyciszony #9BA1AB
- Fonty: Inter Display Bold (duże słowa), Inter SemiBold (napisy), JetBrains Mono (etykiety) — ten sam system co Deepsea i Rolex Cafe

## Ustawienia
- Surówka 400x710 przeliczona na stałe 30 fps wg znaczników czasu (lekcja z Rolex Cafe — brak dryfu i zacięcia na końcu; sprawdzone: 0 zatrzymanych klatek, obraz = dźwięk = 62,9 s).
- Prawdziwy kadr kamery wszędzie (pokój, bez wycinania). Kadry: FULL (x2,7) i OKNO (x1,6, y 660–1420). Duże słowa skalowane do najwyższego punktu włosów w danym beacie.
- Napisy: Inter SemiBold 60 px, karaoke (słowo rozjaśnia się na wypowiedzenie; pierwsza linia od razu pełna), słowo-klucz złote, y=1500.
- Cięcia: cisza < −36 dB ≥ 0,22 s → ~0,15 s, 10 ms fade (66,5 s → 62,9 s), koniec ~0,1 s po „więcej” (nagranie kończy się tuż po słowie).
- Przejścia: 0,3 s „wipe” od góry ze złotą linią przy każdej zmianie układu.
- Audio: highpass 70 Hz + loudnorm 2-pass (−14 LUFS); SFX miksowane w numpy, sprawdzone co 2 s — głos nigdzie nie odbiega o >2 dB.

## Status
- Runda 1: spokojna wersja (pliki w głównym folderze) — zostaje jako alternatywa.
- **Runda 2: wersja w stylu MrBeasta** — folder \`mrbeast/\` (v1, v2 SFX, 2 hooki). Silnik: \`src/render_beast.py\`, \`src/audio_beast.py\`.

## Runda 2 — styl MrBeast (co doszło)
Świadomie łamie część Twoich pierwotnych zasad („bez bounce”, „jedna rzecz naraz”), bo poprosiłeś o styl MrBeasta. Twarz, kadr, pozycja napisów i brak filtrów — bez zmian.
1. Napisy: Inter Display Bold 66 px, biało-czarny gruby obrys, słowa-klucze żółte #FFD23F, każda linia wyskakuje (pop 0,14 s).
2. Duże słowa nad głową: pop ze sprężystym „back-out”, czarny obrys, żółte podkreślenie; przekreślenia grubsze (czerwień + czarny kontur).
3. Jump-zoom: na pełnym kadrze co linię napisów przeskok 100% ↔ 108% (zakotwiczony na twarzy, głowa nigdy nie jest ucinana — limit dużych słów liczony z uwzględnieniem zoomu).
4. 14 momentów „impact”: wstrząs kadru 0,3 s + biały błysk 0,1 s (przekreślenia, pieczątka, $20 000, $100 000+, „wyzwanie”, „ogromna kwota”, „dał radę”, „symbol statusu”, „najdziwniejszy”, „w salonie”, „tysiące pizz”, tap „Obserwuj”).
5. 19 emoji wyskakujących na słowo (❌ 🚫 💪 🍕 ⌚ 🤔 🔥 💰 😱 📈 ✅ 🎁 🚀 👑 💎 🤯 💬 🔔) — po bokach, nigdy na twarzy ani na logo.
6. Czerwone strzałki MrBeast (czerwień + czarny kontur) do logo: hook, zielona podkładka, obie tarcze z porównania.
7. Najazdy na szczegóły: hook (do logo, x1,32), zielona podkładka (x1,45), porównanie tarcz (x1,55 na logo).
8. Przejścia: szybki whip 0,2 s z rozmyciem ruchu przy każdej zmianie ujęcia (napisy zostają ostre nad przejściem); między Twoimi pełnymi kadrami — jump-cut.
9. Kółko z Tobą widoczne od pierwszej klatki każdego ujęcia (wcześniej wjeżdżało z opóźnieniem).
10. SFX (v2, 166 efektów): whoosh przy przejściach, pop przy słowach/emoji/etykietach, swish przy strzałkach i przekreśleniach, boom przy wstrząsach, ding przy osi czasu, „ka-ching” przy licznikach dolarów, klikanie klawiatury przy czacie i komentarzu, klik + ding przy „Obserwuj”. Głos nienaruszony (sprawdzone co 2 s), całość −14 LUFS, szczyt −0,6 dBFS.

Przegląd rundy 2: ciemna klatka między dwoma klipami wideo → whip przy każdej zmianie ujęcia; kółko z Tobą znikało na ~0,5 s po przejściu → widoczne od razu; napisy rozmywały się w przejściu → rysowane nad przejściem; sprawdzone: 0 zatrzymanych klatek, obraz = dźwięk = 62,9 s.

## Wybory podjęte bez pytania
1. Od razu pełny render (bez czekania na OK beatów/stillsów), bo prosiłeś „wykonaj mi to”.
2. Dwa pliki SnapInsta potraktowałem jako ruchomy b-roll (nie referencje): zapięcie z logo i nowy model z czystą tarczą.
3. Napisy wg tego, co mówisz: „To nie **jest** podróbka”, „**nosił** na ręce”, „**Tom** rzuca wyzwanie”, „Seiko zastąpił **Rolexem Air-Kingiem**” (tak słyszę w nagraniu — sprawdź, czy chcesz to zostawić), „**To** jeden z najdziwniejszych”, CTA „Co o tym sądzisz? Napisz w komentarzu i obserwuj po więcej!”.
4. Nie rysowałem logo Domino's (cudzy znak) — pokazuję je tylko na Twoich zdjęciach/wideo; w grafikach jest nazwa tekstem i kawałki pizzy jako ikony.
5. Dodane w grafikach: „Edycja Domino's”, oś czasu Bulova → Seiko → Air-King → Oyster Perpetual, 7 dni tygodnia, 27 ikon pizzy, przykładowy komentarz „Sprzedałbym każdą pizzę za niego”, licznik polubień 1 → 128 (dekoracja, nie dane).
6. Bez muzyki. Zdjęcie na mankiecie (wrist_cuff) niewykorzystane — dubluje hook.

## Cue sheet
| Wyjście | Układ | Na ekranie | Animacja | Napisy |
|---|---|---|---|---|
| 0:00.00–0:01.50 | Zdjęcie na pełny ekran + Ty w kółku | Air-King z logo na ręce, „Rolex z logo pizzerii?” | statyczny pierwszy kadr, złoty pierścień rysuje się wokół logo | Rolex z logo pizzerii? |
| 0:01.50–0:03.28 | Ty na pełnym kadrze + duże słowo nad głową | „PODRÓBKA? ŻART?” / TO NIE JEST | litery wjeżdżają kaskadowo, czerwone przekreślenie | To nie jest podróbka / ani żart. |
| 0:03.28–0:05.06 | Karta u góry + Ty w oknie | metka „CENA — zł” | metka rysuje się, czerwona pieczątka „NIE NA SPRZEDAŻ” na „kupić” | Tego zegarka / nie dało się kupić. |
| 0:05.06–0:08.32 | Ty na pełnym kadrze + duże słowo nad głową | „ZAPRACUJ NA NIEGO” / SPRZEDAJĄC PIZZĘ | litery wjeżdżają kaskadowo, złote podkreślenie, punch-in 6% | Trzeba było na niego / zapracować, / sprzedając pizzę. |
| 0:08.32–0:13.78 | Karta u góry + Ty w oknie | oś czasu BULOVA → SEIKO → AIR-KING → OYSTER PERPETUAL + Tom Monaghan | węzły zapalają się na nazwę zegarka | Lata 70. / Tom Monaghan, / współzałożyciel Domino's, / nosił na ręce / Bulovę z logo / swojej firmy. |
| 0:13.78–0:18.89 | Karta u góry + Ty w oknie | czat: franczyzobiorca → Tom Monaghan | kropki pisania, pytanie pisze się samo, potem „Tom pisze…” | Pewnego dnia / jeden z franczyzobiorców / pyta go wprost: / „Co muszę zrobić, / żeby dostać / taki zegarek?” |
| 0:18.89–0:19.86 | Ty na pełnym kadrze + duże słowo nad głową | „WYZWANIE” / TOM MONAGHAN | litery wjeżdżają kaskadowo, złote podkreślenie | Tom rzuca wyzwanie: |
| 0:19.86–0:23.15 | Karta u góry + Ty w oknie | licznik $0 → $20 000 + 7 dni tygodnia | licznik rośnie na „20 tysięcy”, dni wypełniają się na „tygodnia” | sprzedaj pizzę / za 20 tysięcy dolarów / w ciągu jednego tygodnia. |
| 0:23.15–0:25.01 | Ty na pełnym kadrze + duże słowo nad głową | „OGROMNA KWOTA” / W TAMTYCH CZASACH | litery wjeżdżają kaskadowo, złote podkreślenie | W tamtych czasach / to była ogromna kwota. |
| 0:25.01–0:27.81 | Karta u góry + Ty w oknie | $20 000 (lata 70.) → $100 000+ (dziś) | strzałka rysuje się, licznik rośnie na „100 tysiącom” | Dziś odpowiadałaby / ponad 100 tysiącom dolarów. |
| 0:27.81–0:29.11 | Ty na pełnym kadrze + duże słowo nad głową | „DAŁ RADĘ” / FRANCZYZOBIORCA | litery wjeżdżają kaskadowo, złote podkreślenie | Franczyzobiorca dał radę. |
| 0:29.11–0:33.50 | Karta u góry + Ty w oknie | oś czasu BULOVA → SEIKO → AIR-KING → OYSTER PERPETUAL + „Seiko z logo Domino's” + kolejka | węzły zapalają się na nazwę zegarka, ludziki w kolejce pojawiają się po kolei | Dostał Seiko / z logo Domino's, / a za nim w kolejce / ustawili się następni. |
| 0:33.50–0:35.73 | Ty na pełnym kadrze + duże słowo nad głową | „STAWKA W GÓRĘ” / LATA 80. | litery wjeżdżają kaskadowo, złote podkreślenie | W latach 80. / stawka poszła w górę. |
| 0:35.73–0:39.23 | Zdjęcie/wideo na pełny ekran + Ty w kółku | Air-King z logo na zielonej podkładce | etykiety na słowo: SEIKO  →  ROLEX AIR-KING, →  OYSTER PERPETUAL + pierścień wokół logo | Seiko zastąpił / Rolexem Air-Kingiem, / a później / Oyster Perpetual. |
| 0:39.23–0:42.23 | Ty na pełnym kadrze + duże słowo nad głową | „SYMBOL STATUSU” | litery wjeżdżają kaskadowo, złote podkreślenie, punch-in 6% | Zegarek z pizzerii / stał się symbolem / statusu w całej sieci. |
| 0:42.23–0:45.08 | Pływająca karta u góry + Ty w oknie | porównanie tarcz: czerwono-niebieskie logo | pierścień rysuje się wokół logo, etykieta pod kartą | Pierwsze egzemplarze / miały czerwono-niebieskie / logo na tarczy. |
| 0:45.08–0:47.02 | Pływająca karta u góry + Ty w oknie | porównanie tarcz: wersja monochromatyczna | pierścień rysuje się wokół logo, etykieta pod kartą | Najrzadsza jest / wersja monochromatyczna. |
| 0:47.02–0:50.15 | Zdjęcie/wideo na pełny ekran + Ty w kółku | wideo: nowy model z czystą tarczą na ręce | etykiety na słowo: CZYSTA TARCZA, GRAWEROWANY DEKIEL | Nowsze modele, / takie jak ten, / mają czystą tarczę, / grawerowany dekiel |
| 0:50.15–0:53.07 | Zdjęcie/wideo na pełny ekran + Ty w kółku | wideo: logo Domino's na zapięciu bransolety | etykiety na słowo: LOGO DOMINO'S NA BRANSOLECIE | i logo Domino's / na bransolecie Oyster. |
| 0:53.07–0:55.05 | Ty na pełnym kadrze + duże słowo nad głową | „NAJDZIWNIEJSZY ROLEX” / JEDEN Z | litery wjeżdżają kaskadowo, złote podkreślenie, punch-in 6% | To jeden z / najdziwniejszych Rolexów świata. |
| 0:55.05–0:56.09 | Ty na pełnym kadrze + duże słowo nad głową | „W SALONIE” / NIE KUPISZ GO | litery wjeżdżają kaskadowo, czerwone przekreślenie | Nie kupisz go w salonie. |
| 0:56.09–0:59.15 | Karta u góry + Ty w oknie | siatka 27 kawałków pizzy + „TYSIĄCE PIZZ” | kawałki pojawiają się po kolei | Kiedyś trzeba było / na niego zarobić, / sprzedając tysiące pizz. |
| 0:59.15–1:00.71 | Karta u góry + Ty w oknie | „Co sądzisz?” + pole komentarza | pole pisze się samo, serce i licznik polubień | Co o tym sądzisz? / Napisz w komentarzu |
| 1:00.71–1:02.90 | Ty na pełnym kadrze + duże słowo nad głową | karta @zegarkidawida + „Obserwuj” | złota obwódka, tap → „Obserwujesz”, niski hit w wersji SFX | i obserwuj / po więcej! |


## Lista cięć
| # | Surowy IN | Surowy OUT | Wideo IN | Wideo OUT | Słowa |
|---|---|---|---|---|---|
| 1 | 0.00 | 5.06 | 0.00 | 5.06 | Piolek z logo pizzerii. To nie jest podróbka ani żart. Tego zegarka nie dało się kupić. |
| 2 | 5.26 | 6.91 | 5.06 | 6.71 | Trzeba było na niego zapracować, |
| 3 | 7.19 | 8.80 | 6.71 | 8.32 | pizzę. |
| 4 | 8.95 | 10.82 | 8.32 | 10.19 | Tata 70. Tom Monaghana. |
| 5 | 10.89 | 12.03 | 10.19 | 11.33 | Spółzałżyciel Domino. |
| 6 | 12.11 | 14.56 | 11.33 | 13.78 | Nosił na ręce bulowe z logo swojej firmy. |
| 7 | 14.65 | 17.12 | 13.78 | 16.25 | Pewnego dnia jeden z franczyzobiorców pyta go wprost. |
| 8 | 17.34 | 19.00 | 16.25 | 17.91 | Co muszę zrobić, żeby dostać taki zegarek? |
| 9 | 19.11 | 20.09 | 17.91 | 18.89 |  |
| 10 | 20.33 | 23.40 | 18.89 | 21.96 | Tom rzuca wyzwanie. Sprzedaj pizzę za 20 tysięcy dolarów w |
| 11 | 23.65 | 26.80 | 21.96 | 25.11 | ciągu jednego tygodnia. W tamtych czasach to była ogromna kwota. Dziś |
| 12 | 26.92 | 34.27 | 25.11 | 32.46 | odpowiadałaby ponad 100 tysiącom dolarów. Franczyzobiorca dał radę. Dostał Seiko z logo Domino, a zanim wykolejcy ustaliły lisie, |
| 13 | 34.38 | 35.42 | 32.46 | 33.50 | następni. |
| 14 | 35.49 | 43.50 | 33.50 | 41.51 | W latach 80. stapka poszła w górę. Seiko zastąpił Rolexem Air -Kingiem, a później Oyster Perpetual. Zegarek z pizzerią stał się symbolem statusu w |
| 15 | 43.78 | 47.35 | 41.51 | 45.08 | całej sieci. Pierwsze egzemplarze miały czerwono niebieskie logo na tarczy. |
| 16 | 47.52 | 50.15 | 45.08 | 47.71 | Najżawcza jest wersja monochromatyczna. Nowsze modele, |
| 17 | 50.28 | 54.72 | 47.71 | 52.15 | takie jak ten mają czystą tarczy, grawerowany dekiel i logo Domino na branzolecie. Oyster! |
| 18 | 54.83 | 55.77 | 52.15 | 53.09 |  |
| 19 | 55.90 | 58.90 | 53.09 | 56.09 | jeden z najdziwniejszych Rolexów świata. Nie kupisz go w salonie. |
| 20 | 59.02 | 60.74 | 56.09 | 57.81 | Kiedyś trzeba było na niego zarobić. |
| 21 | 60.93 | 62.27 | 57.81 | 59.15 | tysiące piz. |
| 22 | 62.56 | 64.17 | 59.15 | 60.76 | Co o tym sądnić? Napisz w komentarzu i |
| 23 | 64.24 | 65.32 | 60.76 | 61.84 | obserwuj. |
| 24 | 65.46 | 66.52 | 61.84 | 62.90 | Powięcej! |


## Co poprawiłem w przeglądach
**Pass 1 (stillsy):** zdjęcie z ręki ma 2576 px (nie 2000) → pierścień w hooku był obok logo, przeliczony; pusta karta Seiko → dodany tytuł „Seiko z logo Domino's”; etykiety porównania leżały na logo → przeniesione pod kartę, kadr poszerzony, by logo było całe; etykiety na wideo zasłaniały zegarek → wideo zaczyna się niżej, etykiety w ciemnym pasie u góry; czat miał pustą dolną połowę → bąbelek „Tom Monaghan pisze…”.
**Pass 2 (cały film co 0,5 s):** pierwsza linia napisów była przygaszona (karaoke) w pierwszej klatce → pełna jasność od razu; dopasowane pierścienie (hook, zielona podkładka); sprawdzona końcówka (ruch do ostatniej klatki) i miks v2.

## Ograniczenia
- Surówka 400x710 („compressed”) — twarz miękka po powiększeniu; oryginał 1080p/4K da ostrzejszy obraz bez zmian w montażu.
- Brak referencji strukturalnej/efektów.
