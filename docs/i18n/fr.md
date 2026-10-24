# Clean Your TV — guide d’utilisation

## Prérequis

Ce guide couvre l’installation, l’utilisation et la récupération. Le choix de langue et l’application de bureau macOS/Linux sont inclus dans [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). Les anciens téléchargements v0.9.0 ne contiennent pas l’application graphique. Consultez le [guide d’installation des deux éditions](../INSTALL.md).

Allumez le téléviseur et reliez-le au même réseau local de confiance que l’ordinateur. L’ordinateur peut ensuite rester éteint. La compatibilité dépend du modèle, du micrologiciel et de la télécommande ; Root reste une préversion avec des essais matériels à terminer.

- **No-root :** activez LG Developer Mode et Key Server. Saisissez la phrase secrète affichée sur le téléviseur et acceptez sur celui-ci la demande d’association distincte. Developer Mode doit rester actif : son expiration peut supprimer les applications installées ainsi. Surveillez son compteur officiel même avec le renouvellement Beta activé. La surveillance du Helper nécessite le réseau local.
- **Root :** un accès SSH root existant est nécessaire. L’installateur ne roote pas le téléviseur. N’activez pas Developer Mode sur une installation déjà rootée. Conservez l’accès root et les services de récupération.

## Installation et langue

- **Windows x64 :** décompressez le paquet console et ouvrez `cytv.exe`. Dans PowerShell, remplacez `./cytv` par `.\cytv.exe` dans les commandes suivantes. Il n’y a pas d’application graphique Windows dans ce paquet.
- **macOS 13+ :** décompressez `cytv-macos-arm64.zip` pour Apple Silicon ou `cytv-macos-x64.zip` pour Intel. Placez `cytv.app` dans Applications et ouvrez-la ; autorisez l’accès au réseau local. En cas de blocage d’un téléchargement fiable, utilisez Confidentialité et sécurité → Ouvrir quand même, sans désactiver Gatekeeper. La validation sur les anciens systèmes reste ouverte.
- **Linux x64 :** sous Ubuntu 22.04+, Debian 12+ ou Mint 21+, installez `cytv-linux-x64.deb` avec le gestionnaire graphique de paquets, puis ouvrez Clean Your TV depuis le menu. Internet peut être nécessaire pour les bibliothèques. Linux ARM n’est pas fourni.

L’assistant utilise initialement la langue du système et mémorise votre choix explicite. Sur le téléviseur, ouvrez **Paramètres → Langue** et choisissez une langue ou l’option automatique du système. Les préférences du téléviseur et de l’installateur sont indépendantes. Les codes figurent dans l’[index des langues](../LANGUAGES.md).

Pour la CLI téléchargée séparément sous macOS/Linux, depuis son dossier décompressé :

```sh
chmod +x cytv
./cytv --language fr install
```

Choisissez le téléviseur ou son adresse IP, l’édition, puis vérifiez le récapitulatif. N’acceptez une nouvelle identité SSH que pour votre téléviseur sur un réseau fiable ; une clé enregistrée modifiée bloque la connexion. Root prépare la récupération et active Home immédiatement, sans essai temporaire ni étape de conservation. Testez flèches, OK, Home, Retour/Annuler, volume, veille et démarrage à froid.

## Utilisation et récupération

Les flèches sélectionnent, OK ouvre ; maintenez OK pour réorganiser. Un appui bref sur Retour conserve la navigation et la confirmation de sortie de l’application. Home ouvre le lanceur si le contrôle est actif. Dans les nouvelles compilations, maintenez Retour pendant 1,2 seconde pour ouvrir LG Home une fois. L’interrupteur du contrôle de Home et vos paramètres restent inchangés.

**Nouvelles compilations : appuyez trois fois sur Home en deux secondes**, en relâchant entre les appuis. Cela rétablit LG Home et arrête le contrôle sans effacer vos préférences. Avec No-root Helper jusqu’à 0.6.13 inclus, maintenez plutôt Home environ deux secondes. Maintenir Home n’est pas le geste d’urgence de Root.

No-root : ouvrez **Home Helper** dans les applications LG pour reprendre ; Home seul ne supprime pas l’arrêt. Root : activez **Changer Home** dans les paramètres de Home pour reprendre. **Ouvrir LG Home** ouvre LG Home une fois sans modifier la destination de Home. Pour rétablir LG Home comme destination permanente, désactivez **Changer Home** ou exécutez `cytv restore`. N’exécutez jamais les deux contrôleurs ensemble. Si la panne revient, laissez LG Home actif.

```sh
./cytv --language fr status
./cytv --language fr doctor --report
./cytv --language fr restore
./cytv --language fr uninstall
```

Après interruption, lancez d’abord `status` et conservez les journaux. `restore` rétablit LG Home sans supprimer les applications ; `uninstall` le rétablit avant leur suppression. Les données de récupération Root sont conservées volontairement : ne les effacez pas pour forcer une réinstallation. Vérifiez les rapports avant partage ; ne publiez ni clés ni dossiers de profils.

## Mises à jour et suppression

Gardez les paquets fonctionnels et des sauvegardes privées des paramètres. Arrêtez No-root Helper avant de remplacer ses paquets ; mettez à jour depuis l’ordinateur sans désinstaller d’abord, car cela peut effacer les préférences. L’installation Root combinée de cytv comprend les mises à jour compatibles dans Paramètres → Mises à jour logicielles ; l’installation manuelle présente d’autres limites. N’installez pas une IPK isolée sur un environnement Root actif. Utilisez le parcours explicite de réinstallation cytv. Supprimer l’application de bureau ne supprime pas les applications TV.

Documentation technique en anglais : [bureau](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [No-root](../INSTALL.md), [installation manuelle](../MANUAL_INSTALL.md), [récupération](../RECOVERY.md), [éditions](../EDITIONS.md).

Après connexion, cytv lit les versions du téléviseur et affiche la version actuelle → incluse pour Home et Home Helper (No-root), ou Root et Root Updater. Vérifiez et confirmez avant installation. Les premières installations, réinstallations et retours à une version antérieure sont signalés ; `--yes` ignore la confirmation mais affiche les versions.

Les mises à jour logicielles affichent uniquement les détails de la version installée ou plus récente. Ouvrez Récupération pour voir la version enregistrée à restaurer ou la raison de son indisponibilité ; Retour revient aux mises à jour.

No-root vérifie l’ABI du shell du téléviseur et accepte un noyau 64 bits avec un environnement ARM32 confirmé. En cas d’échec, joignez le JSON de diagnostic généré ; ne partagez ni clés ni phrases secrètes.

Les mises à jour de Home demandent une confirmation avant l’installation ; le démarrage est ensuite vérifié automatiquement. L’actualisation de l’état conserve le bouton sélectionné avec la télécommande.
