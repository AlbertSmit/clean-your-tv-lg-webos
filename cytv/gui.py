"""Windowed cytv wizard. Run with python -m cytv.gui."""
import html
from pathlib import Path
import shutil
import sys
import threading

from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout,
                              QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar,
                              QPushButton, QTextBrowser, QVBoxLayout, QWidget)

from cytv import __version__, cli, diagnostics
from cytv.desktop import Channel


class Events(QObject):
    event = Signal(str, object)


class Wizard(QMainWindow):
    def __init__(self, run=cli.main):
        super().__init__()
        self.run = run
        self.running = False
        self.pending = None
        self.report = None
        self.worker = None
        self.setWindowTitle('Clean Your TV')
        self.resize(820, 740)
        self.setMinimumSize(620, 540)
        self.events = Events()
        self.events.event.connect(self.receive)
        body = QWidget()
        self.setCentralWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        brand = QLabel('CLEAN YOUR TV')
        brand.setStyleSheet('font-weight: 700; letter-spacing: 2px; color: #385db3;')
        layout.addWidget(brand)
        self.title = QLabel('Make your TV feel like yours')
        self.title.setWordWrap(True)
        self.title.setStyleSheet('font-size: 26px; font-weight: 700;')
        layout.addWidget(self.title)
        self.subtitle = QLabel('Install Root or No-root. We will help you choose.')
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)
        self.content = QTextBrowser()
        self.content.setOpenExternalLinks(False)
        self.content.setFrameShape(QFrame.Shape.NoFrame)
        self.content.document().setDefaultStyleSheet('p { margin-bottom: 12px; } h3 { margin-top: 20px; }')
        layout.addWidget(self.content, 1)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.form = QWidget()
        self.form_layout = QVBoxLayout(self.form)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        layout.addWidget(self.form)
        footer = QHBoxLayout()
        footer.addWidget(QLabel('cytv ' + __version__))
        footer.addStretch()
        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(self.close)
        footer.addWidget(self.cancel)
        layout.addLayout(footer)
        self.home()

    def clear_form(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

    def button(self, label, callback, default=False):
        button = QPushButton(label)
        button.setMinimumHeight(38)
        button.setDefault(default)
        if default:
            button.setStyleSheet('QPushButton { background: #315fc4; color: white; border: none; border-radius: 6px; padding: 8px; } QPushButton:focus { border: 2px solid #163775; }')
        button.clicked.connect(callback)
        self.form_layout.addWidget(button)
        return button

    def home(self):
        self.clear_form()
        self.title.setText('Make your TV feel like yours')
        self.subtitle.setText('Install Root or No-root. We will help you choose.')
        self.content.setHtml('<h3>Before you begin</h3><p>Turn on your LG webOS TV and connect it to the same home network as this computer.</p><p>cytv will look for your TV automatically. Keep the remote nearby to approve pairing on the TV.</p>')
        self.button('Set up my TV', lambda: self.start('install'), True)
        actions = QComboBox()
        actions.setAccessibleName('Maintenance action')
        for label, command in [('Check TV status', 'status'), ('Check connection and create a diagnostic report', 'doctor'), ('Return to LG Home', 'restore'), ('Uninstall Clean Your TV', 'uninstall')]:
            actions.addItem(label, command)
        self.form_layout.addWidget(actions)
        self.button('Run selected maintenance action', lambda: self.start(actions.currentData()))

    def start(self, command):
        if self.running:
            return
        self.running = True
        self.report = None
        self.pending = None
        self.content.clear()
        self.clear_form()
        self.title.setText('Connecting to your TV')
        self.subtitle.setText('Keep your TV on and watch for a pairing request.')
        self.cancel.setText('Cancel')
        self.cancel.setEnabled(False)
        self.progress.show()
        self.channel = Channel(self.events.event.emit)
        def work():
            try:
                args = [command, '--report'] if command == 'doctor' else [command]
                code = self.run(args, ask=self.channel.ask, secret=self.channel.secret, write=self.channel.console)
            except Exception:
                # Startup/storage errors outside cli.main's handler must stay visible,
                # without exposing exception text that could contain credentials.
                self.events.event.emit('heading', 'Could not start this operation')
                self.events.event.emit('text', 'Check that your user account can write to its application data folder. You can report this problem using Open an issue below.')
                code = 1
            self.events.event.emit('done', code)
        self.worker = threading.Thread(target=work, name='cytv-install', daemon=False)
        self.worker.start()

    def receive(self, kind, value):
        if kind == 'step':
            number, title, clear = value
            self.title.setText(title)
            self.subtitle.setText(f'Step {number} of 4')
            if clear:
                self.content.clear()
        elif kind in ('text', 'heading'):
            text = str(value)
            if kind == 'text' and text.endswith('.json') and 'diagnostic-' in text:
                path = Path(text.strip())
                if path.is_file():
                    self.report = path
            tag = 'h3' if kind == 'heading' else 'p'
            self.content.append(f'<{tag}>' + html.escape(text).replace('\n', '<br>') + f'</{tag}>')
        elif kind == 'prompt':
            self.show_prompt(value)
        elif kind == 'done':
            self.running = False
            self.pending = None
            self.progress.hide()
            self.cancel.setText('Close')
            self.cancel.setEnabled(True)
            self.clear_form()
            self.title.setText('Finished' if value == 0 else 'Cancelled' if value == 130 else 'Let’s resolve this')
            self.subtitle.setText('Read the result below before continuing.')
            self.content.moveCursor(self.content.textCursor().MoveOperation.End)
            if self.report:
                self.button('Save diagnostic report…', self.save_report)
            if value not in (0, 130):
                self.button('Open an issue', lambda: QDesktopServices.openUrl(QUrl(diagnostics.ISSUE_URL)))
            self.button('Back to start', self.home)

    def show_prompt(self, prompt):
        self.pending = prompt
        self.progress.hide()
        self.cancel.setEnabled(True)
        self.clear_form()
        label = QLabel(prompt.title)
        label.setWordWrap(True)
        label.setStyleSheet('font-weight: 600;')
        self.form_layout.addWidget(label)
        if prompt.kind == 'confirm':
            yes = self.button('Connect and remember' if prompt.label.startswith('Connect') else 'Continue', lambda: self.submit('y'), prompt.default == 'y')
            no = self.button('No, go back / cancel this operation', lambda: self.submit('n'), prompt.default == 'n')
            (yes if prompt.default == 'y' else no).setFocus()
            if prompt.label.startswith('Connect'):
                self.button('Connection details', lambda: self.submit('?'))
        elif prompt.kind == 'choice':
            choices = QComboBox()
            choices.setAccessibleName(prompt.title)
            for key, name, detail in prompt.options:
                choices.addItem(name + (' — ' + detail if detail else ''), key)
                if key == prompt.default:
                    choices.setCurrentIndex(choices.count() - 1)
            self.form_layout.addWidget(choices)
            self.button('Continue', lambda: self.submit(choices.currentData()), True)
            choices.setFocus()
            if prompt.label.startswith('TV number'):
                # Saved-TV menus also use this label; retry is offered only for discovery.
                if any(name == 'Enter an IP address manually' for _, name, _ in prompt.options):
                    self.button('Search again', lambda: self.submit('r'))
        elif prompt.kind == 'ready':
            self.button('TV is on — check again', lambda: self.submit(''), True).setFocus()
        else:
            entry = QLineEdit()
            entry.setAccessibleName(prompt.title)
            label.setBuddy(entry)
            if prompt.secret:
                entry.setEchoMode(QLineEdit.EchoMode.Password)
            elif 'IP address' in prompt.label:
                entry.setPlaceholderText('For example, 192.168.1.50')
            self.form_layout.addWidget(entry)
            def submit_entry():
                value = entry.text()
                entry.clear()
                self.submit(value)
            entry.returnPressed.connect(submit_entry)
            self.button('Continue', submit_entry, True)
            if prompt.kind == 'file':
                def choose_file():
                    filename, _ = QFileDialog.getOpenFileName(self, 'Choose your existing SSH private key')
                    if filename:
                        entry.setText(filename)
                self.button('Choose key file…', choose_file)
            if 'IP address' in prompt.label:
                self.button('Search again', lambda: self.submit('r'))
                self.button('Help finding my TV', lambda: self.submit('?'))
            entry.setFocus()

    def submit(self, value):
        if not self.pending:
            return
        self.pending = None
        self.clear_form()
        self.cancel.setEnabled(False)
        self.progress.show()
        self.channel.answer(value)

    def save_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save diagnostic report', self.report.name, 'JSON (*.json)')
        if filename:
            try:
                if Path(filename).resolve() != self.report.resolve():
                    shutil.copyfile(self.report, filename)
            except OSError:
                QMessageBox.warning(self, 'Could not save report', 'Choose another folder and try again.')

    def closeEvent(self, event):
        if self.running:
            event.ignore()
            if self.pending:
                self.submit(None)
            else:
                QMessageBox.information(self, 'Operation in progress', 'Please wait for this step to finish. This keeps installation and recovery data consistent.')
        else:
            event.accept()


def main():
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Clean Your TV')
    app.setOrganizationName('CleanYourTV')
    app.setWindowIcon(QIcon(str(cli.payload_dir() / 'fallback.png')))
    app.setStyleSheet('QWidget { font-size: 14px; } QTextBrowser { padding: 8px; } QLineEdit, QComboBox { padding: 8px; }')
    window = Wizard()
    window.show()
    if '--smoke-test' in sys.argv:
        QTimer.singleShot(200, app.quit)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
