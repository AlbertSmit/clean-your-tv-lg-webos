# Clean Your TV — guida all’uso

1.4.0: il responsabile ha accettato i test corretti su C3 di alimentazione, Home, focus, stato disattivato e rollback manuale a 1.3.0; #90 è stato chiuso su sua richiesta. Altre TV, audio eARC e Android fisico restano non verificati. Non tutti i tasti base del candidato precedente sono stati riprovati. [1.4.0 acceptance (English)](../RELEASE-1.4.0-ACCEPTANCE.md). Earlier pending statements below are historical.


No-root e Root sono opzioni equivalenti per diverse configurazioni della TV. Scegli No-root per LG Developer Mode oppure Root se disponi già di accesso root tramite SSH. Compatibilità e verifiche eseguite sono specifiche di ogni edizione.

## Requisiti

Questa guida descrive **[v1.3.0 stabile](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)**. I collegamenti `releases/latest/download` distribuiscono la versione stabile pubblicata. Vedi [installazione](../INSTALL.md) e [note di rilascio](../RELEASE-1.3.0.md).

Versioni del rilascio: cytv **0.4.0**, Home **1.4.2**, Home Helper **0.6.19**, Root **0.4.0**, Home Updater e Root Updater **0.3.0**, Android **0.3.0-preview** (codice **11**), supervisore System Updater **1.1.0**, protocollo **1**.

Il candidato 1.4.0 non ancora pubblicato prevede Android 0.4.0 (codice 13), senza preview, dopo i test in emulatore accettati dal manutentore. Testato: Android 15 ARM64 / WebView 124. Telefoni fisici e ripristino durante una vera installazione TV non sono verificati; Android 7 / WebView 108 è un requisito minimo, non un telefono testato. Aggiornare senza disinstallare o cancellare dati. I download pubblicati restano 0.3.0-preview. Segnalare telefono, Android/WebView, TV/firmware, edizione e passaggio fallito, senza credenziali.

Problema noto della 1.3.0: dopo lo standby, il controllo Home di Root può disattivarsi e Home torna ad aprire LG. Riattivalo esplicitamente nelle impostazioni di Clean Your TV; se non riesce, mantieni LG Home e salva la diagnostica. Vedi [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90) e i [test attuali](../RELEASE-1.3.0-ACCEPTANCE.md).

Accendi il televisore e collegalo alla stessa rete locale affidabile del computer. Dopo l’installazione il computer può restare spento. La compatibilità dipende da modello, firmware e telecomando; Root ha ancora verifiche hardware da completare.

- **No-root:** attiva LG Developer Mode e Key Server. Inserisci la frase di accesso mostrata sul televisore e accetta sullo schermo la richiesta separata di abbinamento. Developer Mode deve restare attivo: alla scadenza le app installate in questo modo possono essere rimosse. Controlla il timer ufficiale anche con rinnovo Beta attivo. Il monitoraggio di Helper richiede la rete locale.

Il Helper No-root aggiornato richiede Node.js 0.12.2 o successivo sulla TV. Il programma di installazione verifica questo requisito prima di installare. I pacchetti già pubblicati non acquisiscono automaticamente questa compatibilità; accesso al telecomando, standby e avvio a freddo richiedono prove su ogni modello.

- **Root:** serve un accesso SSH root già disponibile. L’installer non ottiene i privilegi root. Non attivare Developer Mode su una configurazione già dotata di root. Mantieni disponibili accesso root e servizi di ripristino.


## Configurare Developer Mode (No-root)

Developer Mode permette a CYTV di installare app su una TV senza root.

1. Sulla TV, apri LG Apps, cerca Developer Mode e installalo.
2. Apri Developer Mode e accedi con il tuo account LG Developer. Se necessario, crea un account su webostv.developer.lge.com.
3. Attiva Dev Mode Status. La TV si riavvia. Poi apri di nuovo Developer Mode.
4. Attiva Key Server e lascia Developer Mode aperto. Inserisci il suo IP Address come indirizzo della TV in CYTV.
5. Inserisci la Passphrase: i sei caratteri mostrati in Developer Mode sulla TV. Rispetta maiuscole e minuscole.

Usa il codice della TV, non la password del tuo account LG. Se il codice non appare, attiva Key Server.

