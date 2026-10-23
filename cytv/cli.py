"""Numbered terminal wizard and small maintenance command surface."""
import argparse
import getpass
import json
from pathlib import Path
import sys

from . import __version__, package, state
from .errors import UserError, TVNotReady, ExistingRoot
from .operations import Installer
from .terminal import Console
from . import diagnostics, discovery, inspect_tv, prompts


def payload_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'payload'
    return Path(__file__).resolve().parents[1] / 'build/cytv/payload'


def parser():
    result = argparse.ArgumentParser(prog='cytv', description='Clean Your TV — one installer for No-root and Root.')
    result.add_argument('command', nargs='?', default='install', choices=('install', 'status', 'doctor', 'restore', 'uninstall'))
    result.add_argument('--version', action='store_true', help='Print installer version')
    result.add_argument('--host', help='TV IPv4 address or hostname')
    result.add_argument('--no-discovery', action='store_true', help='Skip local network discovery and enter a TV address manually')
    result.add_argument('--edition', choices=('no-root', 'root'))
    result.add_argument('--port', type=int, help='SSH port (No-root: 9922; Root: 22)')
    result.add_argument('--identity', type=Path, help='Existing Root SSH private key')
    result.add_argument('--data-dir', type=Path, help='Private local profile directory')
    result.add_argument('--non-interactive', action='store_true', help='Never prompt; needs a saved, trusted connection')
    result.add_argument('--yes', action='store_true', help='Accept install/remove summary; does not accept SSH trust')
    result.add_argument('--migrate-home', action='store_true', help='Root install: explicitly import existing Home packaged/profile data')
    result.add_argument('--check-payload', action='store_true', help='Verify embedded release assets without contacting a TV')
    result.add_argument('--report', action='store_true', help='doctor: save an issue-ready diagnostic report without private connection data')
    return result


def choose_profile(args, store, ask, write, search, inspect):
    profiles = [p for p in store.profiles() if not args.edition or p['edition'] == args.edition]
    if not args.host and len(profiles) == 1 and (args.command != 'install' or args.non_interactive):
        profile = dict(profiles[0])
        write('Using saved ' + profile['edition'] + ' TV connection.')
    elif not args.host and profiles:
        write.step(1, 'Choose a saved TV')
        for index, p in enumerate(profiles, 1):
            write.option(index, p['host'], 'Root' if p['edition'] == 'root' else 'No-root')
        write.option(0, 'Add another TV')
        selected = prompts.number(ask, write, 'TV number [1]: ', 0, len(profiles), default=1)
        profile = dict(profiles[selected - 1]) if selected else None
    else:
        profile = None
    if profile is None:
        host = args.host or prompts.tv_address(ask, write, search=None if args.no_discovery or args.non_interactive else search)
        edition = args.edition
        if edition is None:
            try:
                state.target(host, 'no-root', args.port)
            except ValueError:
                raise UserError('Invalid TV address or port. Use an IPv4 address or hostname and a port from 1 to 65535.') from None
            info = {}
            if not args.non_interactive:
                write('')
                write('Checking TV connections…')
                info = inspect(host, args.port)
            recommended = 2 if info.get('root_ssh') else 1
            write.step(2, 'Choose your edition')
            write('TV: ' + host)
            write.heading('Connection check')
            if info.get('root_ssh'):
                write(f"Root SSH detected on port {info.get('root_port', 22)}.")
                write('Root privileges will be verified after sign-in.')
            else:
                write('Root access not confirmed. SSH may be disabled or use another port.')
            if info.get('developer_ssh'):
                write('Developer Mode SSH detected.')
            write.option(1, 'No-root' + (' (recommended)' if recommended == 1 else ''),
                         'For a TV without root. Uses LG Developer Mode.')
            write.option(2, 'Root' + (' (recommended)' if recommended == 2 else ''),
                         'For an already rooted TV with existing SSH access.')
            write('')
            write('This installer does not obtain root. Unsure? Choose No-root.')
            write('Enter = recommended edition   |   q = quit')
            choice = prompts.number(ask, write, f'Edition [{recommended}]: ', 1, 2, default=recommended)
            edition = 'no-root' if choice == 1 else 'root'
        try:
            profile = state.target(host, edition, args.port, args.identity)
        except ValueError:
            raise UserError('Invalid TV address or port. Use an IPv4 address or hostname and a port from 1 to 65535.') from None
        # Match saved credentials, including the identity, when targeting a known TV explicitly.
        for saved in profiles:
            if all(saved[k] == profile[k] for k in ('host', 'edition', 'port')):
                profile = dict(saved)
                break
    if args.port is not None:
        profile['port'] = args.port
    if args.identity:
        profile['identity'] = str(args.identity.expanduser().resolve())
    return state.target(**profile)


