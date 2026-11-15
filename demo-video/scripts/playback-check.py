#!/usr/bin/env python3
"""Uninterrupted local browser playback of the exported master; never publishes it."""
import json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
B=['bash',str(ROOT/'scripts/browser.sh'),'--session','barakah-film-release-20261115']
def b(*args):
 p=subprocess.run(B+list(args),capture_output=True,text=True,timeout=30,check=True)
 return p.stdout
states=[]
try:
 b('open',(ROOT/'output/barakah-demo-final.mp4').as_uri())
 b('set','viewport','1280','720')
 b('eval','(()=>{const v=document.querySelector("video"); v.muted=false; v.currentTime=0; return v.play().then(()=>"playing")})()')
 start=time.monotonic()
 for i in range(13):
  if i:time.sleep(10)
  raw=b('eval','JSON.stringify((()=>{const v=document.querySelector("video"); const q=v.getVideoPlaybackQuality();return {time:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,readyState:v.readyState,error:v.error?.message||null,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames}})())')
  obj=json.loads(raw)
  if isinstance(obj,str):obj=json.loads(obj)
  states.append(obj)
  assert obj['error'] is None,obj
  if i in [2,8,11]:b('screenshot',str(ROOT/f'reports/release-export-frames/playback-{i*10:03}.png'))
  if obj['ended']:break
 assert states[-1]['ended'] and states[-1]['time']>=115,states[-1]
 report={'mode':'uninterrupted real-time browser playback; no seek after start','wall_seconds':time.monotonic()-start,'states':states,'subjective_listening':'not claimed; use local ASR and measured audio checks alongside manual listening'}
 (ROOT/'reports/playback-check.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
finally:b('close')
