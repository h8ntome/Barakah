import {Composition, Still} from 'remotion';
import {BarakahDemo} from './BarakahDemo';
import {Thumbnail} from './scenes';

export const RemotionRoot = () => <>
 <Composition id="BarakahDemo" component={BarakahDemo} durationInFrames={3450} fps={30} width={1920} height={1080}/>
 <Still id="Thumbnail" component={Thumbnail} width={1920} height={1080}/>
</>;
