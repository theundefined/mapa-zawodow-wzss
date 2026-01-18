# 🎯 Mapa Zawodów WZSS (Nieoficjalna)

![Status Aktualizacji](https://github.com/theundefined/mapa-zawodow-wzss/actions/workflows/update_map.yml/badge.svg)

Interaktywna mapa, lista i kalendarz zawodów strzeleckich organizowanych w ramach Wielkopolskiego Związku Strzelectwa Sportowego.

👉 **Zobacz mapę na żywo:** [https://theundefined.github.io/mapa-zawodow-wzss/](https://theundefined.github.io/mapa-zawodow-wzss/)

---

## ℹ️ O projekcie

Strona powstała z prozaicznej przyczyny – dla własnej wygody. Przeglądanie wielu regulaminów i stron klubowych bywa czasochłonne, a wizualizacja na mapie pozwala błyskawicznie ocenić, gdzie warto wybrać się w najbliższy weekend.

Jest to **projekt nieoficjalny**, stworzony hobbystycznie, aby ułatwić życie strzelcom z Wielkopolski.

> 🤖 **Nota autorska:** Projekt ten jest dowodem na to, że chęć optymalizacji czasu (nazywana czasem "konstruktywnym lenistwem") w połączeniu z nowoczesnymi asystentami AI potrafi dać wymierne rezultaty. Kod, logika oraz automatyzacja tego narzędzia powstały przy ścisłej współpracy z AI.

## 🚀 Główne funkcjonalności

*   **🗺️ Interaktywna Mapa:** Szybki podgląd lokalizacji zawodów w regionie.
*   **🔍 Filtrowanie:** Wybieraj interesujące Cię kluby oraz zakres dat (najbliższy weekend, miesiąc, rok).
*   **📅 Integracja z Kalendarzem:** 
    *   Możliwość pobrania pliku `.ics` dla wybranego klubu.
    *   **Subskrypcja:** Skopiuj link i wklej go do Kalendarza Google lub Outlook. Gdy klub ogłosi nowe zawody, Twój prywatny kalendarz zaktualizuje się automatycznie!
*   **📱 Responsywność:** Działa wygodnie zarówno na komputerze, jak i na telefonie.

## ⚙️ Jak to działa (Automatyzacja)

Całość działa bezobsługowo w oparciu o **GitHub Actions**:
1.  Codziennie w nocy skrypt Python pobiera ogólnodostępne dane z portalu WZSS.
2.  Dane są przetwarzane, a na ich podstawie generowane są pliki `JSON` dla mapy oraz `ICS` dla kalendarzy.
3.  Zaktualizowana strona jest automatycznie publikowana na GitHub Pages.

## 🤝 Feedback

Mimo że projekt powstał głównie na użytek własny, **sugestie i uwagi są mile widziane!** 
Jeśli widzisz błąd, masz pomysł na nową funkcję lub po prostu chcesz dać znać, że narzędzie się przydaje – śmiało korzystaj z zakładki [Issues](https://github.com/theundefined/mapa-zawodow-wzss/issues).
