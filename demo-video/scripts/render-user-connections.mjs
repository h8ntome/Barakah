import {spawnSync} from 'node:child_process';
import {existsSync, mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const browserExecutable=process.env.REMOTION_BROWSER_EXECUTABLE;
if(browserExecutable&&!existsSync(browserExecutable))throw new Error('Configured browser executable does not exist');
const rawOutput='output/user-connections-review/barakah-demo-user-connections-candidate-v2.mp4';
const output='output/user-connections-review/barakah-demo-user-connections-yuv420p-v2.mp4';
// This review lane must never promote a render or replace a historical export.
for(const file of [rawOutput,output])if(existsSync(path.join(root,file)))throw new Error(`Refusing to overwrite ${file}`);
mkdirSync(path.dirname(path.join(root,output)),{recursive:true});
function run(cmd,args,timeout=1200000){
 const result=spawnSync(cmd,args,{cwd:root,stdio:'inherit',timeout});
 if(result.error||result.status!==0)throw result.error??new Error(`${cmd} exited ${result.status}`);
}
run('npx',['tsc','--noEmit']);
run('node',['scripts/check-source.mjs']);
run('npx',['remotion','render','src/index.ts','BarakahDemo',rawOutput,'--codec=h264','--crf=18','--audio-codec=aac','--audio-bitrate=192k','--concurrency=2','--is-production=false','--disable-shared-memory-capture',...(browserExecutable?[`--browser-executable=${browserExecutable}`]:[])]);
// JPEG capture can yield full-range yuvj420p; explicitly convert range for portable playback.
run('ffmpeg',['-n','-v','error','-i',rawOutput,'-vf','scale=in_range=auto:out_range=tv','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-color_range','tv','-c:a','copy','-movflags','+faststart',output]);
run('python3',['scripts/validate-video.py',output,'USER_CONNECTIONS_V2_VALIDATION']);
console.log(`Review candidate only: ${output}. No promotion or historical export changes.`);
