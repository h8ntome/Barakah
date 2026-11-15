"""Real, opt-in model/browser check. No mocks. Uses only a fresh fictional demo.
Run against a configured local app: BARAKAH_UI_URL=http://127.0.0.1:8088 python3 tests/e2e/ai_live.py
Optional BARAKAH_AI_RECORDING records the actual request, without speeding up waiting.
"""
import json
import os
from pathlib import Path
import time
from urllib.parse import urlparse
import journey as j

QUESTION = 'I earn USD 3100 monthly and spend USD 2275 on essentials. I want an emergency fund before a holiday. What should I consider? Please be brief.'
FOLLOWUP = 'I also send my parents USD 200 each month. How should I adjust the plan? Please be brief.'


def observe():
    j.browser('eval', 'window.__aiEvidence = []')


def main():
    if urlparse(j.URL).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise SystemExit('Real-AI test is loopback only; never enter private financial information.')
    os.environ['AGENT_BROWSER_INIT_SCRIPTS'] = str(Path(__file__).with_name('observe_ai.js').resolve())
    j.browser('open', j.URL)
    j.click('Try Demo')
    j.wait('Private demo')
    j.click('AI Chat')
    j.wait('AI endpoint configured')
    j.fill('Message to advisor', QUESTION)
    j.click('Send message')
    j.check('saved consent required before sending', 'Save AI consent in Settings')
    j.click('Home'); j.click('Settings')
    j.browser('check', j.ref('I consent to sending my questions and recent conversation history', 'checkbox'))
    j.click('Save AI consent'); j.wait('Saved.')
    j.click('AI Chat')
    j.browser('set', 'viewport', '440', '850', '2')
    observe()
    recording = os.environ.get('BARAKAH_AI_RECORDING')
    if recording:
        j.browser('record', 'start', str(Path(recording).resolve()), '--fps', '30', '--cursor')
    j.fill('Message to advisor', QUESTION)
    j.click('Send message')
    j.browser('wait', '--fn', 'window.__aiEvidence.length === 1')
    evidence = json.loads(j.browser('eval', 'window.__aiEvidence'))
    assert evidence[0]['status'] == 200, evidence[0]
    result = evidence[0]['body']
    assert result['response']['text'].strip() and result['error'] is None
    assert result['metadata']['model'] == 'h8notme/barakah1'
    assert result['metadata']['revision'] == '912a5697cf9d85adf065ee512f509cfa236459d4'
    assert result['metadata']['output_tokens'] > 0
    j.wait('Model response')
    time.sleep(2)  # Hold the genuine result for readable capture, not model polling.
    j.screenshot('ai-live.png')
    if recording:
        j.browser('record', 'stop')
    j.checks.append('real browser-backend-pinned-model response with identity metadata')
    j.fill('Message to advisor', FOLLOWUP); j.click('Send message')
    j.browser('wait', '--fn', 'window.__aiEvidence.length === 2')
    evidence = json.loads(j.browser('eval', 'window.__aiEvidence'))
    j.OUT.mkdir(parents=True, exist_ok=True)
    (j.OUT/'ai-live-responses.json').write_text(json.dumps({'synthetic_inputs': [QUESTION, FOLLOWUP], 'responses': evidence}, indent=2)+'\n')
    second = evidence[1]['body']
    assert evidence[1]['status'] == 200, second
    assert second['conversation_id'] == result['conversation_id']
    assert second['metadata']['input_tokens'] > result['metadata']['input_tokens']
    j.checks.append('real follow-up includes bounded conversation history')
    j.click('New conversation')
    j.wait('No messages yet')
    j.browser('select', j.ref('Conversation history', 'combobox'), result['conversation_id'])
    j.wait(FOLLOWUP)
    j.checks.append('switching conversations restores persisted messages')
    j.browser('reload'); j.browser('wait', '--load', 'networkidle')
    j.wait('Welcome to Barakah.'); j.click('AI Chat')
    j.browser('select', j.ref('Conversation history', 'combobox'), result['conversation_id'])
    j.wait(FOLLOWUP)
    j.checks.append('AI conversation survives full browser reload')
    first_session = j.SESSION
    j.SESSION += '-second'
    try:
        j.browser('open', j.URL); j.click('Try Demo'); j.wait('Private demo'); j.click('AI Chat')
        j.wait('No messages yet')
        assert result['conversation_id'] not in j.browser('get', 'html', j.ref('Conversation history', 'combobox'))
        j.checks.append('separate demo account has no first-account conversation')
    finally:
        j.browser('close'); j.SESSION = first_session
    j.click('Home'); j.click('Settings'); j.click('Sign out'); j.wait('Welcome back.')
    j.checks.append('logout removes AI workspace')
    assert not j.browser('errors').strip()
    j.OUT.mkdir(parents=True, exist_ok=True)
    record = {'synthetic_inputs': [QUESTION, FOLLOWUP], 'responses': evidence, 'checks': j.checks,
              'note': 'Actual browser fetch responses, not mocks. Metadata is service-attested. No auth headers/cookies captured.'}
    (j.OUT/'ai-live.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'passed':len(j.checks), 'failed':0, 'checks':j.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        try:
            j.screenshot('ai-failure.png')
        except Exception:
            pass
        raise
    finally:
        if os.environ.get('BARAKAH_AI_RECORDING'):
            try:
                j.browser('record', 'stop')
            except Exception:
                pass
        j.browser('close')
