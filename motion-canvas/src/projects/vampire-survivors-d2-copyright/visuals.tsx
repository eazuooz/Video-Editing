import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

export interface Diagram {
  kind: string; title: string; duration: number; image?: string; image2?: string;
  cueLabels?: string[]; cueTimes?: number[]; currentPicture?: string;
}
type Point = [number, number];
const smooth = (v: number) => {const x = Math.max(0, Math.min(1, v)); return x * x * (3 - 2 * x);};
const txt = (s: string, x: number, y: number, size = 48, color: string = D.ink) =>
  <Txt text={s} x={x} y={y} fill={color} fontSize={size} fontFamily={D.font} fontWeight={600} lineHeight={size * 1.28}/>;

/** Independently authored conceptual diagrams. No scores, permissions or engine measurements are invented. */
export function* lesson(view: View2D, d: Diagram) {
  const t = createSignal(0);
  const cue = (i: number) => d.cueTimes?.[i] ?? Math.min(d.duration * .12 + i * d.duration * .21, d.duration - .5);
  const reveal = (i: number, delay = 0) => () => smooth((t() - cue(i) - delay) / .55);
  const add = (i: number, node: any) => view.add(<Node opacity={reveal(i)}>{node}</Node>);
  const arrow = (points: Point[], i: number, color: string = D.teal) => view.add(
    <Line points={points} stroke={color} lineWidth={8} endArrow arrowSize={20} end={reveal(i)} lineCap={'round'} lineJoin={'round'}/>,
  );
  const picture = (src: string, x: number, y: number, width: number, i = 0) => add(i,
    <Node x={x} y={y}><Img src={src} width={width} height={width * 9 / 16}/>
      <Rect width={width + 4} height={width * 9 / 16 + 4} stroke={D.line} lineWidth={3}/></Node>,
  );
  view.fill(D.background);
  view.add(txt(d.title, 0, -440, 56, D.title));
  view.add(txt(d.currentPicture ?? '실제 화면 + 해설 도식', 650, -365, 28, D.muted));
  const paired = ['overview', 'power', 'conclusion'].includes(d.kind);
  if (paired && d.image && d.image2) {
    picture(d.image, -440, -65, 790); picture(d.image2, 440, -65, 790);
  } else if (d.image && !['files', 'court', 'permissions', 'puzzle'].includes(d.kind)) {
    picture(d.image, -420, -50, 900);
  }

  if (d.kind === 'overview' || d.kind === 'conclusion') {
    add(0, txt('D2 Survivors', -440, -330, 43));
    add(0, txt('Vampire Survivors', 440, -330, 43));
    add(1, txt('재미의 구조', -440, 245, 52, D.green));
    add(2, txt('이용한 표현과 허락', 440, 245, 52, D.teal));
    arrow([[-230, 245], [170, 245]], 2, D.title);
  } else if (d.kind === 'power') {
    add(0, txt('처음의 공격 범위', -440, -330, 43));
    add(1, txt('성장한 뒤의 화면', 440, -330, 43));
    add(1, txt('적을 피함', -440, 245, 52, D.ink));
    add(2, txt('적을 밀어냄', 440, 245, 52, D.green));
    arrow([[-200, 245], [190, 245]], 2, D.green);
  } else if (d.kind === 'expression') {
    add(0, txt('처치 → 경험치', 515, -245, 49));
    add(0, txt('규칙 · 아이디어', 515, -140, 43, D.teal));
    add(1, <Line points={[[195, -35], [835, -35]]} stroke={D.line} lineWidth={4}/>);
    add(1, txt('특정 그림 · 소리', 515, 75, 49));
    add(1, txt('구체적 표현', 515, 185, 43, D.orange));
  } else if (d.kind === 'files') {
    view.add(txt('같은 파일도, 이용 행위는 구분', 0, -280, 49));
    for (const [i, y, a, b, color] of [
      [0, -95, '내 설치 파일', '내 컴퓨터에서 읽기', D.teal],
      [1, 150, '서버의 호스팅 사본', '다른 이용자에게 제공', D.orange],
    ] as const) {
      add(i, <Node>{txt(a, -470, y, 48, color)}{txt(b, 395, y, 48, color)}</Node>);
      arrow([[-180, y], [65, y]], i, color);
    }
    add(2, txt('위치와 방식의 차이 ≠ 자동 이용허락', 0, 310, 47, D.title));
  } else if (d.kind === 'permissions') {
    const labels = ['무료 배포', '정품 보유', '이용허락'];
    const subs = ['받는 가격', '보유한 사본', '허용된 사용'];
    [-590, 0, 590].forEach((x, i) => {
      add(i, <Node>{txt(labels[i], x, -120, 59, i === 2 ? D.teal : D.ink)}
        <Line points={[[x - 170, -58], [x + 170, -58]]} stroke={i === 2 ? D.teal : D.line} lineWidth={6}/>
        {txt(subs[i], x, 30, 44, D.muted)}</Node>);
    });
    add(2, txt('서로 다른 조건을 확인해야 합니다', 0, 245, 54, D.title));
  } else if (d.kind === 'court') {
    add(0, txt('대법원 2019. 6. 27. 선고', 0, -300, 49));
    add(0, txt('2017다212095', 0, -205, 57, D.title));
    const words = ['선택', '배열', '유기적 조합'];
    [-570, -50, 530].forEach((x, i) => {
      add(i, <Node><Rect x={x} y={35} width={i === 2 ? 430 : 310} height={140} stroke={D.teal} lineWidth={5}/>{txt(words[i], x, 35, 51)}</Node>);
      if (i < 2) arrow([[x + 170, 35], [x + 300, 35]], i + 1);
    });
    add(2, txt('별개 게임 판례 · D2 침해 판결 아님', 0, 265, 45, D.orange));
  } else if (d.kind === 'puzzle') {
    const colors = [D.teal, D.title, D.orange];
    for (let row = 0; row < 3; row++) for (let col = 0; col < 3; col++) {
      const x = -650 + col * 175, y = -220 + row * 175;
      add(0, <Circle x={x} y={y} width={110} height={110} fill={colors[row === 1 ? 1 : (row + col) % 3]}/>);
    }
    add(1, <Rect x={-475} y={-45} width={495} height={140} stroke={D.green} lineWidth={8}/>);
    ['세 개를 맞추는 큰 규칙', '캐릭터 · 효과 · 단계 전개', '선택과 배열의 구체적 결합'].forEach((s,i)=>add(i,txt(s,460,-220+i*195,44,i===2?D.title:D.ink)));
    add(2, txt('두 퍼즐게임의 판례 · D2 판결 아님', 0, 310, 45, D.orange));
  } else if (d.kind === 'notice' || d.kind === 'choices') {
    const labels = d.cueLabels ?? (d.kind === 'notice'
      ? ['비공식 · 블리자드 승인 아님', '무료 제공 · 요청 시 대응 방침', '방침의 고지 ≠ 이용허락 증거']
      : ['조건을 정해 허락', '별도의 자산으로 변경 요청', '자산 이용 중단 요청']);
    labels.forEach((s, i) => add(i, txt(s, 515, -220 + i * 200, 42, i === 2 ? D.title : D.ink)));
  } else {
    const defaults: Record<string, string[]> = {
      loop: ['이동 · 자동 공격', '경험치 · 레벨업', '다음 강화 선택'],
      familiar: ['익숙한 직업', '빌드의 기대', '장비 파밍'],
      quality: ['재미', '완성도', '이용허락'],
      reactions: ['플레이의 즐거움', '제작 과정과 권리', '각기 다른 평가 기준'],
      responsibility: ['새로운 경험', '구체적인 창작물', '사용 조건 확인'],
      license: ['에셋 팩 구매', '허용된 용도 확인', '조건에 맞게 사용'],
    };
    const labels = d.cueLabels ?? defaults[d.kind] ?? defaults.quality;
    labels.slice(0, 3).forEach((s, i) => {
      add(i, txt(s, 515, -220 + i * 200, 49, i === 2 ? D.title : D.ink));
      if (i < 2 && !['quality', 'reactions'].includes(d.kind)) arrow([[515, -155 + i * 200], [515, -95 + i * 200]], i + 1);
      if (d.kind === 'quality') add(i, <Line points={[[205, -160 + i * 200], [825, -160 + i * 200]]} stroke={i === 2 ? D.teal : D.line} lineWidth={4}/>);
    });
  }
  yield* t(d.duration, d.duration, linear);
}
