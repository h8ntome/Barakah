#!/usr/bin/env python3
"""Licensed stock TTS voice + original synthesized score; exact phrase-aligned captions."""
import argparse, hashlib, json, pathlib, subprocess
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--candidate', action='store_true', help='Write isolated user-connections review audio and captions')
args=parser.parse_args()
audio_dir=ROOT/('assets/audio/user-connections-review' if args.candidate else 'assets/audio')
output_dir=ROOT/('output/user-connections-review' if args.candidate else 'output')
report_prefix='USER_CONNECTIONS_' if args.candidate else ''
audio_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)
SR=24000
segments=json.loads((ROOT/'scripts/narration.json').read_text())
k=Kokoro(str(ROOT/'.runtime/tts/kokoro-v1.0.onnx'),str(ROOT/'.runtime/tts/voices-v1.0.bin'))
voice=np.zeros(SR*115,dtype=np.float32)
captions=[]; stats=[]
for i,seg in enumerate(segments):
    text=seg['text']
    key=hashlib.sha256(text.encode()).hexdigest()[:10]
    path=ROOT/f'.runtime/tts/line-{i}-{key}.wav'
    if path.exists(): a,rate=sf.read(path,dtype='float32')
    else:
        a,rate=k.create(text,voice='af_heart',speed=.96,lang='en-us')
        sf.write(path,a,rate)
    assert rate==SR
    duration=len(a)/SR; slot=seg['end']-seg['start']
    if duration>slot:
        tempo=duration/(slot-.10)
        assert tempo<=1.22, f'Line {i} too long: shorten narration ({duration}/{slot})'
        fitted=ROOT/'.runtime/tts/fitted.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-af',f'atempo={tempo}',str(fitted)],check=True)
        a,rate=sf.read(fitted,dtype='float32')
        duration=len(a)/SR
    assert duration<=slot+.03, (i,duration,slot)
    n=int(seg['start']*SR); voice[n:n+len(a)]+=a
    caption={'text':text,'startMs':round(seg['start']*1000),'endMs':round((seg['start']+duration)*1000),'timestampMs':None,'confidence':None,'pageBreakAfter':True}
    captions.append(caption);stats.append({'line':i,'duration':duration,'start':seg['start'],'peak':float(np.max(np.abs(a)))})
    print(i,round(duration,2),text,flush=True)
sf.write(audio_dir/'narration.wav',voice,SR)
# An original, restrained harmonic bed. No samples, stock music, or borrowed melody.
t=np.arange(SR*115,dtype=np.float64)/SR
bed=np.zeros((len(t),2))
for j,notes in enumerate([(146.832,220,329.628,369.994),(130.813,196,293.665,329.628),(164.814,220,293.665,369.994),(146.832,220,293.665,440)]*4):
    start=j*8.0; end=min(start+10,115)
    if start>=115:break
    mask=(t>=start)&(t<end);q=t[mask]-start
    env=np.minimum(q/2,1)*np.minimum((end-start-q)/2,1)
    for n,freq in enumerate(notes):
        tone=np.sin(2*np.pi*freq*q+.12*np.sin(2*np.pi*.08*q))+.15*np.sin(2*np.pi*freq*2*q)
        pan=.25+.5*(n/3)
        bed[mask,0]+=tone*env*.0045*(1-pan)
        bed[mask,1]+=tone*env*.0045*pan
# Gentle original title/transition tones; soft attacks, no startling transients.
for start in [0.3,8,18,34,51,65,77,91,107]:
    mask=(t>=start)&(t<start+2.5);q=t[mask]-start
    chime=(np.sin(2*np.pi*587.33*q)+.3*np.sin(2*np.pi*880*q))*np.exp(-2.5*q)*np.minimum(q/.08,1)*.008
    bed[mask]+=chime[:,None]
fade=np.clip(t/2,0,1)*np.clip((115-t)/2,0,1)
bed*=fade[:,None]
sf.write(audio_dir/'original-score.wav',bed,SR,subtype='PCM_24')
mix=voice[:,None]*np.ones((1,2))*.83+bed
assert np.max(np.abs(mix))<.99
sf.write(ROOT/'.runtime/mix.wav',mix,SR,subtype='PCM_24')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'.runtime/mix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-ac','2',str(audio_dir/'final-mix.wav')],check=True)
(audio_dir/'captions.json').write_text(json.dumps(captions,indent=2))
(ROOT/f'reports/{report_prefix}audio-generation.json').write_text(json.dumps({'model':'Kokoro-82M v1.0 ONNX','voice':'af_heart','sample_rate':SR,'segments':stats},indent=2))
def stamp(ms):
    sec,ms=divmod(ms,1000);m,s=divmod(sec,60)
    return f'00:{m:02}:{s:02},{ms:03}'
(output_dir/'barakah-demo-captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["startMs"])} --> {stamp(c["endMs"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n')
(ROOT/f'reports/{report_prefix}NARRATION.md').write_text('# Final narration and captions\n\nStock synthetic voice: Kokoro v1.0 `af_heart`; no custom voice clone. Phrase timings derive from generated PCM, not guessed word timing.\n\n'+'\n\n'.join(f'**{stamp(c["startMs"])} – {stamp(c["endMs"])}**\n{c["text"]}' for c in captions)+'\n')
