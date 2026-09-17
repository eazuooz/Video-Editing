import {Node, Txt, Video, View2D} from '@motion-canvas/2d';
import {createSignal, tween, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import manifest from '../../../../../projects/visible-rewards/project.json';
import {STORYBOARD} from '../storyboard';
import {RewardWorld} from './reward-world';

const revised=import.meta.glob('../assets/gameplay-v3/scene*.mp4',{eager:true,query:'?url',import:'default'}) as Record<string,string>;
class MixedVideo extends Video {protected override video(){const v=super.video();v.muted=true;return v;}}
const headings=[
 ['딱 300G만 더.','목표가 가까워지는 순간'],
 ['가방이 필요한 이유','하고 싶은 행동이 먼저다'],
 ['현재값에는 목표가 필요하다','1,700G → 2,000G'],
 ['보상은 플레이를 바꾼다','12칸 → 24칸 → 더 챙기기'],
 ['조금 더, 다음 선택까지','수집 → 선택 → 공격의 변화'],
 ['전부 보여주면 잘 보일까?','현재 의도에 맞춰 정보를 줄이기'],
 ['남은 1개 ≠ 사냥 1번','개수와 시도 횟수는 다른 정보'],
 ['보상은 다음 행동의 약속','그 사이의 플레이도 재미있어야 한다'],
 ['만들고 싶은 장비가 있다','목표 장비 → 필요한 소재 → 다음 사냥'],
];

export function* explanation(view:View2D,index:number,seconds:number){
 const time=createSignal(0),root=new Node({opacity:0}),world=new RewardWorld({});
 world.chapter(index);world.clock(time);world.span(seconds);root.add(world);view.add(root);view.fill(P.background);
 root.add(<Txt text={headings[index][0]} y={-426} fontFamily={P.font} fontWeight={700} fontSize={62} fill={P.ink}/>);
 root.add(<Txt text={headings[index][1]} y={-336} fontFamily={P.font} fontSize={32} fill={P.blue}/>);
 // v3: no explanatory footer or reserved caption band. Context remains in narration and publishing notes.
 yield* tween(seconds-1/60,p=>{time(p*seconds);root.opacity(Math.min(1,p*seconds/.4));});
 root.remove();
}

export function* dioramaScene(view:View2D,index:number,duration:number){
 const id=STORYBOARD[index]?.id??'09',seconds=manifest.editing.exampleSeconds;
 const src=revised[`../assets/gameplay-v3/scene${id}.mp4`];
 if(!src)throw new Error(`Missing reviewed gameplay for scene ${id}`);
 const v=new MixedVideo({src,width:1920,height:1080});view.add(v);yield v;v.play();yield* waitFor(seconds);v.pause();v.remove();
 yield* explanation(view,index,duration-seconds);
}
