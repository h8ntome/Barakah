#!/usr/bin/env python3
"""Decode the whole export, check media limits, and measure audio/black-frame defects."""
import hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
path=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'output/barakah-demo-final.mp4'
name=sys.argv[2] if len(sys.argv)>2 else 'VALIDATION'
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True,timeout=300)
metadata=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]).stdout)
v=next(s for s in metadata['streams'] if s['codec_type']=='video')
a=next(s for s in metadata['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080)
assert v['r_frame_rate']=='30/1' and int(v['nb_read_frames'])==3450
assert v['pix_fmt']=='yuv420p'
duration=float(metadata['format']['duration']);assert 114.9<=duration<=120
assert a['codec_name']=='aac' and a['channels']==2 and a['sample_rate']=='48000'
decode=run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'])
assert not decode.stderr.strip(),decode.stderr
black=run(['ffmpeg','-hide_banner','-i',str(path),'-vf','blackdetect=d=0.03:pix_th=0.02:pic_th=0.99','-an','-f','null','-']).stderr
assert 'black_start:' not in black,'Unintended black frame detected'
audio=run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']).stderr
measure=json.loads(audio[audio.rfind('{'):audio.rfind('}')+1])
assert float(measure['input_tp'])<=-.8,measure
assert -19<=float(measure['input_i'])<=-13,measure
silence=run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','silencedetect=noise=-60dB:d=1','-f','null','-']).stderr
silence_events=[l for l in silence.splitlines() if 'silence_start:' in l or 'silence_end:' in l]
assert not silence_events,silence_events
report={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duration_seconds':duration,'video_duration_seconds':float(v['duration']),'resolution':[1920,1080],'fps':'30/1','frames_decoded':int(v['nb_read_frames']),'file_bytes':path.stat().st_size,'video_codec':v['codec_name'],'pixel_format':v['pix_fmt'],'audio_codec':a['codec_name'],'audio_sample_rate':int(a['sample_rate']),'audio_channels':a['channels'],'audio_loudness':measure,'complete_decode':'PASS','black_frames':'none detected at 99% black / 0.02 threshold','silence_longer_than_1s_below_minus60dB':silence_events}
(ROOT/f'reports/{name}.json').write_text(json.dumps(report,indent=2))
(ROOT/f'reports/{name}.md').write_text(f'''# Export validation\n\n- File: `{path.name}`\n- Container duration: **{duration:.3f} seconds**; video exactly **{float(v['duration']):.3f} seconds**. Under 120 seconds.\n- Resolution / frame rate: **1920 × 1080 / 30 fps**.\n- Frames: **{v['nb_read_frames']}**, all decoded successfully.\n- File size: **{path.stat().st_size:,} bytes**.\n- Video: H.264, yuv420p. Audio: AAC stereo, 48 kHz.\n- Integrated loudness: **{measure['input_i']} LUFS**; true peak: **{measure['input_tp']} dBTP**.\n- Full decode: no errors. No near-total black frames. No silence below −60 dB lasting a second.\n- SHA256: `{report['sha256']}`\n\nThese are machine measurements, not a substitute for visual/playback review. See `FINAL_RELEASE.md` and `CLAIMS_AND_EVIDENCE.md` for current review and content limitations; earlier review reports are labeled historical. Intentional reading holds and static archival excerpts are not frame-drop claims.\n''')
print(json.dumps(report,indent=2))
