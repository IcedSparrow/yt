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
- Runda 1: pełny render v1 + v2 SFX + 2 hooki — czeka na Twoją akceptację.

## Wybory podjęte bez pytania
1. Od razu pełny render (bez czekania na OK beatów/stillsów), bo prosiłeś „wykonaj mi to”.
2. Dwa pliki SnapInsta potraktowałem jako ruchomy b-roll (nie referencje): zapięcie z logo i nowy model z czystą tarczą.
3. Napisy wg tego, co mówisz: „To nie **jest** podróbka”, „**nosił** na ręce”, „**Tom** rzuca wyzwanie”, „Seiko zastąpił **Rolexem Air-Kingiem**” (tak słyszę w nagraniu — sprawdź, czy chcesz to zostawić), „**To** jeden z najdziwniejszych”, CTA „Co o tym sądzisz? Napisz w komentarzu i obserwuj po więcej!”.
4. Nie rysowałem logo Domino's (cudzy znak) — pokazuję je tylko na Twoich zdjęciach/wideo; w grafikach jest nazwa tekstem i kawałki pizzy jako ikony.
5. Dodane w grafikach: „Edycja Domino's”, oś czasu Bulova → Seiko → Air-King → Oyster Perpetual, 7 dni tygodnia, 27 ikon pizzy, przykładowy komentarz „Sprzedałbym każdą pizzę za niego”, licznik polubień 1 → 128 (dekoracja, nie dane).
6. Bez muzyki. Zdjęcie na mankiecie (wrist_cuff) niewykorzystane — dubluje hook.

## Cue sheet


## Lista cięć


## Co poprawiłem w przeglądach
**Pass 1 (stillsy):** zdjęcie z ręki ma 2576 px (nie 2000) → pierścień w hooku był obok logo, przeliczony; pusta karta Seiko → dodany tytuł „Seiko z logo Domino's”; etykiety porównania leżały na logo → przeniesione pod kartę, kadr poszerzony, by logo było całe; etykiety na wideo zasłaniały zegarek → wideo zaczyna się niżej, etykiety w ciemnym pasie u góry; czat miał pustą dolną połowę → bąbelek „Tom Monaghan pisze…”.
**Pass 2 (cały film co 0,5 s):** pierwsza linia napisów była przygaszona (karaoke) w pierwszej klatce → pełna jasność od razu; dopasowane pierścienie (hook, zielona podkładka); sprawdzona końcówka (ruch do ostatniej klatki) i miks v2.

## Ograniczenia
- Surówka 400x710 („compressed”) — twarz miękka po powiększeniu; oryginał 1080p/4K da ostrzejszy obraz bez zmian w montażu.
- Brak referencji strukturalnej/efektów.
