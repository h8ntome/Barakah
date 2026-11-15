import {getRemotionEnvironment} from 'remotion';

// Chromium 158 on this Mac leaves native rAF pending even on a visible blank page.
// Keep Remotion's bundled browser; a one-shot timer fallback unblocks its handshake.
// Video time still comes exclusively from Remotion frames, never this wall clock.
if (typeof window !== 'undefined' && getRemotionEnvironment().isRendering) {
 const nativeRequest=window.requestAnimationFrame.bind(window);
 const nativeCancel=window.cancelAnimationFrame.bind(window);
 const timers=new Map<number,ReturnType<typeof setTimeout>>();
 window.requestAnimationFrame=(callback)=>{
  let done=false;
  let id=0;
  const run=(time:number)=>{
   if(done)return;
   done=true;
   clearTimeout(timers.get(id));
   timers.delete(id);
   nativeCancel(id);
   callback(time);
  };
  id=nativeRequest(run);
  timers.set(id,setTimeout(()=>run(performance.now()),100));
  return id;
 };
 window.cancelAnimationFrame=(id)=>{
  clearTimeout(timers.get(id));timers.delete(id);nativeCancel(id);
 };
}
