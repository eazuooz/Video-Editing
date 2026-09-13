import {Node,Txt,Video,makeScene2D} from '@motion-canvas/2d';
import {all,createRef,createSignal,tween,usePlayback} from '@motion-canvas/core';
import {STORYBOARD} from '../storyboard';
import {SCENE_DURATIONS} from '../timing';
import manifest from '../../../../../projects/ai-era-cs-fundamentals/project.json';
import footage from '../../../../../projects/ai-era-cs-fundamentals/sources/selected-footage.json';
import {PAPER} from '../../../styles/research-paper';
import {explain} from './concepts';
import {memeAside} from './memes';

export const EXAMPLE_SECONDS=manifest.editing.exampleSeconds;
const files=import.meta.glob('../assets/broll/*.mp4',{eager:true,query:'?url',import:'default'}) as Record<string,string>;
const EXAMPLE_LABELS=[
  'Godot 편집기 · 실제 게임 제작 화면','인디 게임 프로토타입 · 구현과 검증',
  'Python 디버깅 시연','컬렉션·자료구조 강연','요구사항과 설계 흐름',
  'GDScript 코딩 연습 · 직접 작성하고 실행하기','테트리스 실제 플레이 · 이동과 줄 삭제',
  '테스트 실패 출력과 수정','게임 처리 비용 측정 예시 · AI 요금 화면 아님','게임 루프 연결 · 실행하고 완성하기',
  '로컬 개발 도구 시연 · 오프라인 녹화라는 뜻은 아님','직접 만든 2D 게임 · 결과 확인과 플레이 테스트',
];
class MixedVideo extends Video {
  protected override video():HTMLVideoElement {const element=super.video();element.muted=true;return element;}
}
export function makeReviewScene(index:number) {
  return makeScene2D(function* (view) {
    const scene=STORYBOARD[index],source=footage.clips[index];
    const src=files[`../assets/broll/scene${scene.id}.mp4`];
    if(!src)throw Error(`Missing licensed clip ${scene.id}`);
    const example=createRef<Node>(),clip=createRef<MixedVideo>(),time=createSignal(0);
    const credit=()=>{
      let remaining=time();
      const segment=source.segments.find(s=>{if(remaining<s.duration)return true;remaining-=s.duration;return false;})||source.segments[source.segments.length-1];
      return footage.clips.find(c=>c.scene===segment.sourceScene)!.credit;
    };
    view.fill(PAPER.background);
    view.add(<Node ref={example}>
      <Txt text={`${scene.id} / 12  ·  ${EXAMPLE_LABELS[index]}`} x={-864} y={-510} offset={[-1,0]} fontFamily={PAPER.font} fontSize={23} fill={PAPER.muted}/>
      <MixedVideo ref={clip} src={src} width={1664} height={936} y={-10}/>
      <Txt text={credit} y={500} width={1740} textWrap fontFamily={PAPER.font} fontSize={21} fill={PAPER.muted}/>
    </Node>);
    // Await metadata/frame resources without advancing the scene clock. A cold
    // render must not read the duration before the media node is ready.
    yield clip();
    clip().play();
    yield* tween(EXAMPLE_SECONDS-.25,v=>time(v*(EXAMPLE_SECONDS-.25)));
    yield* example().opacity(0,.25);clip().pause();example().remove();
    const stage=createRef<Node>();
    view.add(<Node ref={stage}>
      <Txt text={`${scene.id} · AI 시대의 컴퓨터공학`} x={-864} y={-477} offset={[-1,0]} fontFamily={PAPER.font} fontSize={25} fill={PAPER.muted}/>
      <Txt text={scene.title} x={-864} y={-405} offset={[-1,0]} fontFamily={PAPER.font} fontSize={50} fontWeight={600} fill={PAPER.ink}/>
      <Txt text={manifest.audio.mixStatus==='narration-source-ready-bgm-pending'?`v${manifest.scriptRevision} 전체 TTS 검토본 · 작은 원음 · Blue Dream 적용 대기`:manifest.audio.mixStatus==='final'?'AI 시대의 컴퓨터공학':['full-mix-awaiting-listening-review','full-mix-license-pending'].includes(manifest.audio.mixStatus)?`v${manifest.scriptRevision} 청취 검토본 · 내레이션 + 작은 원음 + BGM · 게시 전 권리 확인`:'새 내레이션 제작 중 · 현재 화면 타이밍 갱신 대기'} x={-864} y={507} offset={[-1,0]} fontFamily={PAPER.font} fontSize={20} fill={PAPER.muted}/>
      <Txt text={`${scene.id} / 12`} x={864} y={507} offset={[1,0]} fontFamily={PAPER.font} fontSize={22} fill={PAPER.muted}/>
    </Node>);
    // Scene retirement consumes one frame. Compensate at the active preview /
    // export rate so twelve scenes don't accumulate drift against WAV and SRT.
    const retireFrame=usePlayback().framesToSeconds(1);
    yield* all(explain(stage(),index,Math.max(1,SCENE_DURATIONS[index]-EXAMPLE_SECONDS-retireFrame)),memeAside(stage(),index,manifest.editing.memeSeconds));
  });
}
