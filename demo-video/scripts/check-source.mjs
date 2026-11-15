import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import ts from 'typescript';
const captions=JSON.parse(readFileSync('assets/audio/captions.json','utf8'));
for(let i=0;i<captions.length;i++){
 assert(captions[i].startMs>=0&&captions[i].endMs<=115000);
 assert(captions[i].endMs>captions[i].startMs);
 if(i)assert(captions[i].startMs>=captions[i-1].endMs);
}
assert.equal([8,10,16,17,14,26,16,8].reduce((a,b)=>a+b),115);
for(const clip of ['desktop','dashboard','spending','zakat','giving','portfolio','ai-live'])assert(existsSync(`assets/recordings/${clip}.mp4`));
assert(readFileSync('src/Root.tsx','utf8').includes('durationInFrames={3450}'));
// Release claims must stay tied to actual local output and matched comparisons.
const scenes=readFileSync('src/scenes.tsx','utf8');
const narration=JSON.parse(readFileSync('scripts/narration.json','utf8'));
assert.deepEqual(captions.map(c=>c.text),narration.map(c=>c.text));
assert.deepEqual(captions.map(c=>c.startMs),narration.map(c=>Math.round(c.start*1000)));
const live=JSON.parse(readFileSync('reports/ai-live-evidence.json','utf8'));
assert.equal(live.responses[0].body.metadata.model,'h8notme/barakah1');
assert.equal(live.responses[0].body.metadata.revision,'912a5697cf9d85adf065ee512f509cfa236459d4');
assert(live.responses[0].body.response.text.includes('With a monthly surplus of $825, a high-yield savings account'));
assert(live.responses[1].body.response.text.includes('Since this is a personal transfer, it does not affect your own emergency fund strategy.'));
assert.equal(3100-2275-200,625);
assert(existsSync('assets/screenshots/ai-live.png'));
for(const text of ['36/40','32/40','15/15','11/15','60 conceptual answers unreviewed','Neutral benchmark prompt differs from app prompt','Public AI unavailable','Advice unverified','durationInFrames={177}'])assert(scenes.includes(text),text);
assert(!/No model connected|Integration pending|AI integration pending|12\/15/.test(scenes));
const comparisons=JSON.parse(readFileSync('reports/release-comparisons.json','utf8'));
for(const [key,n,baseline,candidate] of [['numeric',40,36,32],['rules',15,15,11]]){
 const c=comparisons[key];assert.equal(c.paired_numeric_n,n);
 assert.equal(Math.round(c.numeric_correctness.baseline*n),baseline);
 assert.equal(Math.round(c.numeric_correctness.candidate*n),candidate);
 if(existsSync(c.source))assert.equal(createHash('sha256').update(readFileSync(c.source)).digest('hex'),c.sha256);
}
assert.equal(comparisons.numeric.candidate,comparisons.rules.candidate);
// Test the actual render-only scheduler shim with deterministic fake clocks.
const compiled=ts.transpileModule(readFileSync('src/render-clock.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
function harness(rendering){
 let next=0;const native=new Map(),timers=new Map();
 const window={requestAnimationFrame:cb=>{const id=++next;native.set(id,cb);return id;},cancelAnimationFrame:id=>native.delete(id)};
 const original=window.requestAnimationFrame;
 vm.runInNewContext(compiled,{exports:{},require:()=>({getRemotionEnvironment:()=>({isRendering:rendering})}),window,performance:{now:()=>123},setTimeout:cb=>{const id=++next;timers.set(id,cb);return id;},clearTimeout:id=>timers.delete(id)});
 return {window,native,timers,original};
}
{
 const h=harness(false);assert.equal(h.window.requestAnimationFrame,h.original);
}
{
 const h=harness(true);let calls=0;
 const id=h.window.requestAnimationFrame(()=>calls++);
 const originalCallback=h.native.get(id);
 [...h.timers.values()][0]();originalCallback(124);
 assert.equal(calls,1);assert.equal(h.timers.size,0);assert.equal(h.native.size,0);
}
{
 const h=harness(true);let calls=0;
 const id=h.window.requestAnimationFrame(()=>calls++);h.native.get(id)(100);
 assert.equal(calls,1);assert.equal(h.timers.size,0);
 const cancelled=h.window.requestAnimationFrame(()=>calls++);h.window.cancelAnimationFrame(cancelled);
 assert.equal(h.timers.size,0);assert.equal(h.native.size,0);assert.equal(calls,1);
}
console.log('PASS: 115-second timeline, caption bounds, assets, current live evidence and matched numeric/rules claims, rAF fallback/native/cancel/nonrender paths');
