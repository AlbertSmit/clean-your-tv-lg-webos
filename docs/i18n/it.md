# Clean Your TV — guida all’uso

No-root e Root sono opzioni equivalenti per diverse configurazioni della TV. Scegli No-root per LG Developer Mode oppure Root se disponi già di accesso root tramite SSH. Compatibilità e verifiche eseguite sono specifiche di ogni edizione.

## Requisiti

Questa guida tratta installazione, utilizzo e ripristino. La scelta della lingua e l’app desktop per macOS/Linux sono incluse in [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). I vecchi download della v0.9.0 non contengono l’app grafica. Consulta la [guida d’installazione per entrambe le edizioni](../INSTALL.md).

Accendi il televisore e collegalo alla stessa rete locale affidabile del computer. Dopo l’installazione il computer può restare spento. La compatibilità dipende da modello, firmware e telecomando; Root ha ancora verifiche hardware da completare.

- **No-root:** attiva LG Developer Mode e Key Server. Inserisci la frase di accesso mostrata sul televisore e accetta sullo schermo la richiesta separata di abbinamento. Developer Mode deve restare attivo: alla scadenza le app installate in questo modo possono essere rimosse. Controlla il timer ufficiale anche con rinnovo Beta attivo. Il monitoraggio di Helper richiede la rete locale.
- **Root:** serve un accesso SSH root già disponibile. L’installer non ottiene i privilegi root. Non attivare Developer Mode su una configurazione già dotata di root. Mantieni disponibili accesso root e servizi di ripristino.

## Installazione e lingua

- **Windows x64:** scarica `cytv-windows-x64-desktop.zip`, scegli **Estrai tutto** in Esplora file e apri `cytv-desktop/cytv-desktop.exe`. Mantieni la cartella `_internal` accanto al file. La firma dell’editore Windows non è configurata. La console separata è `cytv-windows-x64.exe`; rinominala in `cytv.exe` e usa `.\cytv.exe` in PowerShell per i comandi seguenti.
- **macOS 13+:** estrai `cytv-macos-arm64.zip` per Apple Silicon oppure `cytv-macos-x64.zip` per Intel, sposta `cytv.app` in Applicazioni e aprila. Consenti l’accesso alla rete locale. Se un download affidabile viene bloccato, usa Privacy e sicurezza → Apri comunque; non disattivare Gatekeeper. La verifica sui sistemi meno recenti non è conclusa.
- **Linux x64:** su Ubuntu 22.04+, Debian 12+ o Mint 21+, installa `cytv-linux-x64.deb` con il gestore grafico dei pacchetti e apri Clean Your TV dal menu. Le librerie possono richiedere Internet. Linux ARM non è incluso. L’eseguibile autonomo `cytv-linux-x64` è la CLI; usa il `.deb` per l’app grafica.

[Installer Android](../../android/README.md): sono disponibili tutte e dieci le lingue. Il pulsante in alto a destra mostra la lingua attuale; toccalo per sceglierne un’altra. La scelta viene salvata sul telefono.

Su Android, l’azione di manutenzione scelta resta visibile durante la connessione e mostra il proprio avanzamento. L’interfaccia usa il carattere di sistema del telefono con etichette e testi di aiuto più grandi.

L’assistente usa inizialmente la lingua del sistema e salva una scelta esplicita. Sul televisore, apri **Impostazioni → Lingua** e scegli una lingua oppure l’opzione automatica del sistema. Le preferenze del televisore e dell’installer sono separate. I codici sono nell’[indice delle lingue](../LANGUAGES.md).

Per la CLI scaricata separatamente su macOS/Linux, dalla cartella estratta:

```sh
chmod +x cytv
./cytv --language it install
```

Scegli il televisore o inserisci l’IP, seleziona l’edizione e controlla il riepilogo. Accetta una nuova identità SSH solo per il tuo televisore su una rete affidabile; una chiave salvata cambiata blocca l’accesso. Root prepara il ripristino e attiva subito Home, senza prova temporanea né passaggio per confermare il mantenimento. Verifica frecce, OK, Home, Indietro/Annulla, volume, standby e avvio a freddo.

## Uso e ripristino

Le frecce selezionano, OK apre; tieni premuto OK per riordinare. Un breve Indietro conserva navigazione e conferma di uscita dell’app. Home apre il launcher quando il controllo è attivo. Nelle nuove compilazioni, tieni premuto Indietro per 1,2 secondi per aprire LG Home una volta. L’interruttore del controllo Home e le impostazioni restano invariati.

**Nuove compilazioni: premi Home tre volte entro due secondi**, rilasciandolo tra le pressioni. Ripristina LG Home e interrompe il controllo senza cancellare le preferenze. Con No-root Helper fino alla 0.6.13 inclusa, tieni invece premuto Home per circa due secondi. La pressione prolungata di Home non è il gesto di emergenza di Root.

