import {spawnSync} from 'node:child_process';
import {existsSync,renameSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
function run(cmd,args,timeout=1200000){
 const r=spawnSync(cmd,args,{cwd:root,stdio:'inherit',timeout});
 if(r.error||r.status!==0)throw r.error??new Error(`${cmd} exited ${r.status}`);
}
run('npx',['tsc','--noEmit']);
run('node',['scripts/check-source.mjs']);
run('npx',['remotion','render','src/index.ts','BarakahDemo','output/barakah-demo-candidate.mp4','--codec=h264','--crf=18','--audio-codec=aac','--audio-bitrate=192k','--concurrency=2']);
run('python3',['scripts/validate-video.py','output/barakah-demo-candidate.mp4','CANDIDATE_VALIDATION']);
// Never delete a working master before the replacement has passed validation.
if(existsSync(path.join(root,'output/barakah-demo-final.mp4'))){
 renameSync(path.join(root,'output/barakah-demo-final.mp4'),path.join(root,'output/barakah-demo-previous.mp4'));
}
renameSync(path.join(root,'output/barakah-demo-candidate.mp4'),path.join(root,'output/barakah-demo-final.mp4'));
run('python3',['scripts/validate-video.py']);
run('ffmpeg',['-y','-v','error','-i','output/barakah-demo-final.mp4','-vf','scale=1280:720','-c:v','libx264','-crf','26','-preset','medium','-c:a','aac','-b:a','128k','-movflags','+faststart','output/barakah-demo-preview.mp4']);
run('npx',['remotion','still','src/index.ts','Thumbnail','output/thumbnail.png','--image-format=png']);
console.log('Validated final MP4, 720p preview and thumbnail saved.');
