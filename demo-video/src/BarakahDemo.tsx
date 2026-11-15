import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {AIAssistant, Closing, Dashboard, Evaluation, Hook, Introduction, Portfolio, Zakat} from './scenes';
import {BasicCaptions} from './basic-captions.element';
import captions from '../assets/audio/captions.json';
import './styles.css';

export const BarakahDemo = () => {
 const {fps}=useVideoConfig();
 const [handle]=useState(()=>delayRender('Load Barakah fonts'));
 useEffect(()=>{Promise.all([document.fonts.load('400 40px "DM Sans"'),document.fonts.load('700 40px Manrope')]).then(()=>continueRender(handle));},[handle]);
 return <AbsoluteFill style={{background:'#062D23',fontFamily:'DM Sans',color:'#FCFBF7'}}>
  <TransitionSeries name="Eight editorial scenes">
   <TransitionSeries.Sequence name="Hook" durationInFrames={8*fps+12}><Hook/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Introduce Barakah" durationInFrames={10*fps+12}><Introduction/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Financial dashboard" durationInFrames={16*fps+12}><Dashboard/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Zakat and giving" durationInFrames={17*fps+12}><Zakat/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Shariah-conscious portfolio tracking" durationInFrames={14*fps+12}><Portfolio/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Local AI and observed advice failure" durationInFrames={26*fps+12}><AIAssistant/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Engineering evaluation" durationInFrames={16*fps+12}><Evaluation/></TransitionSeries.Sequence>
   <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>
   <TransitionSeries.Sequence name="Closing" durationInFrames={8*fps}><Closing/></TransitionSeries.Sequence>
  </TransitionSeries>
  <Audio name="Narration and original stereo score" src={staticFile('audio/final-mix.wav')} />
  <div className="film-captions" style={{position:'absolute',left:180,bottom:30,width:1560,height:105,pointerEvents:'none'}}>
   <BasicCaptions name="Phrase-aligned narration captions" width={2600} captions={captions} combineTokensWithinMilliseconds={0} style={{position:'absolute',bottom:0,left:0,scale:.6,transformOrigin:'left bottom'}}/>
  </div>
 </AbsoluteFill>;
};
