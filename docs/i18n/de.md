# Clean Your TV — Benutzeranleitung

## Voraussetzungen

Diese Anleitung behandelt Installation, Bedienung und Wiederherstellung. Sprachauswahl und Desktop-App für macOS/Linux sind in [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3) enthalten. Ältere Downloads von v0.9.0 enthalten die Desktop-App nicht. Siehe die [gemeinsame Installationsanleitung](../INSTALL.md) für beide Editionen.

Fernseher einschalten und mit demselben vertrauenswürdigen Heimnetz wie den Computer verbinden. Danach muss der Computer nicht eingeschaltet bleiben. Die Kompatibilität hängt von Modell, Firmware und Fernbedienung ab; Root ist weiterhin eine Vorschau mit offenen Gerätetests.

- **No-root:** LG Developer Mode und Key Server einschalten. Die am Fernseher angezeigte Passphrase eingeben und die separate Kopplungsanfrage am Fernseher bestätigen. Developer Mode muss aktiv bleiben: Bei Ablauf können nachinstallierte Apps entfernt werden. Den offiziellen Timer auch mit aktivierter Beta-Verlängerung kontrollieren. Die Überwachung durch Helper benötigt das lokale Netzwerk.
- **Root:** Bereits vorhandener Root-Zugang über SSH ist nötig. Der Installer richtet keinen Root-Zugang ein. Developer Mode nicht auf einem bereits gerooteten Fernseher aktivieren. Root-Zugang und Wiederherstellungsdienste verfügbar halten.

## Installation und Sprache

- **Windows x64:** Konsolenpaket entpacken und `cytv.exe` öffnen. In PowerShell unten `./cytv` durch `.\cytv.exe` ersetzen. Eine grafische Windows-Version ist nicht enthalten.
- **macOS 13+:** `cytv-macos-arm64.zip` für Apple Silicon oder `cytv-macos-x64.zip` für Intel entpacken. `cytv.app` nach Programme verschieben und öffnen; Zugriff auf das lokale Netzwerk erlauben. Bei einer Sperre für einen vertrauenswürdigen Projekt-Download Datenschutz & Sicherheit → Dennoch öffnen verwenden. Gatekeeper nicht abschalten. Ältere Systeme sind nicht abschließend geprüft.
- **Linux x64:** Unter Ubuntu 22.04+, Debian 12+ oder Mint 21+ `cytv-linux-x64.deb` mit der grafischen Paketverwaltung installieren, dann Clean Your TV im Anwendungsmenü öffnen. Für Bibliotheken kann Internet nötig sein. Linux ARM wird nicht angeboten.

Der Desktop-Assistent verwendet zunächst die Systemsprache und speichert eine ausdrückliche Auswahl. Am Fernseher unter **Einstellungen → Sprache** die gewünschte Sprache oder die automatische Systemauswahl wählen. Die Spracheinstellungen von Installer und Fernseher sind unabhängig. Alle Sprachcodes stehen im [Sprachverzeichnis](../LANGUAGES.md).

Für die separat heruntergeladene CLI unter macOS/Linux im entpackten Verzeichnis:

```sh
chmod +x cytv
./cytv --language de install
```

Fernseher oder IP-Adresse und Edition auswählen, dann die Zusammenfassung prüfen. Einer neuen SSH-Identität nur für den eigenen Fernseher im vertrauenswürdigen Netz zustimmen; ein geänderter gespeicherter Schlüssel blockiert den Zugang. Root aktiviert Home nach Einrichtung der Wiederherstellung sofort, ohne Testphase oder Behalten-Schritt. Pfeile, OK, Home, Zurück/Abbrechen, Lautstärke, Bereitschaft und Kaltstart am eigenen Fernseher testen.

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
