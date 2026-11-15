#!/usr/bin/env python3
"""Local-only independent ASR check of intelligibility and spoken timing."""
import json,pathlib,subprocess
import numpy as np
from faster_whisper import WhisperModel
ROOT=pathlib.Path(__file__).resolve().parents[1]
model=WhisperModel('tiny.en',device='cpu',compute_type='int8',download_root=str(ROOT/'.runtime/whisper'))
# Decode with FFmpeg: PyAV 19 removed metadata_errors used by faster-whisper 1.2.
pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'output/barakah-demo-final.mp4'),'-vn','-ar','16000','-ac','1','-f','f32le','-'])
audio=np.frombuffer(pcm,dtype=np.float32)
segments,info=model.transcribe(audio,beam_size=5,word_timestamps=True,language='en')
rows=[]
for s in segments:
 rows.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word} for w in (s.words or [])]})
 print(f'{s.start:.2f}–{s.end:.2f} {s.text}',flush=True)
(ROOT/'reports/audio-asr-review.json').write_text(json.dumps({'model':'Systran/faster-whisper-tiny.en','purpose':'local ASR QA, not product model or ground truth','duration':info.duration,'segments':rows},indent=2))
