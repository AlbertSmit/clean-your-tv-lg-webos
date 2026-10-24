# CYTV Android

Approved direction: self-contained Android installer for No-root and Root, with a polished UI and screenshots of the actual interface. Technical documents are English; the initial app UI is Russian/English.

## Architecture

Kotlin Activity hosts bundled HTML/CSS/JS in an offline WebView. A foreground service runs the existing Python CLI through Chaquopy 17.1 / Python 3.12, with structured events and blocking user prompts. No HTTP server, remote web content, shell runtime or Termux is needed. Existing Installer, SSH pinning, payload verification, journals and recovery flows remain authoritative. A new optional CLI payload path lets Android supply its private extracted asset directory without changing desktop defaults.

Android 7+ (API 24); arm64-v8a (64-bit ARM). APK includes the public TV payload from the verified public payload directory. Debug builds are explicitly prerelease. No claim of TV compatibility without hardware testing.

## UX

Cinema-inspired graphite/ink surfaces, ice-blue primary action, muted jade success, warm white text. Existing local Noto Sans supports Cyrillic. Distinct television illustration, spacious edition selection, visible form labels, 48px targets, inline validation, focus rings, reduced motion, scalable text and responsive safe-area spacing. Welcome, connection, operation, prompt, result and recovery states share the same local UI assets as the browser preview.

Manual IP entry and editable SSH port; No-root Key Server passphrase is requested only when needed. Root supports password or an imported private key through Android's document picker. SSH fingerprints require explicit confirmation and changed keys remain rejected. CLI version/reinstall/recovery confirmations are presented in a scrollable dialog with the real preceding context. No automatic approval. Status and restore are available for both editions; destructive uninstall is excluded from the first UI.

## Lifecycle and privacy

One operation per process, with a foreground notification and bounded wake lock. Rotation/recreation replays current log and pending prompt; process death relies on durable CYTV receipts and the next status/restore operation, never automatic install replay. Secrets are not put in event logs or configuration. Imported keys and profiles stay in app-private storage, excluded from backup. Only bundled assets can load in the WebView; network and external navigation are blocked there. Python alone communicates with TV endpoints. Raw logs are local and not exported automatically.

## Validation

Unit tests for request validation, explicit trust, secret separation, operation serialization and CLI payload injection. Browser tests for both editions, forms, native bridge events, dialogs, recovery, narrow screens and screenshot capture. Build APK, inspect manifest/ZIP and run emulator smoke tests if emulator support is available. Run the repository test script and report pre-existing failures separately. No unattended changes to a real TV.

## Dependency decision during build

The official Chaquopy index has bcrypt 3.1.7 for Python 3.11, below Paramiko 3.5.1's minimum. Python 3.12 has bcrypt 3.2.2 and compatible cryptography/PyNaCl wheels, so the initial APK targets 64-bit ARM phones. No dependency constraints are bypassed. TV ARM32 payloads are independent of the phone ABI.
