import unittest

from cytv.terminal import Console


class TerminalTests(unittest.TestCase):
    def test_plain_output_has_hierarchy_and_wraps_to_small_terminal(self):
        lines = []
        ui = Console(lines.append, width=42, interactive=False)
        ui.step(2, 'Choose your edition')
        ui.option('1', 'No-root', 'For a TV without root. Uses LG Developer Mode.')
        self.assertIn('STEP 2 / 4', '\n'.join(lines))
        self.assertIn('[1] No-root', '\n'.join(lines))
        self.assertNotIn('\x1b', '\n'.join(lines))
        self.assertTrue(all(len(line) <= 42 for text in lines for line in text.splitlines()))
        self.assertTrue(ui.prompt('Edition [1]: ').startswith('\n  > '))

    def test_real_terminal_starts_new_step_without_erasing_scrollback(self):
        lines = []
        ui = Console(lines.append, width=72, interactive=True, color=True)
        ui.step(2, 'Choose your edition')
        self.assertIn('\x1b[2J\x1b[H', '\n'.join(lines))
        self.assertNotIn('\x1b[3J', '\n'.join(lines))
        self.assertTrue(lines[0].startswith('\n\n'))
        self.assertIn('\x1b[1m', '\n'.join(lines))


if __name__ == '__main__':
    unittest.main()
