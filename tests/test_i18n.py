"""t() returns the key itself when it misses, so a typo is invisible at runtime.
These tests are what makes it visible."""
import string

import pytest

from lib.i18n import MESSAGES, get_lang, t

LANGS = ('en', 'es')


def placeholders(template):
    return {f for _, f, _, _ in string.Formatter().parse(template) if f}


@pytest.mark.parametrize('key', sorted(MESSAGES))
def test_every_key_has_both_languages(key):
    assert set(MESSAGES[key]) >= set(LANGS), f'{key} is missing a translation'


@pytest.mark.parametrize('key', sorted(MESSAGES))
def test_translations_agree_on_placeholders(key):
    """A Spanish string that drops {reason} loses it silently for Spanish users."""
    found = {lang: placeholders(MESSAGES[key][lang]) for lang in LANGS}
    assert found['en'] == found['es'], f'{key}: {found}'


@pytest.mark.parametrize('key', sorted(MESSAGES))
def test_templates_render(key):
    values = {name: 'x' for name in placeholders(MESSAGES[key]['en'])}
    for lang in LANGS:
        assert t(lang, key, **values)


def test_unknown_locale_falls_back_to_english():
    assert get_lang('fr') == 'en'
    assert get_lang('es-ES') == 'es'


def test_missing_key_returns_the_key():
    assert t('en', 'no_such_key_anywhere') == 'no_such_key_anywhere'
