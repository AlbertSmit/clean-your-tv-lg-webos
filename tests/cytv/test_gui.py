"""Offline widget checks; never connect to a TV."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import time
import unittest
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
