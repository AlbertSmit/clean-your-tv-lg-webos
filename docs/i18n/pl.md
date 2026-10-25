# Clean Your TV — instrukcja użytkownika

No-root i Root to równorzędne opcje dla różnych konfiguracji telewizora. Wybierz No-root dla LG Developer Mode lub Root, jeśli masz już dostęp root przez SSH. Zgodność i zakres wykonanych testów są określane osobno dla każdej wersji.

## Wymagania

Ta instrukcja obejmuje instalację, obsługę i odzyskiwanie. Wybór języka oraz aplikacja okienkowa macOS/Linux są dostępne w [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). Starsze pliki v0.9.0 nie zawierają aplikacji okienkowej. Zobacz [instalację obu edycji](../INSTALL.md).

Włącz telewizor i połącz go z tą samą zaufaną siecią lokalną co komputer. Później komputer może być wyłączony. Zgodność zależy od modelu, oprogramowania i pilota; Root ma nieukończone testy sprzętowe.

- **No-root:** włącz LG Developer Mode i Key Server. Wpisz hasło wyświetlane na telewizorze i zaakceptuj na nim osobne żądanie parowania. Developer Mode musi pozostać aktywny: wygaśnięcie sesji może usunąć tak zainstalowane aplikacje. Sprawdzaj oficjalny licznik także przy włączonym odnawianiu Beta. Monitorowanie Helper wymaga sieci lokalnej.

Zaktualizowany Helper No-root wymaga Node.js 0.12.2 lub nowszego na telewizorze. Instalator sprawdza ten wymóg przed instalacją. Wcześniej opublikowane pakiety nie uzyskują tej zgodności automatycznie; dostęp do urządzeń wejściowych, wybudzanie i zimny start wymagają testów na każdym modelu.

- **Root:** potrzebny jest istniejący dostęp root przez SSH. Instalator nie uzyskuje uprawnień root. Nie włączaj Developer Mode na telewizorze z istniejącym rootem. Zachowaj dostęp root i usługi odzyskiwania.

## Instalacja i język

- **Windows x64:** pobierz `cytv-windows-x64-desktop.zip`, wybierz **Wyodrębnij wszystkie** w Eksploratorze i otwórz `cytv-desktop/cytv-desktop.exe`. Zachowaj obok folder `_internal`. Podpis wydawcy Windows nie jest skonfigurowany. Osobna konsola to `cytv-windows-x64.exe`; zmień nazwę na `cytv.exe` i użyj `.\cytv.exe` w PowerShell dla poniższych poleceń.
- **macOS 13+:** rozpakuj `cytv-macos-arm64.zip` dla Apple Silicon lub `cytv-macos-x64.zip` dla Intela. Przenieś `cytv.app` do Aplikacji i otwórz; zezwól na dostęp do sieci lokalnej. Jeśli zaufany plik zostanie zablokowany, użyj Prywatność i ochrona → Otwórz mimo to; nie wyłączaj Gatekeepera. Zgodność ze starszymi systemami nie jest w pełni potwierdzona.
- **Linux x64:** na Ubuntu 22.04+, Debianie 12+ lub Mint 21+ zainstaluj `cytv-linux-x64.deb` przez graficzny menedżer pakietów i otwórz Clean Your TV z menu. Pobranie bibliotek może wymagać Internetu. Nie ma pakietu Linux ARM. Samodzielny plik `cytv-linux-x64` to CLI; aplikacja graficzna jest w pakiecie `.deb`.

[Instalator Android](../../android/README.md) obsługuje wszystkie dziesięć języków interfejsu. W prawym górnym rogu widać bieżący język; dotknij go, aby wybrać inny. Wybór zostaje zapisany w telefonie.

W Androidzie wybrane działanie serwisowe pozostaje widoczne podczas łączenia i pokazuje własny postęp. Interfejs używa czcionki systemowej telefonu oraz większych etykiet i tekstów pomocy.

Kreator początkowo używa języka systemu i zapamiętuje wybrany język. Na telewizorze otwórz **Ustawienia → Język** i wybierz język lub automatyczny wybór według systemu. Preferencje instalatora i telewizora są niezależne. Kody zawiera [spis języków](../LANGUAGES.md).

Dla osobno pobranej CLI na macOS/Linux, w rozpakowanym katalogu:

