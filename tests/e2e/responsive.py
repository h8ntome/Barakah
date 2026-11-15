"""Chromium viewport/layout checks for every destination; no physical-device claim."""
import json
from urllib.parse import urlparse
import journey as j


def main():
    assert urlparse(j.URL).hostname in {'127.0.0.1', 'localhost', '::1'}
    j.browser('open', j.URL); j.click('Try Demo'); j.wait('Welcome to Barakah.')
    for width, height in [(1280, 900), (768, 1024), (390, 844), (320, 740)]:
        j.browser('set', 'viewport', str(width), str(height))
        for index, name in enumerate(['home', 'invest', 'zakat', 'chat', 'give'], 1):
            j.browser('click', f'.bottom-nav button:nth-child({index})')
            j.browser('eval', "document.querySelectorAll('.screen-page:not([hidden]) .screen-content, .screen-page:not([hidden]) .chat-scroll').forEach(x=>x.scrollTop=0)")
            assert j.browser('eval', 'document.documentElement.scrollWidth > innerWidth') == 'false', (width, name)
            # Each persistent navigation target remains reachable and at least 44px high.
            assert j.browser('eval', "Array.from(document.querySelectorAll('.bottom-nav button')).every(x => x.getBoundingClientRect().height >= 44 && x.getBoundingClientRect().bottom <= innerHeight + 1)") == 'true'
            j.checks.append(f'{name} at {width}px: no overflow and navigation reachable')
            if width in (1280, 390) or name == 'home': j.screenshot(f'{name}-{width}.png')
    j.browser('eval', "document.querySelector('.bottom-nav button').focus()")
    j.browser('press', 'Tab')
    assert j.browser('eval', "document.activeElement === document.querySelector('.bottom-nav button:nth-child(2)')") == 'true'
    j.checks.append('keyboard focus moves to an interactive control')
    assert not j.browser('errors').strip()
    j.checks.append('no uncaught browser exceptions across destinations')
    print(json.dumps({'passed': len(j.checks), 'failed': 0, 'checks': j.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    finally:
        j.browser('close')
