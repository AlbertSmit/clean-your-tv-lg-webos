# Clean Your TV — Benutzeranleitung

No-root und Root sind gleichwertige Optionen für unterschiedliche TV-Konfigurationen. Wählen Sie No-root für LG Developer Mode oder Root für vorhandenen Root-Zugriff per SSH. Kompatibilität und Testumfang hängen von der jeweiligen Edition ab.

## Voraussetzungen

Diese Anleitung behandelt Installation, Bedienung und Wiederherstellung. Sprachauswahl und Desktop-App für macOS/Linux sind in [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3) enthalten. Ältere Downloads von v0.9.0 enthalten die Desktop-App nicht. Siehe die [gemeinsame Installationsanleitung](../INSTALL.md) für beide Editionen.

Fernseher einschalten und mit demselben vertrauenswürdigen Heimnetz wie den Computer verbinden. Danach muss der Computer nicht eingeschaltet bleiben. Die Kompatibilität hängt von Modell, Firmware und Fernbedienung ab; für Root stehen noch Gerätetests aus.

- **No-root:** LG Developer Mode und Key Server einschalten. Die am Fernseher angezeigte Passphrase eingeben und die separate Kopplungsanfrage am Fernseher bestätigen. Developer Mode muss aktiv bleiben: Bei Ablauf können nachinstallierte Apps entfernt werden. Den offiziellen Timer auch mit aktivierter Beta-Verlängerung kontrollieren. Die Überwachung durch Helper benötigt das lokale Netzwerk.

Der aktualisierte No-root Helper benötigt Node.js 0.12.2 oder neuer auf dem TV. Der Installer prüft die TV-Laufzeit vor der Installation. Ältere veröffentlichte Pakete erhalten diese Kompatibilität nicht automatisch; Eingabegeräte, Standby und Kaltstart müssen je Modell getestet werden.

- **Root:** Bereits vorhandener Root-Zugang über SSH ist nötig. Der Installer richtet keinen Root-Zugang ein. Developer Mode nicht auf einem bereits gerooteten Fernseher aktivieren. Root-Zugang und Wiederherstellungsdienste verfügbar halten.

## Installation und Sprache

- **Windows x64:** `cytv-windows-x64-desktop.zip` herunterladen, im Explorer **Alle extrahieren** wählen und `cytv-desktop/cytv-desktop.exe` öffnen. Den Ordner `_internal` daneben behalten. Eine Windows-Herausgebersignatur ist nicht eingerichtet. Die separate Konsole heißt `cytv-windows-x64.exe`; für die folgenden PowerShell-Befehle in `cytv.exe` umbenennen und `.\cytv.exe` verwenden.
- **macOS 13+:** `cytv-macos-arm64.zip` für Apple Silicon oder `cytv-macos-x64.zip` für Intel entpacken. `cytv.app` nach Programme verschieben und öffnen; Zugriff auf das lokale Netzwerk erlauben. Bei einer Sperre für einen vertrauenswürdigen Projekt-Download Datenschutz & Sicherheit → Dennoch öffnen verwenden. Gatekeeper nicht abschalten. Ältere Systeme sind nicht abschließend geprüft.
- **Linux x64:** Unter Ubuntu 22.04+, Debian 12+ oder Mint 21+ `cytv-linux-x64.deb` mit der grafischen Paketverwaltung installieren, dann Clean Your TV im Anwendungsmenü öffnen. Für Bibliotheken kann Internet nötig sein. Linux ARM wird nicht angeboten. Die eigenständige Datei `cytv-linux-x64` ist die CLI; für die grafische App das `.deb` verwenden.

[Android-Installer](../../android/README.md): Alle zehn Oberflächensprachen sind verfügbar. Oben rechts steht die aktuelle Sprache; antippen, um eine andere zu wählen. Die Auswahl wird auf dem Smartphone gespeichert.

Unter Android bleibt die gewählte Wartungsaktion beim Verbinden sichtbar und zeigt ihren eigenen Fortschritt. Die Oberfläche nutzt die Systemschrift des Smartphones mit größeren Beschriftungen und Hilfetexten.

