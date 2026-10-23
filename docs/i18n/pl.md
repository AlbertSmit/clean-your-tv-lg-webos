# Clean Your TV — instrukcja użytkownika

## Wymagania

Ta instrukcja obejmuje instalację, obsługę i odzyskiwanie. Wybór języka oraz aplikacja okienkowa macOS/Linux dotyczą następnej kompilacji lub źródeł zawierających tę zmianę. Dotychczasowe pliki v0.9.0 nie zawierają nowej aplikacji okienkowej. Pobierz odpowiednie [wydanie projektu](https://github.com/Razdva122/clean-your-tv-lg-webos/releases), gdy zostanie opublikowane, albo wynik udanego przebiegu **cytv standalone builds** z tą zmianą.

Włącz telewizor i połącz go z tą samą zaufaną siecią lokalną co komputer. Później komputer może być wyłączony. Zgodność zależy od modelu, oprogramowania i pilota; Root pozostaje wersją przedpremierową z nieukończonymi testami sprzętowymi.

- **No-root:** włącz LG Developer Mode i Key Server. Wpisz hasło wyświetlane na telewizorze i zaakceptuj na nim osobne żądanie parowania. Developer Mode musi pozostać aktywny: wygaśnięcie sesji może usunąć tak zainstalowane aplikacje. Sprawdzaj oficjalny licznik także przy włączonym odnawianiu Beta. Monitorowanie Helper wymaga sieci lokalnej.
- **Root:** potrzebny jest istniejący dostęp root przez SSH. Instalator nie uzyskuje uprawnień root. Nie włączaj Developer Mode na telewizorze z istniejącym rootem. Zachowaj dostęp root i usługi odzyskiwania.

## Instalacja i język

- **Windows x64:** rozpakuj pakiet konsolowy i otwórz `cytv.exe`. W PowerShell zamień `./cytv` na `.\cytv.exe` w poniższych poleceniach. Nie dołączono aplikacji okienkowej dla Windows.
- **macOS 13+:** rozpakuj `cytv-macos-arm64.zip` dla Apple Silicon lub `cytv-macos-x64.zip` dla Intela. Przenieś `cytv.app` do Aplikacji i otwórz; zezwól na dostęp do sieci lokalnej. Jeśli zaufany plik zostanie zablokowany, użyj Prywatność i ochrona → Otwórz mimo to; nie wyłączaj Gatekeepera. Zgodność ze starszymi systemami nie jest w pełni potwierdzona.
- **Linux x64:** na Ubuntu 22.04+, Debianie 12+ lub Mint 21+ zainstaluj `cytv-linux-x64.deb` przez graficzny menedżer pakietów i otwórz Clean Your TV z menu. Pobranie bibliotek może wymagać Internetu. Nie ma pakietu Linux ARM.

Kreator początkowo używa języka systemu i zapamiętuje wybrany język. Na telewizorze otwórz **Ustawienia → Język** i wybierz język lub automatyczny wybór według systemu. Preferencje instalatora i telewizora są niezależne. Kody zawiera [spis języków](../LANGUAGES.md).

Dla osobno pobranej CLI na macOS/Linux, w rozpakowanym katalogu:

```sh
chmod +x cytv
./cytv --language pl install
```

Wybierz telewizor lub podaj IP, wybierz edycję i sprawdź podsumowanie. Nową tożsamość SSH zatwierdzaj tylko dla własnego telewizora w zaufanej sieci; zmieniony zapisany klucz blokuje dostęp. Root przygotowuje odzyskiwanie i od razu aktywuje Home, bez okresu próbnego ani potwierdzenia zachowania ustawień. Sprawdź strzałki, OK, Home, Wstecz/Anuluj, głośność, czuwanie i uruchomienie po całkowitym odłączeniu zasilania.

## Obsługa i odzyskiwanie

Strzałki wybierają, OK otwiera; przytrzymaj OK, aby zmienić kolejność. Krótkie Wstecz zachowuje nawigację aplikacji i jej potwierdzenie wyjścia. Home otwiera ekran Clean Your TV, gdy sterowanie jest aktywne. W nowych kompilacjach przytrzymaj Wstecz przez 1,2 sekundy, aby jednorazowo otworzyć LG Home. Przełącznik sterowania Home i ustawienia pozostają bez zmian.

**Nowe kompilacje: naciśnij Home trzy razy w ciągu dwóch sekund**, puszczając przycisk po każdym naciśnięciu. Przywraca to LG Home i zatrzymuje sterowanie bez usuwania preferencji. W No-root Helper do wersji 0.6.13 włącznie zamiast tego przytrzymaj Home około dwóch sekund. Przytrzymanie Home nie jest gestem awaryjnym Root.

No-root: otwórz **Home Helper** z listy aplikacji LG, aby wznowić; samo Home nie znosi blokady. Root: włącz **Zmień Home** w ustawieniach Home, aby wznowić. **Otwórz LG Home** otwiera LG Home jednorazowo bez zmiany celu przycisku Home. Aby przywrócić LG Home jako stały cel, wyłącz **Zmień Home** lub uruchom `cytv restore`. Nie uruchamiaj obu kontrolerów jednocześnie. Przy powtarzającym się błędzie pozostań przy LG Home.

```sh
./cytv --language pl status
./cytv --language pl doctor --report
./cytv --language pl restore
./cytv --language pl uninstall
```

Po przerwaniu operacji najpierw uruchom `status` i zachowaj dzienniki. `restore` przywraca LG Home bez usuwania aplikacji; `uninstall` przywraca je przed usunięciem. Dane odzyskiwania Root pozostają celowo: nie kasuj ich, by wymusić ponowną instalację. Sprawdź raporty przed udostępnieniem; nie publikuj kluczy ani katalogów profili.

## Aktualizacja i usuwanie

Zachowaj działające pakiety i prywatne kopie ustawień. Zatrzymaj No-root Helper przed wymianą pakietów i aktualizuj z komputera bez wcześniejszego odinstalowania, które może usunąć ustawienia. Łączna instalacja Root przez cytv zawiera aktualizator zgodnych wydań w Ustawienia → Aktualizacje oprogramowania; instalacja ręczna ma inne ograniczenia. Nie nadpisuj działającego środowiska Root pojedynczą IPK. Do ponownej instalacji używaj wyraźnie zatwierdzanej procedury cytv. Usunięcie aplikacji komputerowej nie usuwa aplikacji TV.

Dokumentacja techniczna po angielsku: [aplikacja komputerowa](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [instalacja ręczna](../MANUAL_INSTALL.md), [odzyskiwanie](../RECOVERY.md), [edycje](../EDITIONS.md).
