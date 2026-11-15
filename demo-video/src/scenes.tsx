import {AbsoluteFill, Easing, Img, Interactive, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import {Backdrop, Brand, Count, Detail, ease, Heading, Phone, SourceNote, Topline} from './components';

export const Hook = () => {
 const frame=useCurrentFrame();
 return <AbsoluteFill><Backdrop/>
  <div style={{position:'absolute',left:110,top:68}}><Brand/></div>
  <Interactive.Div name="Opening question" style={{position:'absolute',left:110,top:265,fontFamily:'Georgia',fontSize:104,lineHeight:1.08,letterSpacing:-4,width:1250,opacity:interpolate(frame,[0,20],[0,1],ease),translate:interpolate(frame,[0,30],['0px 30px','0px 0px'],ease)}}>Where is my<br/>money going?</Interactive.Div>
  <Interactive.Div name="Values question" style={{position:'absolute',left:115,top:560,fontSize:48,color:'#B3DEC0',opacity:interpolate(frame,[82,110],[0,1],ease)}}>And is it going where I believe?</Interactive.Div>
  <div style={{position:'absolute',left:115,top:710,width:interpolate(frame,[115,195],[0,1020],ease),height:2,background:'#B3DEC0'}}/>
  <Interactive.Div name="Three financial concerns" style={{position:'absolute',left:115,top:752,fontSize:25,letterSpacing:4,color:'#DFF3E3',opacity:interpolate(frame,[130,160],[0,1],ease)}}>EVERYDAY SPENDING  /  ZAKAT  /  INVESTING</Interactive.Div>
 </AbsoluteFill>;
};

export const Introduction = () => {
 const frame=useCurrentFrame();
 return <AbsoluteFill><Backdrop/><Topline chapter="01 / The idea"/>
  <Heading style={{top:260,width:570,fontSize:88}}>Your money.<br/>Your values.<br/><span style={{color:'#B3DEC0'}}>One place.</span></Heading>
  <Interactive.Div name="Product proposition" style={{position:'absolute',left:115,top:610,width:470,fontSize:30,lineHeight:1.55,color:'#D4E6D8'}}>Islamic personal finance,<br/>built around everyday life.</Interactive.Div>
  <div style={{position:'absolute',left:650,top:190,width:1180,height:738,overflow:'hidden',borderRadius:26,border:'1px solid #6D8C77',boxShadow:'0 35px 90px #001A1360',scale:interpolate(frame,[0,280],[.96,1.02],{...ease,easing:Easing.linear})}}>
    <Video name="Actual desktop application" src={staticFile('recordings/desktop.mp4')} muted style={{width:'100%',height:'100%'}}/>
  </div>
  <SourceNote>Authenticated local app · Amina Rahman is a fictional demo profile</SourceNote>
 </AbsoluteFill>;
};

export const Dashboard = () => {
 const {fps}=useVideoConfig();
 return <AbsoluteFill><Backdrop light/><Topline chapter="02 / Everyday clarity" light/>
  <Heading light style={{top:165,width:1060,fontSize:78}}>Know what’s available.</Heading>
  <div style={{position:'absolute',left:115,top:290,display:'flex',gap:65,color:'#073B2C'}}>
   <div><div style={{fontSize:22,color:'#5D7065',marginBottom:6}}>NOVEMBER INCOME</div><div style={{fontSize:62,fontWeight:700}}>$4,500</div></div>
   <div style={{fontSize:45,paddingTop:35,color:'#72947C'}}>−</div>
   <div><div style={{fontSize:22,color:'#5D7065',marginBottom:6}}>EXPENSES</div><div style={{fontSize:62,fontWeight:700}}>$2,850</div></div>
   <div style={{fontSize:45,paddingTop:35,color:'#72947C'}}>=</div>
   <div><div style={{fontSize:22,color:'#5D7065',marginBottom:6}}>SURPLUS</div><div style={{fontSize:62,fontWeight:700}}><Count value={1650}/></div></div>
  </div>
  <Sequence name="Financial overview magnification" durationInFrames={10*fps}><Detail src="dashboard-detail" top={475} height={280} width={1030} sourceWidth={900} y={-365} label="NOVEMBER 2026 · RECORDED APP DETAIL"/></Sequence>
  <Sequence name="Expense categories magnification" from={10*fps}><Detail src="spending" top={445} height={365} width={1030} sourceWidth={920} y={-260} label="RECORDED SPENDING BREAKDOWN"/></Sequence>
  <Sequence name="Actual month selection" durationInFrames={11*fps}><Phone src="dashboard" width={420} top={135} left={1310}/></Sequence>
  <Sequence name="Actual spending and transactions" from={11*fps}><Phone src="spending" width={420} top={135} left={1310}/></Sequence>
  <SourceNote light>Change the month. Explore categories. Keep the record.<br/>Balances persist after refresh · No live bank feed</SourceNote>
 </AbsoluteFill>;
};

const ZakatCalculation = () => <AbsoluteFill><Backdrop/><Topline chapter="03 / Zakat & giving"/>
 <Heading style={{top:170,fontSize:82}}>A calculation.<br/><span style={{color:'#B3DEC0'}}>With its assumptions.</span></Heading>
 <div style={{position:'absolute',left:115,top:425,width:1020,borderTop:'1px solid #53775E',paddingTop:30}}>
  <div style={{fontSize:24,color:'#B3DEC0',letterSpacing:2}}>DECLARED ELIGIBLE WEALTH × ASSUMED RATE</div>
  <div style={{fontSize:70,fontFamily:'Manrope',marginTop:22,letterSpacing:-2}}>$15,000 <span style={{color:'#B3DEC0'}}>× 2.5%</span></div>
  <div style={{fontSize:118,fontFamily:'Manrope',fontWeight:700,marginTop:12,color:'#DFF3E3'}}>= $375</div>
 </div>
 <div style={{position:'absolute',left:115,top:760,fontSize:27,lineHeight:1.55,color:'#D4E6D8'}}>Eligibility assumed · Lunar year attested<br/>Manual nisab: $5,000 — fictional, not a live threshold</div>
 <Phone src="zakat" top={130} left={1300} width={420}/>
 <SourceNote>Deterministic arithmetic, not AI · Educational estimate, not a religious ruling</SourceNote>
</AbsoluteFill>;

const Giving = () => <AbsoluteFill><Backdrop light/><Topline chapter="03 / Zakat & giving" light/>
 <Heading light style={{top:210,width:1000}}>Giving,<br/>remembered.</Heading>
 <div style={{position:'absolute',left:115,top:450,fontSize:110,fontWeight:700,color:'#073B2C'}}>$125</div>
 <div style={{position:'absolute',left:120,top:590,fontSize:30,lineHeight:1.55,color:'#5D7065'}}>Two recorded contributions.<br/>A history of intention put into action.</div>
 <Phone src="giving" top={125} left={1270} width={420}/>
 <SourceNote light>Fictional giving records · No money collected or transferred</SourceNote>
</AbsoluteFill>;

export const Zakat = () => {
 const {fps}=useVideoConfig();
 return <AbsoluteFill><Sequence name="Save real zakat calculation" durationInFrames={12*fps}><ZakatCalculation/></Sequence><Sequence name="Recorded sadaqah history" from={12*fps}><Giving/></Sequence></AbsoluteFill>;
};

export const Portfolio = () => {
 const frame=useCurrentFrame();
 return <AbsoluteFill><Backdrop light/><Topline chapter="04 / Investment awareness" light/>
  <Heading light style={{top:180,width:1050}}>See your holdings.<br/>Know the limits.</Heading>
  <div style={{position:'absolute',left:115,top:415,fontSize:92,fontWeight:700,color:'#073B2C'}}><Count value={8500}/></div>
  <div style={{position:'absolute',left:120,top:525,fontSize:24,color:'#5D7065'}}>MANUALLY VALUED · USD</div>
  <div style={{position:'absolute',left:120,top:600,width:925}}>
   <div style={{display:'flex',height:34,gap:4,borderRadius:5,overflow:'hidden',width:interpolate(frame,[10,50],[0,925],ease)}}><div style={{background:'#0B7750',width:'58.82%'}}/><div style={{background:'#7DAF88',width:'29.41%'}}/><div style={{background:'#C4DDB6',width:'11.77%'}}/></div>
   <div style={{display:'flex',justifyContent:'space-between',marginTop:18,color:'#31533F',fontSize:22}}><span>DEMO-A · 58.82%</span><span>DEMO-B · 29.41%</span><span>DEMO-C · 11.76%</span></div>
  </div>
  <div style={{position:'absolute',left:120,top:735,fontSize:30,color:'#7B5542',borderTop:'1px solid #CCD9C6',paddingTop:26,width:925}}>Screening: unverified. Not a halal certification.</div>
  <Phone src="portfolio" top={130} left={1310} width={420}/>
  <SourceNote light>Fictional manual quotes dated 15 Nov 2026 · No live prices or brokerage execution</SourceNote>
 </AbsoluteFill>;
};

const AIStatus = () => {
 const {fps}=useVideoConfig();
 return <AbsoluteFill><Backdrop/><Topline chapter="05 / AI — tested honestly"/>
  <div style={{position:'absolute',left:135,top:130,width:420,height:812,borderRadius:32,overflow:'hidden',border:'7px solid #08231B',boxShadow:'0 32px 60px #001A1350'}}>
   <Video name="Real local click to pinned-model response" src={staticFile('recordings/ai-live.mp4')} durationInFrames={177} muted style={{width:'100%',height:'100%'}}/>
   <Sequence name="Actual response screenshot reading hold" from={5.9*fps}><Img name="Actual local assistant response" src={staticFile('screenshots/ai-live.png')} style={{width:'100%',height:'100%'}}/></Sequence>
  </div>
  <Heading style={{left:710,top:190,width:1040,fontSize:76}}>Local AI connected.<br/><span style={{color:'#B3DEC0'}}>Advice unverified.</span></Heading>
  <Interactive.Div name="Real private inference path" style={{position:'absolute',left:715,top:425,width:1020,fontSize:32,lineHeight:1.65,color:'#DFF3E3'}}>Browser → backend → pinned model<br/>Private local service · Not hosted</Interactive.Div>
  <Interactive.Div name="Pinned live model identity" style={{position:'absolute',left:715,top:565,width:1040,fontSize:25,lineHeight:1.7,color:'#B3DEC0'}}>h8notme/barakah1<br/>Revision 912a5697cf9d85adf065ee512f509cfa236459d4</Interactive.Div>
  <Interactive.Div name="Public AI distinction" style={{position:'absolute',left:710,top:710,width:1000,padding:'24px 30px',border:'1px solid #B09068',borderRadius:18,background:'#294234',color:'#F1DCB7',fontSize:29,lineHeight:1.5}}>Public AI remains unavailable.<br/><span style={{fontSize:23}}>barakah-gamma.vercel.app</span></Interactive.Div>
 </AbsoluteFill>;
};

const LiveAdviceFailure = () => <AbsoluteFill><Backdrop light/><Topline chapter="05 / What the model actually did" light/>
 <Heading light style={{top:145,fontSize:70,width:1650}}>Connected does not mean trustworthy.</Heading>
 <Detail src="ai-live" top={260} height={600} width={880} sourceWidth={880} y={-735} label="ACTUAL LOCAL RESPONSE · SCREENSHOT DETAIL"/>
 <Interactive.Div name="Observed no-interest instruction failure" style={{position:'absolute',left:1060,top:275,width:740,fontSize:35,lineHeight:1.4,color:'#073B2C'}}>Surplus: $825 — correct.<br/><span style={{color:'#8B4137'}}>Still recommends high-yield savings,<br/>despite no-interest instructions.</span></Interactive.Div>
 <Interactive.Div name="Exact real follow-up excerpt" style={{position:'absolute',left:1060,top:480,width:740,fontSize:29,lineHeight:1.45,color:'#31533F'}}>FOLLOW-UP · $200 TO PARENTS<br/><span style={{fontFamily:'Georgia',fontSize:35}}>“Since this is a personal transfer, it does not affect your own emergency fund strategy.”</span></Interactive.Div>
 <Interactive.Div name="Corrected monthly surplus" style={{position:'absolute',left:1060,top:720,width:740,fontSize:33,lineHeight:1.5,color:'#8B4137'}}>Available monthly surplus should be<br/><b>$825 − $200 = $625.</b></Interactive.Div>
 <SourceNote light>Real local output · 15 Nov 2026 · Exact follow-up excerpt: reports/ai-live-evidence.json<br/>Observed advice failure, not improved safety · Public AI unavailable</SourceNote>
</AbsoluteFill>;

export const AIAssistant = () => {
 const {fps}=useVideoConfig();
 return <AbsoluteFill><Sequence name="Genuine local assistant connection" durationInFrames={12*fps}><AIStatus/></Sequence><Sequence name="Current local advice failure evidence" from={12*fps}><LiveAdviceFailure/></Sequence></AbsoluteFill>;
};

export const Evaluation = () => <AbsoluteFill><Backdrop/><Topline chapter="06 / Evidence, not promises"/>
 <Heading style={{top:155,fontSize:76,width:1650}}>Measure the model. Keep the limits visible.</Heading>
 <div style={{position:'absolute',left:120,top:310,width:780}}>
  <Interactive.Div name="Current numeric comparison scope" style={{fontSize:24,color:'#B3DEC0',letterSpacing:2}}>40 MATCHED NUMERIC TASKS</Interactive.Div>
  <Interactive.Div name="Original baseline numeric score" style={{fontSize:32,marginTop:42}}>Original LFM3-1.7B <span style={{float:'right',fontFamily:'Manrope',fontSize:58}}>36/40</span></Interactive.Div>
  <Interactive.Div name="Candidate numeric score" style={{fontSize:32,marginTop:58}}>Barakah candidate <span style={{float:'right',fontFamily:'Manrope',fontSize:58}}>32/40</span></Interactive.Div>
 </div>
 <div style={{position:'absolute',left:1010,top:310,width:790,borderLeft:'1px solid #53775E',paddingLeft:55}}>
  <Interactive.Div name="Matched rules comparison scope" style={{fontSize:24,color:'#B3DEC0',letterSpacing:2}}>SAME 15-TASK ZAKAT SUBSET</Interactive.Div>
  <Interactive.Div name="Simple rules zakat score" style={{fontSize:32,marginTop:42}}>Simple rules <span style={{float:'right',fontFamily:'Manrope',fontSize:58}}>15/15</span></Interactive.Div>
  <Interactive.Div name="Candidate matched zakat score" style={{fontSize:32,marginTop:58}}>Barakah candidate <span style={{float:'right',fontFamily:'Manrope',fontSize:58}}>11/15</span></Interactive.Div>
 </div>
 <Interactive.Div name="No superiority conclusion" style={{position:'absolute',left:120,top:630,width:1680,borderTop:'1px solid #53775E',paddingTop:30,fontSize:33,color:'#E7CC9E'}}>No demonstrated advantage over the original model or simple rules.</Interactive.Div>
 <Interactive.Div name="Unreviewed conceptual answers" style={{position:'absolute',left:120,top:735,width:1680,fontSize:30,color:'#DFF3E3'}}>100 authored questions · 40 numeric checks · 60 conceptual answers unreviewed</Interactive.Div>
 <SourceNote>Current matched runs · 15 Nov 2026 · Small, single-run evaluation.<br/>Neutral benchmark prompt differs from app prompt · No verified advice or safety gain.</SourceNote>
</AbsoluteFill>;

export const Closing = () => {
 const frame=useCurrentFrame();
 return <AbsoluteFill><Backdrop/>
  <div style={{position:'absolute',top:230,width:'100%',display:'flex',justifyContent:'center',opacity:interpolate(frame,[0,30],[0,1],ease),translate:interpolate(frame,[0,35],['0px 24px','0px 0px'],ease)}}><Brand large/></div>
  <Interactive.Div name="Final positioning" style={{position:'absolute',top:440,left:280,width:1360,textAlign:'center',fontFamily:'Georgia',fontSize:76,lineHeight:1.15,letterSpacing:-2}}>A clearer way to manage money<br/><span style={{color:'#B3DEC0'}}>around what matters.</span></Interactive.Div>
  <Interactive.Div name="Honest prototype status" style={{position:'absolute',top:695,left:300,width:1320,textAlign:'center',fontSize:28,color:'#DFF3E3'}}>Local AI connected · Advice unverified · Public AI unavailable</Interactive.Div>
  <Interactive.Div name="Finance disclaimer" style={{position:'absolute',top:774,left:300,width:1320,textAlign:'center',fontSize:23,color:'#B3CDBB'}}>This project is a prototype and is not financial advice.</Interactive.Div>
 </AbsoluteFill>;
};

export const Thumbnail = () => <AbsoluteFill style={{color:'#FCFBF7',fontFamily:'DM Sans'}}><Backdrop/>
 <div style={{position:'absolute',left:110,top:105}}><Brand large/></div>
 <div style={{position:'absolute',left:115,top:330,fontFamily:'Georgia',fontSize:112,lineHeight:1.02,letterSpacing:-4}}>Your money.<br/><span style={{color:'#B3DEC0'}}>Your values.</span></div>
 <div style={{position:'absolute',left:120,top:650,fontSize:34,color:'#DFF3E3'}}>A real product. An honest demonstration.</div>
 <div style={{position:'absolute',left:120,top:790,fontSize:25,color:'#B3DEC0'}}>PERSONAL FINANCE PROTOTYPE · 1:55</div>
 <Phone src="dashboard" still left={1320} top={70} width={465}/>
 <Img src={staticFile('screenshots/zakat.png')} style={{position:'absolute',left:1050,top:375,width:310,borderRadius:24,boxShadow:'0 25px 60px #001A1380',border:'5px solid #315C45'}}/>
</AbsoluteFill>;
