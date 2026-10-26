#!/usr/bin/env python3
"""Regenerate static Chinese UI fonts with fonttools==4.60.1 (developer only).

Download the original variable fonts from google/fonts commit
 e7db6ca603fd4862010383ff17ffd6cc4ffac1c0, ofl/notosans{sc,tc}/NotoSans{SC,TC}[wght].ttf.
Pass their directory as the single argument, named NotoSansSC-variable.ttf and
NotoSansTC-variable.ttf. See docs/TV-WEB-BUILD.md for provenance and limits.
"""
import sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('launcher/catalogs.js', 'root-edition/ui/root-locales.js',
           'cytv/translations.py', 'android/app/src/main/assets/ui/translations.js',
           'homebrew/app/i18n.js', 'launcher/i18n.js')


def characters():
    text = ''.join((ROOT / name).read_text() for name in SOURCES)
    text += '年月日星期周一二三四五六天上午下午简体中文繁體中文'
    # Latin, Cyrillic, Hindi and Hangul retain their existing packaged faces.
    return {ord(c) for c in text if 0x2000 <= ord(c) <= 0x9fff or 0xff00 <= ord(c) <= 0xffef}


def main():
    for name in ('SC', 'TC'):
        font = TTFont(Path(sys.argv[1]) / ('NotoSans%s-variable.ttf' % name), recalcTimestamp=False)
        font = instantiateVariableFont(font, {'wght': 400}, inplace=True, updateFontNames=True)
        options = subset.Options()
        options.recalc_timestamp = False
        sub = subset.Subsetter(options=options)
        sub.populate(unicodes=characters())
        sub.subset(font)
        font.save(ROOT / ('launcher/fonts/NotoSans%s.ttf' % name))


if __name__ == '__main__':
    main()
