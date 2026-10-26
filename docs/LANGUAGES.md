# 中文 / Languages / Sprachen / Idiomas / Langues / Lingue / 언어 / भाषाएँ / Języki / Языки

Choose a complete user guide for installation, everyday controls, recovery,
updates and removal. Technical/developer references remain in English and are
linked at the end of each guide.

These twelve guides describe **[v1.2.0 stable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.2.0)**, with candidate-only behavior identified separately. Latest-download links follow the published release. Hardware evidence and outstanding tests remain scoped to the recorded devices and components; see [compatibility](COMPATIBILITY.md) and [release notes](RELEASE-1.2.0.md).

Published v1.2.0 supports the original ten languages below. The unreleased 1.3.0
candidate adds Simplified and Traditional Chinese across Home, Root Home, both
updaters and the desktop/console, Android and Homebrew installers. The Android preview
supports language selection. It follows the phone language on first launch (English fallback); tap the current language code at the top right to choose and save another language.

| Language | Code | User guide |
| --- | --- | --- |
| English | `en` | [English](i18n/en.md) |
| Deutsch | `de` | [Deutsch](i18n/de.md) |
| Español | `es` | [Español](i18n/es.md) |
| Português (Brasil) | `pt-BR` | [Português (Brasil)](i18n/pt-BR.md) |
| Français | `fr` | [Français](i18n/fr.md) |
| Italiano | `it` | [Italiano](i18n/it.md) |
| 한국어 | `ko` | [한국어](i18n/ko.md) |
| हिन्दी | `hi` | [हिन्दी](i18n/hi.md) |
| Polski | `pl` | [Polski](i18n/pl.md) |
| Русский | `ru` | [Русский](i18n/ru.md) |
| 简体中文 (candidate) | `zh-Hans` | [简体中文](i18n/zh-Hans.md) |
| 繁體中文 (candidate) | `zh-Hant` | [繁體中文](i18n/zh-Hant.md) |

The installer starts with the computer's language; the TV interface starts with
the TV's language. Each offers a saved language choice and an automatic/system
option. These preferences are independent. CLI examples use `--language CODE`;
application identifiers, file names and command verbs are not translated.

[Project overview](../README.md) · [Desktop packages](DESKTOP_INSTALL.md) · [CLI reference](CLI.md)

For Chinese, an explicit Hans/Hant script takes precedence over the region.
Bare `zh`, CN and SG use Simplified; TW, HK and MO use Traditional. You can
override the automatic result in the existing language picker. Chinese TV
rendering on the final candidate still needs physical-device acceptance.