Der Desktop-Assistent verwendet zunächst die Systemsprache und speichert eine ausdrückliche Auswahl. Am Fernseher unter **Einstellungen → Sprache** die gewünschte Sprache oder die automatische Systemauswahl wählen. Die Spracheinstellungen von Installer und Fernseher sind unabhängig. Alle Sprachcodes stehen im [Sprachverzeichnis](../LANGUAGES.md).

Für die separat heruntergeladene CLI unter macOS/Linux im entpackten Verzeichnis:

```sh
chmod +x cytv
./cytv --language de install
```

Fernseher oder IP-Adresse und Edition auswählen, dann die Zusammenfassung prüfen. Einer neuen SSH-Identität nur für den eigenen Fernseher im vertrauenswürdigen Netz zustimmen; ein geänderter gespeicherter Schlüssel blockiert den Zugang. Root aktiviert Home nach Einrichtung der Wiederherstellung sofort, ohne Testphase oder Behalten-Schritt. Pfeile, OK, Home, Zurück/Abbrechen, Lautstärke, Bereitschaft und Kaltstart am eigenen Fernseher testen.

Bei unterbrochener Root-Entfernung erneut Entfernen in der App wählen. Sie prüft das TV-Journal und den Paketzustand vor dem Fortsetzen; abgeschlossene Entfernung wird nicht erneut gesendet. Läuft der Vorgang noch, eine Minute warten. Bei unklarem Ergebnis den TV neu starten und erneut prüfen; Diagnosebericht für den Support behalten.

## Bedienung und Wiederherstellung

Pfeile wählen eine Kachel, OK öffnet sie; OK gedrückt halten zum Verschieben. Kurzes Zurück behält Navigation und Beendigungsdialog der App bei. Kurzes Home öffnet bei aktiver Home-Steuerung den Launcher. In neuen Builds öffnet 1,2 Sekunden langes Drücken von Zurück LG Home einmalig. Der Home-Schalter und Ihre Einstellungen bleiben unverändert.

**Neue Builds: Home innerhalb von zwei Sekunden dreimal kurz drücken**, dazwischen loslassen. Dies stellt LG Home wieder her und stoppt die Steuerung, ohne Einstellungen zurückzusetzen. Beim älteren No-root Helper bis einschließlich 0.6.13 stattdessen Home etwa zwei Sekunden halten. Langes Home ist nicht die Root-Notfallgeste.

No-root: **Home Helper** in der LG-App-Liste öffnen, um fortzufahren; Home allein hebt den Stopp nicht auf. Root: **Home ändern** in den Home-Einstellungen einschalten, um fortzufahren. **LG Home öffnen** öffnet LG Home einmalig, ohne das Home-Ziel zu ändern. Für LG Home als dauerhaftes Ziel **Home ändern** ausschalten oder `cytv restore` ausführen. Beide Steuerungen nie gleichzeitig betreiben. Bei wiederholtem Fehler LG Home aktiv lassen.

```sh
./cytv --language de status
./cytv --language de doctor --report
./cytv --language de restore
./cytv --language de uninstall
```

Nach einer Unterbrechung zuerst `status` ausführen und Protokolle behalten. `restore` stellt LG Home ohne App-Entfernung wieder her; `uninstall` stellt es vor der Entfernung wieder her. Root-Wiederherstellungsdaten bleiben absichtlich erhalten; nicht zum Erzwingen einer Neuinstallation löschen. Diagnoseberichte vor Weitergabe prüfen; Schlüssel und Profilordner nicht veröffentlichen.

## Aktualisierung und Entfernung