No-root: apri **Home Helper** dalle app LG per riprendere; aprire solo Home non annulla l’arresto. Root: attiva **Cambia Home** nelle impostazioni Home per riprendere. **Apri LG Home** apre LG Home una volta senza cambiare la destinazione di Home. Per ripristinare LG Home come destinazione permanente, disattiva **Cambia Home** o esegui `cytv restore`. Non eseguire entrambi i controllori insieme. Se il problema ricompare, lascia attivo LG Home.

```sh
./cytv --language it status
./cytv --language it doctor --report
./cytv --language it restore
./cytv --language it uninstall
```

Dopo un’interruzione, esegui prima `status` e conserva i registri. `restore` ripristina LG Home senza rimuovere app; `uninstall` lo ripristina prima della rimozione. I dati di ripristino Root restano intenzionalmente: non cancellarli per forzare una reinstallazione. Controlla i rapporti prima di condividerli; non pubblicare chiavi o cartelle dei profili.

## Aggiornamenti e rimozione

Conserva pacchetti funzionanti e copie private delle impostazioni. Ferma No-root Helper prima di sostituire i pacchetti; aggiorna dal computer senza disinstallare prima, perché potresti perdere preferenze. L’installazione Root combinata di cytv include gli aggiornamenti compatibili in Impostazioni → Aggiornamenti software; l’installazione manuale ha limiti diversi. Non installare una singola IPK sopra un ambiente Root attivo. Usa la procedura esplicita di reinstallazione cytv. Rimuovere l’app desktop non rimuove le app TV.

Documentazione tecnica in inglese: [desktop](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [installazione manuale](../MANUAL_INSTALL.md), [ripristino](../RECOVERY.md), [edizioni](../EDITIONS.md).

Dopo la connessione, cytv legge le versioni sulla TV e mostra la versione attuale → inclusa per Home e Home Helper (No-root), oppure Root e Root Updater. Controlla e conferma prima di installare. Prima installazione, reinstallazione e passaggio a una versione precedente sono indicati separatamente; `--yes` salta la conferma ma mostra le versioni.

Aggiornamenti software mostra i dettagli solo della versione installata o più recente. Apri Ripristino per vedere la versione salvata da ripristinare o il motivo per cui non è disponibile; Indietro torna agli aggiornamenti.

No-root verifica l’ABI della shell TV e accetta un kernel a 64 bit con ambiente ARM32 confermato. Se la verifica fallisce, allega il JSON diagnostico generato; non condividere chiavi o passphrase.

Gli aggiornamenti di Home richiedono conferma prima dell’installazione; poi l’avvio viene verificato automaticamente. Il controllo dello stato mantiene il pulsante selezionato con il telecomando.

In Root e No-root, l’avvio viene confermato automaticamente dopo l’installazione; non devi confermare che tutto funzioni. Il ripristino rimane disponibile dopo la conferma, senza limiti di tempo, fino al prossimo aggiornamento. Ripristina la versione precedente di Home e le impostazioni salvate prima dell’aggiornamento; le modifiche successive possono andare perse. Prima di avviarlo viene mostrato un avviso. Aggiornare e ripristinare No-root dalla TV richiede ancora root e Homebrew Channel; altrimenti usa il programma di installazione sul computer.

La schermata di aggiornamento separa versioni, stato e novità leggibili. Su/Giù scorre le note; Sinistra/Destra sceglie le azioni fisse in basso. Dopo i controlli automatici di avvio, Root ripristina il controllo Home se era attivo; No-root conserva lo stato del Helper separato. Le preferenze disattivate e la disattivazione esplicita o di emergenza restano disattivate.

Aprendo le impostazioni Home, gli aggiornamenti vengono cercati in background. Un punto arancione su Aggiornamenti software indica una versione più recente, anche quando richiede l’installazione dal computer. Le impostazioni restano utilizzabili durante la verifica.

No-root: apri Impostazioni Home → Modalità sviluppatore per rinnovo automatico, verifica della sessione e diagnostica. La schermata principale mantiene visibili un breve stato e gli errori di rinnovo. Indietro torna alle impostazioni Home. Entrambe le edizioni raggruppano Lingua, Aggiornamenti software e Impostazioni TV nella stessa riga; la freccia apre ogni voce.

All’apertura, Home Helper mostra il suo scopo e stato. L’avvio di un Helper arrestato richiede conferma. Home Updater e Root Updater spiegano il ripristino; gli aggiornamenti normali sono nelle impostazioni di Home. Il ripristino è proposto solo se esiste una versione salvata e richiede conferma prima di sostituire Home e le sue impostazioni.
