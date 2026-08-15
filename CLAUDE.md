# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Co to za projekt

Nieoficjalna, statyczna mapa zawodów strzeleckich Wielkopolskiego Związku Strzelectwa Sportowego (WZSS). Codziennie w nocy dane są scrapowane z `https://portal.wzss.pl/competitions/current`, przetwarzane do JSON-a i plików `.ics`, a strona (Leaflet + vanilla JS) publikowana jest na GitHub Pages z katalogu `docs/`.

Nie ma tu buildu, frameworka JS ani testów — to celowo prosty, kilkuplikowy projekt automatyzowany przez GitHub Actions.

## Komendy

```bash
# Instalacja zależności (brak requirements.txt / pyproject.toml — instaluj ręcznie)
pip install requests beautifulsoup4

# Pełny pipeline: scraping -> competitions.json, locations.csv, calendars/*.ics
python run.py            # zmienia cwd na katalog skryptu, woła fetch_competitions.main()
# lub bezpośrednio:
python fetch_competitions.py

# Sprawdzenie brakujących współrzędnych/stron klubów po scrapowaniu
python verify_locations.py

# Lokalny podgląd mapy (map.html robi fetch('competitions.json') więc wymaga serwera HTTP, nie file://)
python -m http.server 8000
# -> http://localhost:8000/map.html

# Lint (konfiguracja ruff istnieje w .ruff_cache, ale brak pliku konfiguracyjnego ruff w repo)
ruff check .
```

Brak testów jednostkowych w repo.

## Architektura

### Pipeline danych (`fetch_competitions.py`)

1. **Pobranie i parsowanie HTML** (`fetch_competitions_html`, `parse_competitions`) — strona portalu WZSS jest scrapowana przez BeautifulSoup na podstawie klas Tailwind (`text-2xl` jako nagłówki miesięcy, `sm:grid-cols-12` jako wiersze zawodów). To krucha, strukturalna zależność od HTML-a portalu — jeśli scraper przestanie działać, najpierw sprawdź, czy zmieniła się struktura/klasy CSS na `portal.wzss.pl`.
2. **Wzbogacenie o współrzędne** — `locations.csv` to ręcznie utrzymywana mapa `location_text -> (latitude, longitude, website)`. Nowe lokalizacje wykryte podczas scrapowania trafiają do CSV z pustymi współrzędnymi (`update_locations_csv`) i wymagają ręcznego uzupełnienia lat/lon przed kolejnym uruchomieniem, inaczej zawody nie pojawią się na mapie (`verify_locations.py` do tego służy).
3. **Generowanie kalendarzy ICS** (`save_calendars`, `generate_slug`, `parse_date_range_for_ics`) — dla każdego klubu tworzony jest osobny plik `calendars/<slug>.ics` (katalog lokalny, gitignorowany — patrz niżej), gdzie `<slug>` to transliterowana nazwa klubu (polskie znaki -> ASCII, spacje -> `_`). Parsowanie dat obsługuje polskie skróty miesięcy (`sty`, `lut`, ...) oraz zakresy dat typu `"27 - 28 lut 2026"`.
4. **Wyjścia**: `competitions.json` (lista lokalizacji z zagnieżdżonymi zawodami) i lokalny katalog `calendars/` — oba to tylko pośredni build output kroku "Fetch new data" w workflow, kopiowany dalej do `docs/`.

### Publikacja (`docs/`)

`docs/` to jedyny katalog serwowany przez GitHub Pages i jedyne miejsce, gdzie `.ics`-y trafiają do gita — musi zawierać kopie `competitions.json`, `calendars/*.ics` (w `docs/calendars/`) oraz `index.html` (kopia `map.html`). Workflow (`.github/workflows/update_map.yml`) kopiuje te pliki po scrapowaniu — **jeśli edytujesz `map.html` ręcznie, pamiętaj też o `docs/index.html`** (oba muszą pozostać identyczne; workflow tego automatycznie nie robi dla `index.html`, tylko dla danych).

Lokalny katalog `calendars/` w korzeniu repo jest w `.gitignore` — to tylko robocze wyjście `fetch_competitions.py` przed skopiowaniem do `docs/calendars/` przez workflow, nigdy nie jest commitowany (żeby nie dryfował niezależnie od tego, co faktycznie jest publikowane).

### Frontend (`map.html` / `docs/index.html`)

Jeden plik HTML z inline CSS/JS, biblioteka mapowa: Leaflet 1.7.1 z CDN (`unpkg.com`). Przy starcie robi `fetch('competitions.json')`, buduje checkboxy klubów i markery na mapie, filtruje po klubie i zakresie dat (predefiniowane zakresy: najbliższy weekend, 14 dni, bieżący/następny miesiąc, cały rok). Wymaga serwowania przez HTTP (nie działa z `file://` z powodu `fetch`).

### Automatyzacja (`.github/workflows/update_map.yml`)

Cron codziennie o 3:00 UTC + `workflow_dispatch`. Kroki: `fetch_competitions.py` -> `verify_locations.py` -> kopiowanie do `docs/` -> auto-commit (`stefanzweifel/git-auto-commit-action`) z komunikatem "Automated competition map update" na branch `main`. To źródło większości commitów w historii repo.

## Uwagi przy edycji

- `locations.csv` jest częściowo ręcznie kuratorowany (współrzędne) — nie nadpisuj go bezmyślnie, scraper dopisuje tylko nowe lokalizacje, nie usuwa istniejących wpisów.
- Zmiany w logice parsowania HTML w `fetch_competitions.py` warto weryfikować względem aktualnej struktury `https://portal.wzss.pl/competitions/current`, bo selektory bazują na konkretnych klasach Tailwind, które mogą się zmienić bez ostrzeżenia.
- `competitions.json` i pliki `.ics` w katalogu głównym oraz w `docs/` to wygenerowane artefakty — zwykle nie edytuje się ich ręcznie, tylko przez ponowne uruchomienie `fetch_competitions.py`.