Funktionierende Pakete und private Sicherungen behalten. No-root Helper vor dem Ersetzen stoppen; über den Computer aktualisieren, ohne vorher zu deinstallieren, da Einstellungen verloren gehen können. Die kombinierte cytv-Root-Installation enthält den Updater unter Einstellungen → Softwareupdates für kompatible Veröffentlichungen; für manuelle Root-Pakete gelten andere Grenzen. Keine einzelne IPK über eine aktive Root-Laufzeit installieren. Für Neuinstallation den ausdrücklichen cytv-Ablauf verwenden. Die Entfernung der Desktop-App entfernt keine TV-Apps.

Technische Anleitungen auf Englisch: [Desktop](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [manuelle Installation](../MANUAL_INSTALL.md), [Wiederherstellung](../RECOVERY.md), [Editionen](../EDITIONS.md).

Nach dem Verbinden liest cytv die installierten TV-Versionen und zeigt aktuelle → mitgelieferte Version für Home und Home Helper (No-root) oder Root und Root Updater. Prüfen und bestätigen Sie die Versionen vor der Installation. Erstinstallation, Neuinstallation und ältere Versionen werden gekennzeichnet; `--yes` überspringt die Bestätigung, zeigt aber weiterhin die Versionen.

Software-Updates zeigt Versionsdetails nur für die installierte oder eine neuere Version. Unter Wiederherstellung siehst du die gespeicherte Version für die Rückkehr oder den Grund, warum sie nicht verfügbar ist; Zurück führt zu den Updates.

No-root prüft die ABI der TV-Shell und akzeptiert einen 64-Bit-Kernel mit bestätigtem ARM32-Benutzerraum. Schlägt die Prüfung fehl, hängen Sie den erzeugten Diagnosebericht an; teilen Sie keine Schlüssel oder Passphrasen.

Home-Updates erfordern eine Bestätigung vor der Installation; danach wird der Start automatisch geprüft. Die Statusabfrage im Hintergrund behält die mit der Fernbedienung gewählte Taste bei.

In Root und No-root wird die Startbereitschaft nach der Installation automatisch bestätigt; eine manuelle Bestätigung ist nicht nötig. Die Wiederherstellung bleibt danach ohne Zeitlimit bis zum nächsten Update verfügbar. Sie stellt die vorherige Home-Version und die vor dem Update gespeicherten Einstellungen wieder her; spätere Einstellungsänderungen können verloren gehen. Vor dem Start erscheint eine Warnung. Updates und Wiederherstellung von No-root direkt am Fernseher erfordern weiterhin Root und Homebrew Channel; andernfalls den Computer-Installer verwenden.

Der Update-Bildschirm trennt Versionen, Status und lesbare Neuerungen. Oben/Unten blättert durch die Änderungen, Links/Rechts wählt die festen Aktionen darunter. Nach automatischen Startprüfungen stellt Root die zuvor aktivierte Home-Steuerung wieder her; No-root erhält den Zustand des separaten Helpers. Deaktivierte Einstellungen sowie ausdrückliches oder Notfall-Ausschalten bleiben erhalten.

Beim Öffnen der Home-Einstellungen wird im Hintergrund nach Updates gesucht. Ein orangefarbener Punkt bei Softwareupdates zeigt eine neuere Version an, auch wenn sie die Einrichtung am Computer erfordert. Die Einstellungen bleiben während der Prüfung bedienbar.

No-root: Öffne Home-Einstellungen → Entwicklermodus für automatische Verlängerung, Sitzungsprüfung und Diagnose. Auf der Hauptseite bleiben der Kurzstatus und Verlängerungsfehler sichtbar. Zurück führt zu den Home-Einstellungen. Beide Editionen zeigen Sprache, Softwareupdates und TV-Einstellungen in derselben Zeile; der Pfeil öffnet den jeweiligen Eintrag.

Home Helper zeigt beim Öffnen seinen Zweck und Status. Der Start eines gestoppten Helpers muss bestätigt werden. Home Updater und Root Updater erklären die Wiederherstellung; reguläre Updates befinden sich in den Home-Einstellungen. Die Wiederherstellung wird nur bei einer gespeicherten Version angeboten und erfordert eine Bestätigung vor dem Ersetzen von Home und seinen Einstellungen.
