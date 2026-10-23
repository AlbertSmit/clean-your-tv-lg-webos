# Offline candidate bundle

Build on the host with Python 3; the output directory must not exist:

```sh
python3 root-edition/build.py --output /absolute/path/to/new-candidate
```

The bundle contains an isolated `com.cleanyourtv.root.preview` IPK, its public-source file hashes, the recovery runtime, and host/device drivers. `bundle.json` covers every distributed support/runtime file. `SHA256SUMS` covers the IPK. No TV connection occurs during build. This candidate still requires hardware validation.

For the later supervised TV session, use an explicit preconfigured OpenSSH alias with its host key already trusted:

```sh
python3 /path/to/candidate/setup.py install --ssh television --bundle /path/to/candidate
python3 /path/to/candidate/setup.py status --ssh television
python3 /path/to/candidate/setup.py trial --ssh television
python3 /path/to/candidate/setup.py restore --ssh television
python3 /path/to/candidate/setup.py uninstall --ssh television
```

`--identity /path/to/key` is optional. The scripts require strict host-key checking and batch authentication. Device operations require root, the webOS Luna tool, and the developer-app directory. Installation does not select this app as Home. Trial uses the runtime's bounded recovery flow; persistent enable is unavailable.

By default the launcher inventory is empty. Explicitly add `--migrate-packaged-home` to **install** to copy `apps.js`, `config.js`, and referenced packaged icons from the fixed installed `com.gathin.tvhome` app. The source is read-only and never modified. Browser/localStorage-only preferences are excluded. Resulting candidate file hashes are retained in `personalization.json`; migration never adds personal data to the offline distribution.

The driver records stages in `/var/lib/clean-your-tv-root/deploy.json` before installation submission. Installation proceeds only after an independent matching terminal backend event and installed-file hash verification. Existing candidate files or state block installation. A timeout, disconnect, or uncertain result requires inspection; do not blindly retry. Remote staging remains available after failure.

Uninstall first requires successful Home recovery, rolls back this candidate's LS2 provisioning, refreshes registration, and requests removal. It requires a terminal removal reply and absence of all candidate app/service/package directories. State and recovery evidence remain on disk; the driver never deletes retained state automatically. The production app and legacy helper are never written by these drivers.
