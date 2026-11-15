import React from 'react';
import {AbsoluteFill, Easing, Img, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';

export const ease = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const, easing: Easing.bezier(.16, 1, .3, 1)};

export const Backdrop = ({light = false}: {light?: boolean}) => <AbsoluteFill style={{background:light?'#FCFBF7':'#062D23',color:light?'#10241D':'#FCFBF7',fontFamily:'DM Sans',overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:light?'radial-gradient(ellipse at 90% 10%, #DFF3E3 0, transparent 60%)':'radial-gradient(ellipse at 85% 20%, #18563E 0, transparent 65%)'}} />
  <svg width="1920" height="1080" style={{position:'absolute',opacity:light?.12:.15}} viewBox="0 0 1920 1080">
    <path d="M1120 1080V510C1120 270 1340 160 1530 -20C1720 160 1940 270 1940 510V1080" stroke="#B3DEC0" strokeWidth="1" fill="none" />
    <path d="M1060 1080V510C1060 240 1320 90 1530 -90C1740 90 2000 240 2000 510V1080" stroke="#B3DEC0" strokeWidth="1" fill="none" />
  </svg>
</AbsoluteFill>;

export const Brand = ({dark=false,large=false}: {dark?:boolean;large?:boolean}) => <div style={{display:'flex',alignItems:'center',gap:large?28:14,color:dark?'#073B2C':'#FCFBF7'}}>
  <Img src={staticFile('graphics/barakah-mark.svg')} style={{width:large?88:40,height:large?95:44}} />
  <span style={{fontFamily:'Georgia',fontSize:large?100:41,letterSpacing:large?-4:-1}}>Barakah</span>
</div>;

export const Topline = ({chapter,light=false}: {chapter:string;light?:boolean}) => <div style={{position:'absolute',top:46,left:90,right:90,display:'flex',alignItems:'center',justifyContent:'space-between',color:light?'#073B2C':'#DFF3E3'}}>
  <Brand dark={light}/><div style={{fontSize:20,letterSpacing:2,textTransform:'uppercase'}}>{chapter}</div><div style={{fontSize:20,border:`1px solid ${light?'#B3DEC0':'#4A735C'}`,padding:'10px 18px',borderRadius:30}}>Prototype · Synthetic data</div>
</div>;

export const Heading = ({children,light=false,style={}}: {children:React.ReactNode;light?:boolean;style?:React.CSSProperties}) => {
 const frame=useCurrentFrame();
 return <Interactive.Div name="Scene headline" style={{position:'absolute',left:110,top:180,width:890,fontFamily:'Georgia',fontWeight:400,fontSize:86,lineHeight:1.06,letterSpacing:-3,color:light?'#073B2C':'#FCFBF7',opacity:interpolate(frame,[5,28],[0,1],ease),translate:interpolate(frame,[0,32],['0px 28px','0px 0px'],ease),...style}}>{children}</Interactive.Div>;
};

export const Phone = ({src,still=false,left=1250,top=130,width=420,trim=0}: {src:string;still?:boolean;left?:number;top?:number;width?:number;trim?:number}) => {
 const frame=useCurrentFrame(); const {fps}=useVideoConfig();
 return <div style={{position:'absolute',left,top,width,height:width*850/440,padding:7,boxSizing:'content-box',background:'#08231B',border:'1px solid #668573',borderRadius:32,boxShadow:'0 32px 60px #001A1350',overflow:'hidden',translate:interpolate(frame,[0,35],['0px 18px','0px 0px'],ease)}}>
  <div style={{borderRadius:25,overflow:'hidden',width:'100%',height:'100%'}}>
   {still?<Img src={staticFile(`screenshots/${src}.png`)} style={{width:'100%',height:'100%'}}/>:<Video name="Actual authenticated app recording" src={staticFile(`recordings/${src}.mp4`)} trimBefore={trim*fps} muted style={{width:'100%',height:'100%'}}/>}
  </div>
 </div>;
};

export const Detail = ({src,left=110,top=420,width=1030,height=430,sourceWidth=1030,y=0,label='ACTUAL APP · DETAIL'}: {src:string;left?:number;top?:number;width?:number;height?:number;sourceWidth?:number;y?:number;label?:string}) => <div style={{position:'absolute',left,top,width,height,borderRadius:20,background:'#FCFBF7',boxShadow:'0 22px 65px #001A1320',overflow:'hidden',border:'1px solid #D2DFD2'}}>
 <Img src={staticFile(`screenshots/${src}.png`)} style={{position:'absolute',width:sourceWidth,top:y,left:(width-sourceWidth)/2}}/>
 <div style={{position:'absolute',left:0,top:0,width:'100%',height:38,background:'#E3EFE3',color:'#31533F',display:'flex',alignItems:'center',paddingLeft:22,fontSize:15,letterSpacing:1.5}}>{label}</div>
</div>;

export const Count = ({value,prefix='$'}: {value:number;prefix?:string})=>{
 const frame=useCurrentFrame();
 const n=Math.round(interpolate(frame,[8,42],[0,value],ease));
 return <span style={{fontFamily:'Manrope',fontVariantNumeric:'tabular-nums'}}>{prefix}{n.toLocaleString('en-US')}</span>;
};

export const SourceNote = ({children,light=false}: {children:React.ReactNode;light?:boolean}) => <div style={{position:'absolute',left:110,bottom:145,fontSize:20,color:light?'#526C5C':'#AAC9B6',maxWidth:1010,lineHeight:1.45}}>{children}</div>;
