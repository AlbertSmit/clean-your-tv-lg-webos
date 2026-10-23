"""Offline widget checks; never connect to a TV."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import time
import unittest
from unittest.mock import patch
from pathlib import Path
try:
    from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QComboBox
    from cytv.gui import Wizard
    from cytv.desktop import Prompt
    HAS_QT = True
except ImportError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, 'Desktop build dependencies are optional for CLI tests')
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from cytv import i18n
        self.addCleanup(i18n.set_language, 'en')
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        prefs = patch('cytv.state.default_dir', return_value=Path(self.directory.name))
        prefs.start()
        self.addCleanup(prefs.stop)
        languages = patch('cytv.i18n.system_languages', return_value=['en'])
        languages.start()
        self.addCleanup(languages.stop)

    def test_language_selection_rerenders_and_persists_all_locales(self):
        from cytv import i18n
        w = Wizard()
        for code in i18n.LANGUAGES:
            w.language.setCurrentIndex(list(i18n.LANGUAGES).index(code))
            self.assertEqual(i18n.language_choice(), code)
            self.assertEqual(i18n.configure(), i18n.resolve_language(code))
            if code not in ('en', 'auto'):
                self.assertNotEqual(w.title.text(), 'Make your TV feel like yours')
        w.close()

    def test_translated_secret_and_confirmation_keep_semantics(self):
        from cytv import i18n
        w = Wizard()
        w.language.setCurrentIndex(list(i18n.LANGUAGES).index('ru'))
        w.show_prompt(Prompt('Connect and remember this TV? [Y/n]: '))
        self.assertTrue(any(b.isDefault() and 'Подключиться' in b.text() for b in w.form.findChildren(QPushButton)))
        w.show_prompt(Prompt('SSH key passphrase: ', secret=True))
        self.assertEqual(w.form.findChild(QLineEdit).echoMode(), QLineEdit.EchoMode.Password)
        w.close()

    def test_failed_language_save_keeps_visible_and_active_selection(self):
        from cytv import i18n
        w = Wizard()
        old_index = w.language.currentIndex()
        old_title = w.title.text()
        with patch('cytv.state.private_write', side_effect=OSError('read only')), patch('cytv.gui.QMessageBox.warning'):
            w.language.setCurrentIndex(list(i18n.LANGUAGES).index('ru'))
        self.assertEqual(w.language.currentIndex(), old_index)
        self.assertEqual(i18n.language_choice(), 'auto')
        self.assertEqual(i18n.resolved_language(), 'en')
        self.assertEqual(w.title.text(), old_title)
        w.close()

    def pump(self, predicate):
        deadline = time.monotonic() + 3
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.005)
        self.assertTrue(predicate())

    def test_worker_prompt_and_completion(self):
        answers = []
        def runner(argv, ask, secret, write):
            write.step(2, 'Choose your edition')
            write.option(1, 'No-root')
            write.option(2, 'Root')
            answers.append(ask('Edition [2]: '))
            answers.append(secret('Password: '))
            write.heading('Root is ready')
            return 0
        w = Wizard(run=runner)
        w.start('install')
        self.pump(lambda: w.pending is not None)
        combo = w.form.findChild(QComboBox)
        self.assertEqual(combo.currentData(), '2')
        w.submit(combo.currentData())
        self.pump(lambda: w.pending is not None)
        self.assertEqual(w.form.findChild(QLineEdit).echoMode(), QLineEdit.EchoMode.Password)
        w.submit('private-password')
        self.pump(lambda: not w.running)
        self.assertEqual(answers, ['2', 'private-password'])
        self.assertNotIn('private-password', w.content.toPlainText())
        self.assertIn('Root is ready', w.content.toPlainText())
        w.close()

    def test_close_cancels_prompt_without_killing_worker(self):
        def runner(argv, ask, secret, write):
            try:
                ask('TV IP address: ')
            except EOFError:
                write('Cancelled. No TV changes were made.')
                return 130
        w = Wizard(run=runner)
        w.start('install')
        self.pump(lambda: w.pending is not None)
        w.close()
        self.pump(lambda: not w.running)
        self.assertEqual(w.title.text(), 'Cancelled')
        w.close()

    def test_real_cli_cancel_never_connects(self):
        from cytv.cli import main
        with tempfile.TemporaryDirectory() as directory:
            def runner(argv, **kwargs):
                return main(argv + ['--data-dir', directory], search=lambda: [], **kwargs)
            w = Wizard(run=runner)
            w.start('install')
            self.pump(lambda: w.pending is not None)
            w.submit(None)
            self.pump(lambda: not w.running)
            self.assertEqual(w.title.text(), 'Cancelled')
            w.close()

    def test_destructive_confirm_focuses_no(self):
        w = Wizard()
        w.show_prompt(Prompt('Continue [y/N]: '))
        buttons = w.form.findChildren(QPushButton)
        defaults = [b.text() for b in buttons if b.isDefault()]
        self.assertEqual(defaults, ['No, go back / cancel this operation'])
        w.close()