L’associazione è un passaggio separato: quando la TV lo chiede, autorizza CYTV con il telecomando.

Mantieni Developer Mode attivo: prima che scada il timer, aprilo e premi EXTEND con la TV connessa a Internet. Alla scadenza, LG può rimuovere queste app.

Home è la tua schermata delle app. Home Helper fa sì che il tasto Home la apra.

Dopo l’installazione, premi Home per provare. Se si apre LG Home, apri Home Helper dalle app della TV. Tre pressioni brevi di Home entro due secondi riportano a LG Home. Per riavviare il controllo Home, apri Home Helper, scegli Avvia Helper e conferma. La tua scelta della schermata Home viene mantenuta.

Sul computer, CYTV mostra la preparazione un passo alla volta. Dettagli apre il registro dell’operazione. Puoi ingrandire le immagini LG; usa il codice della tua TV.

[LG Developer Mode](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

## Python opzionale per Root

Root richiede Python 3.9+ sulla TV. L’installer verifica realmente moduli e operazioni necessari, inclusi `json`, `fcntl`, blocchi, file e sottoprocessi: il solo numero di versione non basta. Se l’interprete esistente è adatto, non scarica un altro Python. Altrimenti, durante la configurazione può scaricare sul computer o su Android CPython **3.13.17 per ARMv7 soft-float**, fissato per URL, dimensione e SHA-256, e trasferirlo con la connessione SSH già verificata. I pacchetti ordinari desktop/Android non contengono questo archivio; per questa fase la TV non deve accedere a Internet.

Il download opzionale è circa **26,3 MB**, il trasferimento SSH normalizzato **51,5 MB**, i file installati **119,3 MB**; la preparazione richiede **320 MiB** liberi sulla TV. La compatibilità del loader e delle librerie viene verificata prima dell’attivazione. I file risiedono in slot privati sotto `/var/lib/clean-your-tv-python/`: Python di sistema, libc e PATH globale non vengono modificati. Restano necessari root, servizi webOS compatibili e Node.js **8+** per Root/System Updater; il Helper No-root richiede Node.js **0.12.2+**.

Per preparare una cache verificata su un computer con Internet, senza cercare né contattare una TV:

```sh
./cytv --prepare-python-runtime --data-dir /percorso/cache-privata
```

Riusa la stessa `--data-dir` durante l’installazione. Per trasferire la cache, crea una cartella privata dedicata: non condividere dati contenenti chiavi SSH o profili. `status`, `doctor`, `restore` e `uninstall` non scaricano automaticamente Python. Conserva gli slot ancora usati da Root, dagli updater o dal ripristino, anche dopo la rimozione delle app. Dettagli: [runtime opzionale](../OPTIONAL-PYTHON.md).

## Installazione e lingua

- **Windows x64:** scarica `cytv-windows-x64-desktop.zip`, scegli **Estrai tutto** in Esplora file e apri `cytv-desktop/cytv-desktop.exe`. Mantieni la cartella `_internal` accanto al file. La firma dell’editore Windows non è configurata. La console separata è `cytv-windows-x64.exe`; rinominala in `cytv.exe` e usa `.\cytv.exe` in PowerShell per i comandi seguenti.
- **macOS 13+:** estrai `cytv-macos-arm64.zip` per Apple Silicon oppure `cytv-macos-x64.zip` per Intel, sposta `cytv.app` in Applicazioni e aprila. Consenti l’accesso alla rete locale. Se un download affidabile viene bloccato, usa Privacy e sicurezza → Apri comunque; non disattivare Gatekeeper. La verifica sui sistemi meno recenti non è conclusa.
- **Linux x64:** su Ubuntu 22.04+, Debian 12+ o Mint 21+, installa `cytv-linux-x64.deb` con il gestore grafico dei pacchetti e apri Clean Your TV dal menu. Le librerie possono richiedere Internet. Linux ARM non è incluso. L’eseguibile autonomo `cytv-linux-x64` è la CLI; usa il `.deb` per l’app grafica.

[Installer Android](../../android/README.md): sono disponibili tutte e dodici le lingue. Il pulsante in alto a destra mostra la lingua attuale; toccalo per sceglierne un’altra. La scelta viene salvata sul telefono.

Su Android, l’azione di manutenzione scelta resta visibile durante la connessione e mostra il proprio avanzamento. L’interfaccia usa il carattere di sistema del telefono con etichette e testi di aiuto più grandi.

L’assistente usa inizialmente la lingua del sistema e salva una scelta esplicita. Sul televisore, apri **Impostazioni → Lingua** e scegli una lingua oppure l’opzione automatica del sistema. Le preferenze del televisore e dell’installer sono separate. I codici sono nell’[indice delle lingue](../LANGUAGES.md).

Per la CLI scaricata separatamente su macOS/Linux, dalla cartella estratta:

```sh
chmod +x cytv
./cytv --language it install
```

Scegli il televisore o inserisci l’IP, seleziona l’edizione e controlla il riepilogo. Accetta una nuova identità SSH solo per il tuo televisore su una rete affidabile; una chiave salvata cambiata blocca l’accesso. Root prepara il ripristino e attiva subito Home, senza prova temporanea né passaggio per confermare il mantenimento. Verifica frecce, OK, Home, Indietro/Annulla, volume, standby e avvio a freddo.

Se la rimozione di Root si interrompe, scegli di nuovo Rimuovi nell’app. Verifica il registro della TV e i pacchetti prima di continuare, senza ripetere una rimozione completata. Se è ancora in corso, attendi un minuto. Se il risultato non è verificabile, riavvia la TV e verifica di nuovo; conserva il rapporto per il supporto.

## Uso e ripristino

Le frecce selezionano, OK apre; tieni premuto OK per riordinare. Un breve Indietro conserva navigazione e conferma di uscita dell’app. Home apre il launcher quando il controllo è attivo. Nelle nuove compilazioni, tieni premuto Indietro per 1,2 secondi per aprire LG Home una volta. L’interruttore del controllo Home e le impostazioni restano invariati.

**Nuove compilazioni: premi Home tre volte entro due secondi**, rilasciandolo tra le pressioni. Ripristina LG Home e interrompe il controllo senza cancellare le preferenze. Con No-root Helper fino alla 0.6.13 inclusa, tieni invece premuto Home per circa due secondi. La pressione prolungata di Home non è il gesto di emergenza di Root.

No-root: Tre pressioni brevi di Home entro due secondi riportano a LG Home. Per riavviare il controllo Home, apri Home Helper, scegli Avvia Helper e conferma. La tua scelta della schermata Home viene mantenuta. Root: attiva **Cambia Home** nelle impostazioni Home per riprendere. **Apri LG Home** apre LG Home una volta senza cambiare la destinazione di Home. Per ripristinare LG Home come destinazione permanente, disattiva **Cambia Home** o esegui `cytv restore`. Non eseguire entrambi i controllori insieme. Se il problema ricompare, lascia attivo LG Home.

```sh
./cytv --language it status
./cytv --language it doctor --report
./cytv --language it restore
./cytv --language it uninstall
```

Dopo un’interruzione, esegui prima `status` e conserva i registri. `restore` ripristina LG Home senza rimuovere app; `uninstall` lo ripristina prima della rimozione. I dati di ripristino Root restano intenzionalmente: non cancellarli per forzare una reinstallazione. Controlla i rapporti prima di condividerli; non pubblicare chiavi o cartelle dei profili.

## Aggiornamenti e rimozione

Dopo la connessione, cytv mostra versione installata → inclusa e distingue prima installazione, reinstallazione e downgrade. Controlla il riepilogo prima della conferma; `--yes` non rende sicuro un passaggio incompatibile. Conserva pacchetti funzionanti e copie private delle impostazioni. Per gli aggiornamenti dal computer ferma No-root Helper prima di sostituire i pacchetti; non disinstallare prima. Non sovrascrivere un ambiente Root attivo con una sola IPK: usa il percorso previsto da cytv. Rimuovere l’app desktop non rimuove le app TV.

La candidata aggiunge **Aggiorna tutto** in Impostazioni → Aggiornamenti software. Il System Updater indipendente verifica un insieme firmato per l’edizione: Home, Helper e Home Updater per No-root su TV con root; Root Home, Root Updater e runtime di controllo/ripristino per Root. L’installazione dalla TV richiede **root, Homebrew Channel**, Python compatibile, Node.js 8+ e servizi webOS funzionanti. Su TV senza root usa il computer.

Per una prima installazione usa l’installer completo della candidata, che prepara Home e l’Updater di ripristino dell’edizione. Questa versione di transizione non è offerta dal feed stabile.

Se Root è già installato e Root Updater è ancora presente, una reinstallazione generica può essere rifiutata intenzionalmente. Prima esegui `status` e la diagnostica, poi verifica la transazione e lo stato di ripristino nell’Updater esistente. Risolvi le operazioni attive o incerte tramite il relativo percorso di ripristino precedente; la transizione dell’infrastruttura va valutata sullo stato reale della TV. Non cancellare il diario né aggirare il blocco con `--yes`, una IPK isolata o un vecchio OTA. L’OTA della sola app non installa la nuova infrastruttura. Segui il [controllo della TV esistente](../UPDATES.md#one-time-computer-preparation).

Solo dopo aver verificato una configurazione compatibile con Home `systemUpdateProtocol = 1` e l’Updater di ripristino appropriato, abilita il supervisore dal computer. Nell’installer scegli l’opzione per abilitare gli aggiornamenti di tutti i componenti TV; per Root, con connessione SSH root salvata:

```sh
./cytv --language it enable-system-updates --edition root --host TV_ADDRESS
```

Per No-root su TV con root, prepara prima Home/Helper/Home Updater dal computer e usa il procedimento con alias SSH root in [Aggiornamenti](../UPDATES.md#one-time-computer-preparation). Il supervisore salva una base di ripristino verificata dei componenti realmente installati. Un vecchio aggiornamento OTA della sola app non installa il nuovo runtime Python, il supervisore o l’infrastruttura degli updater. Dopo la preparazione usa il percorso comune: gli installer precedenti in conflitto vengono rifiutati.

L’installazione richiede conferma, poi verifica automaticamente l’avvio. Le impostazioni e il profilo vengono conservati; un arresto esplicito o di emergenza del controllo Home non viene annullato. La schermata mantiene il fuoco del telecomando: Su/Giù scorre le note, Sinistra/Destra sceglie le azioni. Un punto arancione indica una nuova versione, anche quando richiede il computer. Apri Ripristino dall’Updater per conoscere lo stato e la versione precedente disponibile. Il ripristino del sistema torna all’intero insieme precedente e al profilo salvato; le modifiche successive alle impostazioni possono andare perse. La verifica automatica dell’avvio non elimina il ripristino, che resta disponibile fino alla transazione successiva.

Dopo un’interruzione esegui `status`, conserva il diario e i dati di ripristino. Un risultato ambiguo blocca nuove installazioni e ripristini; leggere una versione non dimostra che l’installer abbia terminato. Non cancellare diari, blocchi o slot Python per forzare un tentativo. Conserva il rapporto `doctor --report`: distingue i requisiti Root falliti e registra codici numerici SSH senza credenziali o output grezzo. Controllalo comunque prima di condividerlo.

## Verifiche hardware e limiti

Root 0.2.0, Root Updater 0.2.0 e supervisore 1.0.0 sono stati verificati su OLED55C3RLA / firmware 43.21.71 / webOS 11.2.0 (`d344d92`, contenuto identico a `4b66951`). Superati comandi, triplo Home e ripresa, standby/risveglio con Emby aperto per 70 secondi, menu versioni e messaggio chiaro con feed non disponibile. Avvio a freddo reale, Helper 0.6.19 su TV, UK6540PTD e aggiornamento/ripristino completo firmato non sono stati testati. Il rilascio stabile accetta queste prove limitate; gli altri modelli non sono validati.

No-root controlla l’ABI della shell e accetta un kernel a 64 bit solo con ambiente ARM32 verificato. Un nome di modello o `armv7l` non garantiscono compatibilità. Mantieni i limiti hardware della versione effettivamente provata.

No-root: Impostazioni Home → Modalità sviluppatore raccoglie rinnovo Beta, verifica sessione e diagnostica. Controlla sempre il timer ufficiale. Home Helper mostra il proprio stato e richiede conferma per riprendere dopo un arresto.

Documentazione tecnica: [desktop](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [installazione manuale](../MANUAL_INSTALL.md), [ripristino](../RECOVERY.md), [edizioni](../EDITIONS.md), [aggiornamenti](../UPDATES.md).

Se Root mostra `Denied methods call status` subito dopo la preparazione del supervisore, chiudi e riapri Home Root una volta, poi controlla gli aggiornamenti. Se persiste, conserva diagnostica e stato di ripristino.

1.2.0 (#51): dopo il rifiuto di un pacchetto da parte della TV, il rapporto JSON conserva solo la categoria dell’operazione, codici numerici limitati, uno stato del pacchetto consentito e un risultato booleano. Esclude il testo originale dell’errore, percorsi e ID delle app. Controllalo prima di condividerlo; nessun tentativo automatico. La risoluzione del problema di installazione su UN70006LA non è ancora confermata.

1.2.0 (#59): se lo stato di Helper non può essere verificato, **Avvia Helper** resta disponibile con conferma. Aprire il riquadro non riavvia Helper e non annulla un arresto di emergenza. Le impostazioni Home richiedono che il controllo risponda.

1.2.0 (#55): Root verifica la migrazione prima di installare. Un’installazione interrotta prima del provisioning può essere rimossa senza uno snapshot LS2 mai creato; conserva una ricevuta verificata per la normale archiviazione e reinstallazione di cytv. Snapshot mancanti nelle fasi successive o prove in conflitto bloccano ancora la pulizia. Serve il nuovo driver; il problema di avvio del servizio di recupero su OLED Flex resta irrisolto.

## Blocco firmware LG in 1.2.0

Solo Root: Impostazioni Home → Aggiornamenti firmware LG modifica l’impostazione esistente di Homebrew Channel. Include gli aggiornamenti di sicurezza del firmware; quelli di Clean Your TV restano separati. Serve un vero riavvio della TV in entrambe le direzioni; lo standby non basta. L’interruttore mostra l’impostazione salvata, non un blocco effettivo verificato. Alcune TV controllano prima del blocco; gli avvisi possono restare e può servire un blocco sul router. Homebrew conserva l’impostazione dopo rimozione o rollback di CYTV. Se non disponibile o non confermato, controlla Homebrew e aggiorna lo stato. Il verbale di accettazione descrive la portata dei test TV.

[LG firmware blocking](../LG-FIRMWARE-UPDATES.md) · [1.2.0](../RELEASE-1.2.0-ACCEPTANCE.md)

## Novità della 1.3.0: ripristino guidato dal computer

Novità della 1.3.0. Dopo il controllo dello stato, la diagnostica della connessione o il ritorno a LG Home, una rimozione No-root incompleta propone **Ripristina e reinstalla** per la stessa TV e connessione. Conferma esplicitamente il completamento della rimozione (predefinito: No), quindi verifica le versioni incluse prima dell’installazione. Anche **Configura la mia TV** offre questo percorso. Il solo ritorno a LG Home non completa la rimozione. In caso di errore, usa **Salva rapporto diagnostico…** per salvare il rapporto di quel tentativo e allegarlo alla segnalazione; non serve il terminale. Se il rapporto non è stato creato, indica l’errore visibile. Conserva i dati di ripristino; le operazioni fallite o dall’esito incerto non vengono ripetute automaticamente. Questo non conferma ancora la soluzione del problema G5 / firmware 43.21.71 (#65).

## Novità della 1.3.0 — #12

Gli Strumenti Android mantengono TV, edizione e porta SSH dopo il ritorno alla schermata iniziale; No-root usa normalmente 9922. Se le impostazioni non possono verificare il controllo Home, mostrano uno stato sconosciuto e nascondono Cambia Home fino a una risposta valida. Questo non significa che Helper sia arrestato e non lo riavvia. Queste modifiche non sono nei pacchetti pubblicati di v1.2.0.

Diagnostica Root della 1.3.0 (#55): dopo un errore di installazione, salvare il rapporto di quel tentativo. Può includere categorie di errori di avvio del servizio di ripristino; conservare i dati di ripristino e il driver installato. La correzione su OLED Flex non è ancora confermata.

## Candidato non pubblicato: installazione Root tramite Homebrew

Questo codice aggiunge l’app separata **CYTV Installer**, solo per **Root**.
Non è ancora pubblicata nel catalogo Homebrew. cytv mantiene No-root e Root su
Windows, macOS, Linux e Android; i collegamenti esistenti restano quelli di cytv.

Servono root già disponibile, Homebrew Channel con esecuzione root, Node.js **8+**
e Python **3.9+** funzionante. È incluso offline un Python privato fissato per
ARMv7/`armv8l` compatibile con ambiente a 32 bit. Apertura e stato non modificano
nulla: preparare esplicitamente Python se manca, controllare di nuovo e rivedere
l’installazione. Servono **320 MiB liberi dopo l’installazione di Installer**;
lo spazio temporaneo aggiuntivo dei pacchetti sul TV non è ancora misurato.
Non è dimostrata compatibilità con nuovi modelli o firmware.

Si installano Root Home e Root Updater; System Updater è una scelta esplicita
facoltativa. Attivare Change Home separatamente dopo le verifiche. Arresto di
emergenza e preferenze disattivate restano tali. Un’installazione attuale verificata
condivide profilo e recupero tra cytv e TV senza reinstallare o azzerare. La vecchia
infrastruttura sconosciuta richiede diagnosi; l’importazione delle preferenze
confezionate vale per una nuova installazione, non per browser o infrastruttura.

Dopo un’interruzione leggere prima lo stato. Continua richiede istantanea e
prenotazione originali con stato finale provato. Altrimenti usare stato, ripristino
o diagnosi; la CLI sorgente può continuare esplicitamente altre fasi riconosciute.
Finish Root setup in cytv non riavvia un processo incompleto. Non eliminare diari
e non riprovare alla cieca. Homebrew aggiorna solo Installer; il prodotto usa gli
Updater esistenti e insiemi completi firmati. Eliminare Installer lascia il prodotto.
La rimozione completa ripristina LG Home e pulisce i collegamenti di avvio propri,
conservando recupero indipendente, archivi e Python necessario. Tutti i test fisici
di questo percorso sono ancora da eseguire; i risultati storici Root 0.2.0 su C3
non lo convalidano.

L’avvio usa file privati associati alle prove di proprietà e verifica l’identità del pacchetto come dati. Gli script di avvio del pacchetto non vengono eseguiti. Pacchetti mancanti o non sicuri bloccano il riavvio automatico; il ripristino indipendente può ancora ripristinare LG Home. L’ispezione può copiare temporaneamente file verificati in uno spazio privato senza modificare Home o il prodotto.

[Installazione e recupero (inglese)](../INSTALL.md#candidate-on-tv-root-installation) ·
[Test fisici in attesa (inglese)](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


Per questo candidato dai sorgenti, un’installazione Root esistente richiede un ripristino verificato e una nuova configurazione per ricevere l’ambiente privato corretto. Aggiornare solo Installer non lo sostituisce. Conservare i dati di ripristino e attivare Home solo dalla configurazione o dalle impostazioni normali.

Solo nel prossimo candidato: No-root Impostazioni → Modalità sviluppatore → Mostra diagnostica include categorie sicure degli errori di archiviazione e RPC Home e la versione effettiva del servizio. La consultazione non abilita il rinnovo né avvia Helper. Un controllo fallito non dimostra che Helper sia fermo. La correzione su C5 non è confermata; [dettagli (inglese)](../SETTINGS-DIAGNOSTICS.md).

Il rapporto riceve il focus del telecomando. Su/Giù scorre; Sinistra/Destra o OK torna alle azioni vicine e Indietro alle impostazioni Home.

**Non ancora pubblicato, #82:** se manca la voce Home, la configurazione Root avviata esplicitamente può impostare LG Home e rileggere il valore prima di completare la preparazione del ripristino. Status/doctor non modifica nulla. Una scrittura con esito incerto non viene ripetuta; conserva i dati di ripristino. La voce esplicita LG Home rimane dopo la disinstallazione. Servono ancora prove su questo firmware.

## Candidato non pubblicato: ripristino audio HDMI (Root)

Impostazioni Home → Audio HDMI offre riconnessione eARC e ripristino HDMI confermato.
ARC-only, combinati/WOW Orchestra e modalità sconosciute sono escluse. L’automazione
all’accensione/risveglio è sperimentale, inizialmente disattivata; richiede una
sottoscrizione di alimentazione supportata e può interrompere audio funzionante.
Indietro chiude durante la pulizia. Dopo interruzione controlla lo stato; ripristina
solo se desideri eARC attivo. Ripristino Home/arresto di emergenza disattiva l’automazione
fino ad attivazione esplicita. Vecchi runtime privati richiedono nuova configurazione
verificata. Compatibilità e minore ritardo non confermati.

[Device acceptance (English)](../development/ROOT-AUDIO-RECOVERY.md)

Non ancora pubblicato: il controllo di Python privato distingue errori ABI, sicurezza delle directory e spazio. La prima installazione richiede 320 MiB liberi in /var/lib. WAM Session Storage può spiegare la mancanza di spazio; cancellarlo può perdere lo stato delle sessioni. Vedi il [ripristino](../RECOVERY.md#private-python-and-low-var-space).

Nel candidato 1.4.0 non ancora pubblicato, anche un’installazione No-root interrotta offre **Ripristina e reinstalla** dopo **Controlla lo stato della TV**. Conferma la rimozione solo se vuoi eliminare le app Clean Your TV, poi controlla le versioni prima di reinstallare. Se il ripristino fallisce, salva il relativo rapporto diagnostico e fermati. Il rifiuto iniziale del pacchetto da parte della TV non è ancora spiegato né confermato come risolto (#21).


**Non pubblicato — WAM:** `cytv clean-wam-cache --edition root`. Sono richiesti solo cache e codecache. Session Storage, cookie, Local Storage, Service Worker e database sono esclusi. Chiudi le app TV. La cache sarà scaricata o ricreata; il prossimo avvio può essere più lento. [WAM](../WAM-CLEANUP.md).

Puoi annullare e liberare spazio da solo. Segui la guida e ricontrolla /var/lib; rimuovere app può liberare un'altra partizione. **Session Storage (SSH):** Chiudi prima le app del TV. Lo stato delle sessioni sarà eliminato; potresti perdere accessi o lavoro non salvato. [WAM](../WAM-CLEANUP.md#free-space-yourself-instead).

Correzione Root dell’avvio a freddo non ancora pubblicata: con il controllo Home attivo e LG impostato sulla schermata Home all’accensione, un avvio protetto può aprire Clean una volta se sono ancora visibili TV in diretta o LG Home. Un’app visibile all’ultimo controllo viene mantenuta; nessun nuovo tentativo. La disattivazione esplicita e tre pressioni Home restano disattivate. Serve un’installazione/aggiornamento verificato del runtime privato; aggiornare solo l’app non basta. La verifica sul televisore resta da completare.

[Cold-start investigation and acceptance (English)](../development/ROOT-COLD-BOOT.md)

Correzione OTA candidata (#115): il System Updater originale di 1.3.0 non può installare 1.4.0 perché cambiano i file consentiti. Un arresto prima della sostituzione non è un’installazione parziale. Conserva il registro; non riprovare, cancellare lo stato o modificare i percorsi. Il prossimo candidato mantiene i contratti di percorsi e permessi di 1.3.0; aggiornamento e rollback su TV richiedono ancora prove coordinate.

Correzione non ancora pubblicata (#108/#109): con System Updater configurato, il punto degli aggiornamenti e «Aggiorna tutto» usano la stessa verifica dell’edizione. Una nuova versione generale senza modifiche alle versioni dei componenti non propone la reinstallazione. Durante la verifica l’installazione resta disabilitata. La verifica precedente viene usata solo se System Updater è assente. La conferma sul televisore è ancora in attesa.

Correzione di accesso #110 del candidato: il nuovo installer registra un’autorizzazione CYTV solo per le API di configurazione Homebrew. Per un’installazione Root esistente esegui `cytv enable-firmware-access --edition root`, riapri Root Home e verifica gli aggiornamenti firmware LG. Non cambia ACL Homebrew o preferenza di blocco. Dopo un’interruzione ripeti lo stesso comando. `cytv disable-firmware-access --edition root` revoca l’accesso senza cambiare il blocco. Il nuovo runtime mantiene la registrazione dopo gli aggiornamenti completi; con un vecchio runtime il comando può servire di nuovo dopo un aggiornamento della sola app. Consulta la guida firmware per requisiti, ripristino e limiti delle verifiche.

CLI candidata: l’output reindirizzato di Windows usa sequenze di escape per i caratteri non supportati dalla codifica scelta, senza interrompersi. UTF-8 conserva il testo localizzato. Questo non conferma il supporto Root su BX/webOS 5.
