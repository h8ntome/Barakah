#!/usr/bin/env python3
"""Record real UI states and input with agent-browser; no intercepted/mock API replies."""
import datetime, json, pathlib, subprocess, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
SESSION = 'barakah-film-capture'
BROWSER = ['bash', str(ROOT/'scripts/browser.sh'), '--session', SESSION]
LOG = []

def b(*args):
    p = subprocess.run(BROWSER + list(args), capture_output=True, text=True, timeout=40)
    if p.returncode: raise RuntimeError(f'{args[0]}: {p.stdout} {p.stderr}')
    return p.stdout

def click(selector): b('click', selector)
def text(selector='body'): return b('get', 'text', selector)
def hold(seconds): time.sleep(seconds)
def scroll(region, top):
    b('eval', f'document.querySelector({json.dumps(region)}).scrollTo({{top:{top},behavior:"smooth"}})')
    hold(.8)
def shot(name):
    b('screenshot', str(ROOT/f'assets/screenshots/{name}.png'))
    (ROOT/f'reports/{name}-ui.txt').write_text(text())
def record(name):
    path=ROOT/f'assets/recordings/{name}.mp4'
    if path.exists(): path.unlink() # Only explicitly selected take; final MP4 untouched.
    b('record','start',str(path),'--fps','30','--cursor')
def stop(name):
    b('record','stop')
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(ROOT/f'assets/recordings/{name}.mp4')]))
    assert float(data['format']['duration']) > 1
    LOG.append({'clip':name,'duration':float(data['format']['duration'])})
def nav(n): click(f'nav[aria-label="Main navigation"] button:nth-child({n})'); hold(.5)
def findbutton(name): b('find','role','button','click','--name',name,'--exact')
def month(value):
    # Native month input is not supported by this agent-browser fill build.
    b('eval', f'(()=>{{const e=document.querySelector("input[type=month]"); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(e,{json.dumps(value)}); e.dispatchEvent(new Event("input",{{bubbles:true}}));e.dispatchEvent(new Event("change",{{bubbles:true}}));}})()')

def main():
    with urllib.request.urlopen('http://127.0.0.1:8095/api/v1/health') as r:
        assert json.load(r)['database']=='available'
    b('open','http://127.0.0.1:8095')
    b('set','viewport','440','850','2')
    record('login'); hold(1); findbutton('Try Demo'); hold(3)
    assert '$4,500.00' in text()
    stop('login')
    findbutton('Settings')
    b('find','label','Display name','fill','Amina Rahman')
    findbutton('Save settings'); hold(.5); b('reload'); b('wait','--load','networkidle')
    assert 'Amina Rahman' in text()
    shot('dashboard')
    record('dashboard'); hold(2)
    # Actual supported date-range interaction and resulting prior-month totals.
    month('2026-10'); hold(2)
    assert '$4,200.00' in text()
    month('2026-11'); hold(2)
    assert '$1,650.00' in text()
    scroll('.home-screen',230); hold(4); shot('dashboard-detail'); stop('dashboard')
    record('spending'); scroll('.home-screen',490); hold(4); shot('spending');
    findbutton('Transactions'); hold(3); shot('transactions'); stop('spending')
    nav(3); scroll('section[aria-label=Zakat] .screen-content',0)
    shot('zakat'); record('zakat'); hold(2)
    # Preserve the existing coherent fixture; calculate it using the real form.
    findbutton('Save and calculate zakat'); hold(1.5)
    assert 'calculated by the server' in text()
    scroll('section[aria-label=Zakat] .screen-content',0); hold(3)
    assert '$375.00' in text('section[aria-label=Zakat]')
    findbutton('Save calculation to history'); hold(1.5)
    shot('zakat-saved'); stop('zakat')
    nav(5); b('find','text','Sadaqah history','click','--exact')
    scroll('section[aria-label=Give] .screen-content',10000)
    hold(.5); shot('giving-history'); record('giving'); hold(3)
    # Real history browsing; no money moved and no new transaction fabricated.
    scroll('section[aria-label=Give] .screen-content',640); hold(2)
    scroll('section[aria-label=Give] .screen-content',10000); hold(3); stop('giving')
    assert '$125.00' in text()
    nav(2); shot('invest'); record('portfolio'); hold(2)
    scroll('section[aria-label=Invest] .screen-content',350); hold(3); shot('holdings')
    scroll('section[aria-label=Invest] .screen-content',0); findbutton('Learn'); hold(3); shot('invest-learn'); stop('portfolio')
    nav(4); shot('ai-before'); record('ai-unavailable'); hold(1)
    b('find','label','Message to advisor','fill',"I have $12,000 in savings and I’m planning for Hajj next year. How should I think about zakat and keeping that money safe?")
    hold(2); findbutton('Send message'); hold(2)
    assert 'No message was saved. Your draft is kept' in text()
    scroll('.chat-scroll',10000); hold(5); shot('ai-unavailable'); stop('ai-unavailable')
    nav(1); scroll('.home-screen',0); findbutton('Overview')
    scroll('.home-screen',0)
    b('set','viewport','1440','900','1'); hold(.8); shot('desktop')
    record('desktop'); hold(5); stop('desktop')
    # Reload proves authenticated persistence, not just in-memory React state.
    b('reload'); b('wait','--load','networkidle')
    assert 'Amina Rahman' in text() and '$23,500.00' in text()
    LOG.append({'persistence':'profile and seeded dashboard survive refresh','ai':'genuine 503 unavailable; no inference'})
    (ROOT/'reports/browser-errors.txt').write_text(b('errors'))
    (ROOT/'reports/browser-console.txt').write_text(b('console'))
    (ROOT/'reports/browser-network.txt').write_text(b('network','requests'))

try:
    main()
finally:
    (ROOT/'reports/capture-log.json').write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'steps':LOG},indent=2))
    b('close')