```sh
chmod +x cytv
./cytv --language pl install
```

Wybierz telewizor lub podaj IP, wybierz edycję i sprawdź podsumowanie. Nową tożsamość SSH zatwierdzaj tylko dla własnego telewizora w zaufanej sieci; zmieniony zapisany klucz blokuje dostęp. Root przygotowuje odzyskiwanie i od razu aktywuje Home, bez okresu próbnego ani potwierdzenia zachowania ustawień. Sprawdź strzałki, OK, Home, Wstecz/Anuluj, głośność, czuwanie i uruchomienie po całkowitym odłączeniu zasilania.

Jeśli usuwanie Root zostanie przerwane, ponownie wybierz Usuń w aplikacji. Sprawdzi dziennik TV i stan pakietów przed kontynuowaniem; nie ponowi zakończonego usuwania. Jeśli operacja trwa, odczekaj minutę. Jeśli wyniku nie można potwierdzić, uruchom TV ponownie i sprawdź stan; zachowaj raport dla pomocy technicznej.

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

Po połączeniu cytv odczytuje wersje na telewizorze i pokazuje obecną → dołączoną wersję dla Home i Home Helper (No-root) albo Root i Root Updater. Sprawdź i potwierdź przed instalacją. Pierwsza instalacja, ponowna instalacja i instalacja starszej wersji są oznaczone osobno; `--yes` pomija potwierdzenie, ale wyświetla wersje.

Aktualizacje oprogramowania pokazują szczegóły tylko zainstalowanej lub nowszej wersji. Otwórz Odzyskiwanie, aby zobaczyć zapisaną wersję do przywrócenia lub powód niedostępności; Wstecz wraca do aktualizacji.

No-root sprawdza ABI powłoki TV i akceptuje jądro 64-bitowe ze zweryfikowanym środowiskiem ARM32. Jeśli weryfikacja się nie powiedzie, dołącz wygenerowany raport JSON; nie udostępniaj kluczy ani haseł.

Aktualizacje Home wymagają potwierdzenia przed instalacją; później uruchomienie jest sprawdzane automatycznie. Odświeżanie stanu zachowuje przycisk wybrany pilotem.

W Root i No-root gotowość po instalacji jest potwierdzana automatycznie; nie musisz potwierdzać, że wszystko działa. Przywracanie pozostaje dostępne po potwierdzeniu, bez limitu czasu, aż do następnej aktualizacji. Przywraca poprzednią wersję Home i ustawienia zapisane przed aktualizacją; późniejsze zmiany ustawień mogą zostać utracone. Przed rozpoczęciem pojawia się ostrzeżenie. Aktualizacja i przywracanie No-root z telewizora nadal wymagają roota i Homebrew Channel; w przeciwnym razie użyj instalatora na komputerze.

Ekran aktualizacji rozdziela wersje, stan i czytelne informacje o zmianach. Góra/Dół przewija informacje; Lewo/Prawo wybiera stałe działania poniżej. Po automatycznych testach uruchomienia Root przywraca wcześniej włączone sterowanie Home; No-root zachowuje stan oddzielnego Helpera. Wyłączone ustawienie oraz jawne lub awaryjne wyłączenie pozostają wyłączone.

Otwarcie ustawień Home uruchamia sprawdzanie aktualizacji w tle. Pomarańczowa kropka przy Aktualizacje oprogramowania oznacza nowszą wersję, również gdy wymaga instalacji z komputera. Ustawienia pozostają dostępne podczas sprawdzania.

No-root: otwórz Ustawienia Home → Tryb dewelopera, aby uzyskać dostęp do automatycznego odnawiania, sprawdzania sesji i diagnostyki. Główny ekran nadal pokazuje krótki stan i błędy odnawiania. Wstecz wraca do ustawień Home. Obie edycje umieszczają Język, Aktualizacje oprogramowania i Ustawienia TV w tym samym wierszu; strzałka otwiera daną pozycję.

Po otwarciu Home Helper pokazuje swoje przeznaczenie i stan. Uruchomienie zatrzymanego Helpera wymaga potwierdzenia. Home Updater i Root Updater wyjaśniają przywracanie; zwykłe aktualizacje są w ustawieniach Home. Przywracanie jest dostępne tylko dla zapisanej wersji i wymaga potwierdzenia przed zastąpieniem Home i jego ustawień.