def main(argv=None, ask=input, write=print, connect=None, secret=getpass.getpass, search=None, inspect=None):
    args = parser().parse_args(argv)
    if args.version:
        write('cytv ' + __version__)
        return 0
    write = write if isinstance(write, Console) else Console(write, interactive=False if args.non_interactive else None)
    ask = write.reader(ask)
    remote = None
    store, profile, phase, tv_info = state.Store(args.data_dir), None, 'select-tv', {}
    try:
        if args.check_payload:
            manifest = package.verify_payload(payload_dir())
            write(f"Embedded payload verified: {len(manifest['files'])} public files; no TV contacted.")
            return 0
        if args.migrate_home and (args.command != 'install' or args.edition == 'no-root'):
            raise UserError('--migrate-home applies only to Root installation.')
        if args.report and args.command != 'doctor':
            raise UserError('--report is available with cytv doctor.')
        if args.non_interactive:
            def no_ask(_):
                raise UserError('Non-interactive mode needs --host and --edition or one saved profile; pairing and SSH trust must already be completed.')
            ask = no_ask
            secret = no_ask
        if args.command == 'install' and not args.non_interactive:
            write.heading('Clean Your TV  /  Installation')
            write('TV > Edition > Connection > Install')
            write('q / Ctrl+C = quit. Password entry uses Ctrl+C.')
        def inspect_connection(host, port):
            nonlocal phase
            phase = 'inspect-tv'
            info = (inspect or inspect_tv.inspect)(host, port)
            phase = 'select-edition'
            return info

        profile = choose_profile(args, store, ask, write, search or discovery.find_tvs, inspect_connection)
        if args.command == 'install':
            phase = 'prepare-payload'
            write.step(3, 'Prepare the TV connection')
            if profile['edition'] == 'root':
                write('Root requires existing root and SSH access.')
                write('Hardware validation: LG C3; other models are unverified.')
            else:
                write('On the TV: LG Apps > Developer Mode. Sign in, then enable:')
                write('  1. Dev Mode Status')
                write('  2. Key Server')
                write('Keep this screen open for the passphrase.')
                write('Developer Mode must stay active after installation.')
            write.step(4, 'Review and install', clear=profile['edition'] == 'root')
            write('TV: ' + profile['host'])
            write('Edition: ' + ('Root' if profile['edition'] == 'root' else 'No-root'))
            write('SSH port: ' + str(profile['port']))
            if profile['edition'] == 'root':
                write('Hardware validation: LG C3; other models are unverified.')
                write('Automatic SSH sign-in first; credentials only if needed.')
            write('Next: verify SSH, read your apps, then install.')
            if profile['edition'] == 'root':
                write('Root will stop the old Home Helper, turn on Home control and open Clean Your TV Home.')
            write('Check controls on the TV after installation.')
        if args.command in ('install', 'uninstall', 'restore') and not args.yes:
            verb = {'install': 'Install this edition', 'uninstall': 'Restore LG Home and remove this edition', 'restore': 'Restore LG Home'}[args.command]
            if not prompts.confirm(verb + '?', ask, write, default=args.command == 'install'):
                write('Cancelled. No TV changes were made.')
                return 0
        payload, manifest = payload_dir(), {}
        if args.command == 'install':
            try:
                manifest = package.verify_payload(payload)
            except FileNotFoundError:
                raise UserError('Release payload is missing. Download a built cytv executable or run python scripts/build-cytv.py --payload-only from source.') from None
            if args.migrate_home and profile['edition'] != 'root':
                raise UserError('--migrate-home applies only to Root installation.')

        def trust(value, root):
            if args.non_interactive:
                raise UserError('This TV is not remembered yet. Connect interactively once to confirm it on your trusted home network.')
            if not prompts.trust_tv(profile['host'], profile['port'], value, ask, write):
                raise EOFError
            return True

        def secret_with_help(prompt):
            if not args.non_interactive:
                write.heading('Connection password')
                if prompt.startswith('Developer Mode'):
                    write('Use the passphrase shown in Developer Mode > Key Server.')
                elif prompt.startswith('SSH key'):
                    write('Enter the passphrase that unlocks your private SSH key file.')
                else:
                    write('Enter your existing TV root SSH password. This was set when SSH access was configured.')
                write('Typing is hidden: no characters or dots appear.')
                write('Enter = submit   |   Ctrl+C = cancel')
            return secret(write.prompt(prompt))

        from .transport import SSH
        with store.lock(profile):
            phase = 'ssh-connect'
            write('Connecting to the TV…')
            if connect:
                remote = connect(profile, store.device_dir(profile), secret_with_help, trust)
            else:
                remote = SSH.connect(profile, store.device_dir(profile), secret_with_help, trust,
                                     identity_prompt=None if args.non_interactive else lambda: prompts.root_credentials(ask, write))
            store.save(profile)
            installer = Installer(remote, store, profile, payload, manifest, write)
            if args.command == 'install':
                reinstall = None
                resume = False
                if store.pending(profile):
                    phase = 'inspect-installation'
                    write('Checking the previous installation on the TV…')
                    existing = installer.status()
                    if existing.get('can_resume_root_setup') is True:
                        if args.non_interactive:
                            raise UserError('Root setup is ready to finish. Open cytv interactively to confirm Home activation.')
                        write.heading('Ready to finish Root setup')
                        write('Root and Root Updater are installed and verified. Continue to stop the old Helper, turn on Home control and open Clean Your TV Home.')
                        if not prompts.confirm('Finish Root setup?', ask, write, default=True):
                            write('Setup left unchanged. You can continue here next time.')
                            return 0
                        resume = True
                    elif store.pending(profile):
                        raise UserError('The previous operation could not be safely resolved. Recovery data was kept. Save the diagnostic report; installation has not restarted.')
                if profile['edition'] == 'root' and not resume:
                    phase = 'inspect-installation'
                    try:
                        installer.preflight(install=True)
                    except ExistingRoot:
                        if args.migrate_home:
                            raise UserError('For Root reinstallation, omit --migrate-home. cytv will read a fresh TV inventory before replacing Root; the existing installation was left unchanged.')
                        existing = installer.status()
                        stage = existing.get('deployment_stage')
                        device = existing.get('device', {}).get('result', {})
                        if stage == 'installed-recovery-only' and device.get('recovery', {}).get('integrity_verified') is True:
                            reinstall = 'installed'
                        elif stage == 'uninstalled-state-retained':
                            reinstall = 'removed'
                        else:
                            raise UserError('Previous Root installation needs recovery. Run cytv status or cytv restore. Reinstallation has not started; recovery data was left unchanged.')
                        if args.non_interactive:
                            raise UserError('Root is already installed or removal data remains. Run cytv interactively to review reinstallation. --yes does not approve replacing Root.')
                        write.heading('Root is already installed' if reinstall == 'installed' else 'Previous Root was removed')
                        write('You can reinstall using the packages in this cytv build.')
                        write('LG Home will be restored first. Previous recovery data will be archived on the TV.')
                        write('Root preferences may be reset. Your other TV apps will stay installed.')
                        if not prompts.confirm('Reinstall Root?', ask, write):
                            write('Existing Root and recovery data left unchanged.')
                            return 0
                phase = 'read-inventory'
                inventory, key = None, None
                if not args.migrate_home and not resume:
                    from .tv import SSAP
                    while True:
                        try:
                            phase = 'pair-tv'
                            with SSAP(profile['host'], store.device_dir(profile), write) as tv:
                                phase = 'read-inventory'
                                inventory = tv.inventory((payload / 'fallback.png').read_bytes())
                                key = tv.key
                            break
                        except TVNotReady:
                            if args.non_interactive:
                                raise
                            prompts.wait_for_tv(ask, write)
                    write(f"Read {len(inventory['apps'])} applications.")
                phase = 'install-packages'
                def progress(message):
                    nonlocal phase
                    phase = {'Installing Home Helper…': 'install-helper', 'Installing Home…': 'install-home',
                             'Configuring Home Helper…': 'configure-helper',
                             'Uploading Root and recovery runtime…': 'install-root',
                             'Installing Root Updater and preparing rollback…': 'install-root-updater',
                             'Checking Root Updater…': 'verify-root-updater',
                             'Checking Root recovery…': 'verify-root-recovery',
                             'Stopping the old Home Helper…': 'stop-old-helper',
                             'Turning on Root Home control…': 'activate-root',
                             'Opening Clean Your TV Home…': 'launch-root',
                             'Restoring LG Home and removing the previous Root…': 'remove-existing-root',
                             'Keeping the previous recovery state in an archive…': 'archive-root-state'}.get(message, phase)
                    write(message)
                installer.progress = progress
                def helper_retry():
                    if args.non_interactive:
                        return False
                    write.heading('Stop Home Helper on the TV')
                    write('Press Home three times within two seconds (older Helper: hold Home for two seconds), then release all buttons and wait for LG Home.')
                    return prompts.confirm('Try stopping Helper again?', ask, write, default=True)
                installer.helper_retry = helper_retry
                if resume:
                    result = installer.resume_root_setup()
                else:
                    result = installer.install(inventory, key, args.migrate_home, reinstall=reinstall) if reinstall else installer.install(inventory, key, args.migrate_home)
                if profile['edition'] == 'root':
                    write.heading('Root is ready')
                    write('Home control is on and Clean Your TV Home was opened.')
                    if result.get('updates_ready'):
                        write('Root Updater is ready. Install future compatible updates in Settings → Software updates on the TV.')
                    write('Home control stays on until you turn it off. The computer can now be switched off.')
                    write('To restore LG Home, use Return to LG Home in settings or run cytv restore.')
                    write('Root emergency exit: three short Home presses within two seconds.')
                else:
                    write('Packages installed; Home Helper launch requested. Check short Home, arrows/OK, Back, volume, standby and cold boot.')
                    write('Emergency exit: three short Home presses within two seconds. Keep Developer Mode active. The computer can now be switched off.')
            elif args.command == 'doctor':
                phase = 'doctor'
                installer.preflight()
                write('Connection and basic requirements passed. This does not certify hardware compatibility.')
                write.raw(json.dumps(installer.status(), indent=2))
                if args.report:
                    write.heading('Diagnostic report')
                    write.raw('  ' + str(diagnostics.create_report(store, args.command, profile, 'doctor-complete', tv_info=tv_info)))
            else:
                phase = args.command
                result = getattr(installer, args.command)()
                if (result.get('reconciled') or '').startswith('updater-not-started'):
                    write.heading('Ready to reinstall Root')
                    write('The previous attempt stopped before Root Updater setup. Recovery and installed files are verified; the previous operation report was saved.')
                    write('Return to the start screen, choose Set up my TV and confirm reinstallation. In the console, run cytv install.')
                else:
                    write.raw(json.dumps(result, indent=2))
        return 0
    except (EOFError, KeyboardInterrupt, StopIteration):
        write('Cancelled. Installation has not started.' if args.command == 'install' and phase in ('pair-tv', 'read-inventory', 'prepare-payload', 'select-tv', 'select-edition', 'inspect-tv', 'ssh-connect', 'inspect-installation')
              else 'Cancelled. If an installation was submitted, run cytv status before retrying.')
        return 130
    except UserError as exc:
        write.heading('Could not complete this step')
        write(str(exc))
        if phase in ('pair-tv', 'read-inventory'):
            write('Installation has not started. No TV packages were changed by this attempt.')
        diagnostics.suggest_issue(write, store, args.command, profile, phase, exc, tv_info)
        return 2
    except Exception as exc:
        write.heading('Could not complete this step')
        kind = type(exc).__name__
        hints = {
            'BadHostKeyException': 'TV identity changed since the last trusted connection. cytv stopped before sign-in. If you reset the TV or changed SSH, verify that change through your existing trusted setup before connecting again.',
            'AuthenticationException': 'SSH authentication failed. Check your key/password; for No-root check Developer Mode and Key Server.',
            'ModuleNotFoundError': 'Source dependencies are missing. Install cytv/requirements.txt or use a built cytv executable.',
        }
        write('Could not read the TV applications. Keep the TV on and accept its pairing request. Installation has not started.'
              if phase in ('pair-tv', 'read-inventory') and kind != 'ModuleNotFoundError' else hints.get(kind, 'Operation could not be confirmed. Check TV connectivity and run cytv status or cytv doctor. Retain local and TV recovery state; do not retry blindly.'))
        diagnostics.suggest_issue(write, store, args.command, profile, phase, exc, tv_info)
        return 1
    finally:
        if remote is not None:
            remote.close()


def entry():
    # Keep the console visible when a frozen Windows executable is opened from Explorer.
    launched_without_args = getattr(sys, 'frozen', False) and sys.platform == 'win32' and len(sys.argv) == 1
    code = main()
    if launched_without_args:
        try:
            input('\nPress Enter to close…')
        except (EOFError, KeyboardInterrupt):
            pass
    return code
