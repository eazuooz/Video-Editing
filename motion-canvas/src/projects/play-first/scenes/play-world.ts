import {Node} from '@motion-canvas/2d';
import {BBox, createSignal} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {Art, iso, lerp, ramp, Point} from '../../let-them-play/editorial/art';

// Original 2.5D teaching dioramas for play-first. The adventurer is the channel's own character;
// nothing here depicts Super Mario Odyssey characters, items or UI. `clock` is seconds since the beat began.
export class PlayWorld extends Node {
  readonly chapter = createSignal(0);
  readonly beat = createSignal(0);
  readonly clock = createSignal(0);
  protected getCacheBBox() {return new BBox(-960, -470, 1920, 960);}

  protected draw(c: CanvasRenderingContext2D) {
    const a = new Art(c), ch = this.chapter(), beat = this.beat(), t = this.clock();
    const r = (from: number, to: number) => ramp(t, from, to);
    c.save();
    // Slow physical dolly so the world keeps moving under the narration.
    const dolly = Math.min(1, t / 14);
    c.translate(-10 + 20 * dolly, 96 - 10 * dolly);
    c.scale(1.42 + 0.05 * dolly, 1.42 + 0.05 * dolly);

    const fade = (alpha: number, f: () => void) => {
      if (alpha <= 0) return;
      c.save(); c.globalAlpha *= Math.min(1, alpha); f(); c.restore();
    };
    const text = (s: string, x: number, z: number, h = 0, size = 22, color: string = P.ink, weight = 600) => {
      const q = iso(x, z, h);
      c.font = `${weight} ${size}px 'Malgun Gothic', 'Segoe UI', sans-serif`;
      c.fillStyle = color; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, q[0], q[1]);
    };
    const label = (s: string, x: number, z: number, h: number, color: string = P.ink, size = 21) => {
      const q = iso(x, z, h);
      c.font = `600 ${size}px 'Malgun Gothic', 'Segoe UI', sans-serif`;
      const w = c.measureText(s).width + 26;
      a.rect(q[0] - w / 2 + 4, q[1] - 17 + 4, w, 34, 'rgba(32,32,32,0.12)');
      a.rect(q[0] - w / 2, q[1] - 17, w, 34, '#ffffff');
      c.strokeStyle = color; c.lineWidth = 2; c.strokeRect(q[0] - w / 2, q[1] - 17, w, 34);
      c.fillStyle = color; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, q[0], q[1] + 1);
    };
    // A standing display facing the viewer; `fill` is the playback progress (0..1).
    const screen = (x: number, z: number, w: number, h: number, fill: number, caption: string) => {
      a.box(x, z, w + 16, 16, 12, '#c9d2d8', '#9fb0bb', '#7f96a5');
      a.box(x, z, w, 10, h, '#3a4247', '#2a3136', '#1f2529', 12);
      const bl = iso(x - w / 2 + 14, z + 6, 30), br = iso(x + w / 2 - 14, z + 6, 30);
      a.line([bl, br], '#56616a', 7);
      if (fill > 0) a.line([bl, [lerp(bl[0], br[0], fill), lerp(bl[1], br[1], fill)]], '#c9d2d8', 7);
      text(caption, x, z + 6, 12 + h * 0.58, 22, '#e8eef1');
    };
    const pad = (x: number, z: number, pressed: number, glow: number) => {
      a.box(x, z, 74, 74, 48, '#dfe6ea', '#b4c3cc', '#8ea3b0');
      const q = iso(x, z, 58 - 8 * pressed);
      a.oval(q[0], q[1] + 6, 26, 11, '#1f4f8f');
      a.oval(q[0], q[1], 26, 11, glow > 0.5 ? '#5f8fd0' : P.blue);
      if (glow > 0) a.ring(x, z, glow, 50);
    };
    const block = (x: number, z: number, big: string, small: string, accent = false, lift = 0, alpha = 1) => fade(alpha, () => {
      a.box(x, z, 86, 70, 46, accent ? '#dfeaf5' : '#eef1f3', accent ? '#9fbbdb' : '#c5ced4', accent ? '#6d95c6' : '#a7b4bd', lift);
      text(big, x, z, 72 + lift, 30, accent ? P.blue : P.ink, 700);
      text(small, x, z, 104 + lift, 18, P.muted, 600);
    });
    const post = (x: number, z: number, s: string, color: string = P.ink, checked = -1) => {
      const base = iso(x, z), top = iso(x, z, 96);
      a.oval(base[0] + 4, base[1] + 2, 14, 5, '#c9d2d6');
      a.line([base, top], '#8a7a60', 7);
      label((checked >= 0 ? (checked > 0.5 ? '☑ ' : '☐ ') : '') + s, x, z, 112, color, 20);
    };
    const flag = (x: number, z: number, rise = 1, color: string = P.yellow) => {
      const b = iso(x, z), top = iso(x, z, 150);
      a.line([b, top], '#54758a', 4);
      const y = lerp(b[1] - 30, top[1], rise);
      a.poly([[top[0], y], [top[0] + 46, y + 13], [top[0], y + 26]], color);
    };
    const question = (x: number, z: number, h: number, alpha = 1, color: string = P.red) => fade(alpha, () => {
      const q = iso(x, z, h);
      a.oval(q[0], q[1], 22, 22, color);
      c.font = "700 28px 'Segoe UI', sans-serif"; c.fillStyle = '#fff'; c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('?', q[0], q[1] + 1);
    });
    const ghost = (x: number, z: number, alpha = 0.45) => fade(alpha, () => a.hero(x, z, t, 0));
    const walkTo = (from: Point, to: Point, s: number, e: number): [number, number, number] => {
      const k = r(s, e);
      return [lerp(from[0], to[0], k), lerp(from[1], to[1], k), k > 0 && k < 1 ? 1 : 0];
    };

    if (ch === 0 && beat === 0) {
      // Waiting in front of a long opening; the pad in hand does nothing yet.
      a.floor('wood');
      screen(90, -95, 300, 190, Math.min(0.97, t / 9), '오프닝 영상 재생 중');
      a.tree(-285, -150, 0.7); a.tree(290, 120, 0.6);
      a.box(-150, 95, 120, 60, 28, '#d7c9ad', '#b49f7d', '#98835f');
      a.hero(-150, 95, t, 0, 28);
      [0, 1, 2].forEach(k => text('·', -150 + k * 16 - 16, 95, 200 + Math.sin(t * 2 + k) * 6, 40, P.muted, 700));
      label(`${String(Math.floor(Math.min(t / 9, 1) * 174 / 60)).padStart(2, '0')}:${String(Math.floor(Math.min(t / 9, 1) * 174 % 60)).padStart(2, '0')} / 03:00`, 150, -40, 30, P.muted, 18);
    } else if (ch === 0 && beat === 1) {
      // Two lanes over the first three minutes: grey = watching, blue = playing.
      a.floor('stone');
      for (let m = 0; m <= 3; m++) {
        const x = -270 + m * 180;
        a.box(x, -160, 14, 14, 70, '#d5dde2', '#aab8c1', '#8ca0ad');
        text(`${m}분`, x, -160, 96, 20, P.muted);
      }
      const lanes: [number, number, string][] = [[-40, 0.9, 'A  보여 주기부터'], [90, 0.08, 'B  해 보게 하기부터']];
      lanes.forEach(([z, watch], li) => {
        const grow = r(0.3 + li * 0.5, 2.2 + li * 0.5);
        for (let k = 0; k < 18; k++) {
          const at = k / 18;
          if (at > grow) break;
          const play = at >= watch;
          a.box(-270 + 540 * (at + 1 / 36), z, 28, 58, 10, play ? '#dfeaf5' : '#eef1f3', play ? '#9fbbdb' : '#cfd6db', play ? P.blue : '#b3bec5');
        }
        label(lanes[li][2], 330, z, 36, li ? P.blue : P.muted, 18);
      });
      ghost(-270 + 540 * 0.9 * r(1, 12), -40, 0.35);
      const [hx, hz, walk] = walkTo([-275, 90], [230, 90], 2.6, 12);
      a.hero(hx, hz, t, walk);
    } else if (ch === 0 && beat === 2) {
      // Explanation podium (crossed out) → playable pad → judgement flag. Waiting too long leads to the exit.
      a.floor('grass'); a.path([[-250, 80], [-60, 20], [150, -50], [260, -110]]);
      a.box(-250, 80, 70, 50, 70, '#e2e6e9', '#bcc6cc', '#9aa8b1');
      label('설명 듣기', -250, 80, 130, P.muted); fade(r(0.2, 0.6), () => text('✕', -250, 80, 175, 34, P.red, 700));
      const press = r(3.2, 3.5) * (1 - r(3.9, 4.3));
      pad(-40, 10, press, r(3.3, 3.8));
      label('직접 해 보기', -40, 10, 118, P.blue);
      flag(200, -80, r(4.2, 5.2));
      label('재미 판단', 200, -80, 185, P.ink);
      const p1 = walkTo([-250, 140], [-40, 60], 1, 3);
      const p2 = walkTo([-40, 60], [180, -20], 4.4, 6.4);
      t < 4.4 ? a.hero(p1[0], p1[1], t, p1[2]) : a.hero(p2[0], p2[1], t, p2[2]);
      fade(r(6.5, 7.2), () => {
        a.box(300, 150, 16, 90, 110, '#f1d5d5', '#d49a9a', P.red);
        label('기다림이 길면 → 떠난다', 250, 150, 150, P.red, 19);
      });
    } else if (ch === 0 && beat === 3) {
      // Crossroads: the three design questions of this video.
      a.floor('grass');
      a.path([[-260, 120], [-60, 40]]); a.path([[-60, 40], [180, -110]]); a.path([[-60, 40], [230, 60]]); a.path([[-60, 40], [-120, -170]]);
      a.tree(-280, -60, 0.7); a.tree(280, -170, 0.7);
      post(-130, -150, '무엇을 먼저 보여 줄까', P.blue, -1);
      post(170, -100, '언제 처음 조작할까', P.blue, -1);
      post(220, 70, '이야기는 어디에 둘까', P.blue, -1);
      const [hx, hz, walk] = walkTo([-260, 120], [-60, 40], 0.2, 2.2);
      a.hero(hx, hz, t, walk);
      a.ring(-60, 40, r(2.2, 2.8));
    } else if (ch === 1 && beat <= 1) {
      // Two hypothetical store trailers laid out as film strips. The "?" resolves when gameplay appears.
      a.floor('stone');
      const strips: [number, string[], number, string][] = [
        [-70, ['CG', '이야기', '이야기', 'CG', '게임'], 4, 'A  이야기부터'],
        [110, ['게임', '게임', '이야기', 'CG', '게임'], 0, 'B  게임부터'],
      ];
      strips.forEach(([z, cells, answer, name], si) => {
        if (si === 1 && beat === 0) return;
        const show = si === 1 ? r(0.2, 1.4) : (beat === 1 ? 1 : r(0.2, 1.4));
        cells.forEach((cell, k) => {
          const game = cell === '게임';
          fade(Math.min(1, show * 5 - k), () => {
            a.box(-240 + k * 120, z, 108, 62, 16, game ? '#dfeaf5' : '#eef1f3', game ? '#9fbbdb' : '#cfd6db', game ? P.blue : '#b3bec5');
            text(cell, -240 + k * 120, z, 34, 20, game ? P.blue : P.muted, 700);
          });
        });
        label(name, 350, z, 40, si ? P.blue : P.muted, 18);
        const travel = si === 0 ? (beat === 1 ? 1 : r(1.4, 6.5)) : r(1.5, 2.1);
        const qx = -240 + answer * 120 * travel;
        const done = si === 0 ? (beat === 1 || travel >= 1) : travel >= 1;
        question(qx, z, 110 + Math.sin(t * 3 + si) * 5, 1, done ? P.blue : P.red);
      });
    } else if (ch === 1 && beat === 2) {
      // "So what do I actually do in this game?" — a visitor in front of an unexplained display.
      a.floor('wood');
      screen(60, -110, 260, 170, 0.3, '???');
      a.tree(-290, -150, 0.7);
      a.hero(-140, 90, t, 0);
      question(-140, 90, 230 + Math.sin(t * 2.4) * 8, 1);
      fade(r(0.6, 1.2), () => label('그래서, 뭘 하는 게임인데?', 40, 60, 230, P.blue, 24));
    } else if (ch === 2 && beat <= 1) {
      // Story order 1-4; in beat 1 the "event" block hops to the front.
      a.floor('stone');
      const names = ['배경', '사건', '위기', '결말'];
      const hop = beat === 1 ? r(0.3, 1.3) : 0;
      names.forEach((name, k) => {
        let x = -240 + k * 160, lift = 0;
        if (beat === 1 && k === 1) { x = lerp(-80, -240, hop); lift = Math.sin(hop * Math.PI) * 90; }
        if (beat === 1 && k === 0) x = lerp(-240, -80, hop);
        const appear = beat === 0 ? r(0.2 + k * 0.25, 0.6 + k * 0.25) : 1;
        block(x, -10, String(k + 1), name, beat === 1 && k === 1, lift, appear);
      });
      a.path([[-300, 110], [300, 110]], 18);
      if (beat === 1) {
        const [hx, hz, walk] = walkTo([-300, 120], [-240, 70], 1.4, 2.6);
        a.hero(hx, hz, t, walk);
        fade(r(1.3, 1.8), () => label('사건 한복판부터', -240, -10, 150, P.blue));
      } else {
        a.hero(-300, 120, t, 0);
      }
    } else if (ch === 2 && beat === 2) {
      // Story order stays on the back row; two playable orders are laid out in front.
      a.floor('stone');
      const names = ['배경', '사건', '위기', '결말'];
      names.forEach((name, k) => block(-150 + k * 120, -160, String(k + 1), name, false, 0, 0.55));
      text('이야기 순서', -300, -160, 40, 19, P.muted);
      const rowA: [string, string, boolean][] = [['3', '위기', true], ['1', '배경', false], ['2', '사건', false], ['4', '결말', false]];
      const rowB: [string, string, boolean][] = [['0', '앞선 인물', true], ['1', '배경', false], ['2', '사건', false], ['3', '위기', false]];
      rowA.forEach(([n, s, acc], k) => block(-150 + k * 120, -20, n, s, acc, 0, r(0.2 + k * 0.15, 0.6 + k * 0.15)));
      rowB.forEach(([n, s, acc], k) => block(-150 + k * 120, 120, n, s, acc, 0, r(1 + k * 0.15, 1.4 + k * 0.15)));
      text('플레이 순서 A', -300, -20, 40, 19, P.blue); text('플레이 순서 B', -300, 120, 40, 19, P.blue);
      fade(r(1.4, 2), () => ghost(-150, 175, 0.5));
    } else if (ch === 2 && beat === 3) {
      // Not knowing yet → in your hands → curiosity → into the story.
      a.floor('grass');
      const stops: [number, number, string][] = [[-250, 110, '아직 영문은 모름'], [-90, 40, '일단 손에 잡힘'], [70, -30, '무슨 일이지?'], [230, -100, '이야기로 들어감']];
      a.path(stops.map(([x, z]) => [x, z] as Point));
      stops.forEach(([x, z, s], k) => {
        const on = r(k * 1.4, k * 1.4 + 0.4);
        a.ring(x, z, on);
        fade(on, () => label(s, x, z, 150, k === 1 ? P.blue : P.ink, 19));
      });
      pad(-90, 40, 0, r(1.4, 1.9));
      question(70, -30, 90 + Math.sin(t * 3) * 6, r(2.8, 3.3), P.blue);
      flag(230, -100, r(4.2, 5));
      const k = Math.min(3, Math.floor(t / 1.4)), f = r(k * 1.4, k * 1.4 + 1.1);
      const from = stops[Math.max(0, k - 1)], to = stops[k];
      a.hero(lerp(from[0], to[0], k === 0 ? 1 : f), lerp(from[1], to[1], k === 0 ? 1 : f) + 30, t, f > 0 && f < 1 && k > 0 ? 1 : 0);
    } else if (ch === 2 && beat === 4) {
      // The story block stays; the play pad slides in front of the adventurer.
      a.floor('wood');
      block(160, -120, '이야기', '그대로', false, 0, 1);
      const slide = r(0.3, 1.4);
      pad(lerp(160, -40, slide), lerp(-120, 40, slide), 0, r(1.4, 2));
      a.hero(-200, 110, t, 0);
      fade(r(1.4, 2), () => label('조작은 앞으로', -40, 40, 118, P.blue));
    } else if (ch === 3 && beat === 0) {
      // Why put play first? Three covered pedestals.
      a.floor('stone');
      [-200, 0, 200].forEach((x, k) => a.box(x, -60, 90, 90, 60, '#e6ebee', '#c2ccd2', '#a2b1ba'));
      a.hero(-20, 120, t, 0);
      question(-20, 120, 230 + Math.sin(t * 2) * 8, r(0.2, 0.7));
    } else if (ch === 3 && beat === 1) {
      // Film, animation and game can all show pictures and story; only the game reacts to your input.
      a.floor('stone');
      // Screens sit forward enough that their tops stay below the heading.
      const cols: [number, number, string][] = [[-290, -100, '영화'], [-110, -160, '애니메이션']];
      cols.forEach(([x, z, name]) => {
        screen(x, z, 130, 90, 0.4 + 0.3 * Math.sin(t + x), '▶');
        label(name, x, z + 70, 16, P.ink, 19);
      });
      const press = Math.max(0, Math.sin(t * 2.2)) > 0.6 ? 1 : 0;
      pad(160, 80, press, press);
      label('게임', 160, 80, 120, P.blue, 20);
      a.hero(60, 160, t, 0);
      for (let k = 0; k < 3; k++) {
        const up = press ? 1 : 0.2;
        a.box(300, 0 + k * 50, 30, 30, 20 + 50 * up * (1 + k * 0.3), '#dfeaf5', '#9fbbdb', P.blue);
      }
      fade(r(1.5, 2.2), () => label('내 입력에 세계가 반응', 320, 50, 190, P.blue, 19));
    } else if (ch === 3 && beat === 2) {
      // First input → the world answers (a bridge extends) → the promise of what comes next.
      a.floor('grass');
      pad(-200, 60, r(0.8, 1.0) * (1 - r(1.3, 1.6)), r(0.9, 1.5));
      const bridge = r(1.2, 2.8);
      for (let k = 0; k < 6; k++) fade(Math.min(1, bridge * 6 - k), () => a.box(-100 + k * 60, 20 - k * 22, 56, 60, 14, '#e8dcc2', '#c8b48f', '#a8926c'));
      flag(260, -120, r(2.6, 3.4));
      label('첫 조작', -200, 60, 125, P.blue); fade(r(1.5, 2), () => label('세계의 반응', 60, -40, 70, P.ink));
      fade(r(2.8, 3.4), () => label('앞으로 할 일', 260, -120, 190, P.ink));
      const [hx, hz, walk] = walkTo([-260, 120], [-200, 110], 0.1, 0.7);
      const [bx, bz, bw] = walkTo([-200, 110], [220, -90], 3.2, 7.2);
      t < 3.2 ? a.hero(hx, hz, t, walk) : a.hero(bx, bz, t, bw);
    } else if (ch === 3 && beat === 3) {
      a.floor('grass'); a.path([[-280, 110], [0, 20], [260, -120]]);
      a.tree(-260, -120, 0.8); a.tree(280, 130, 0.7);
      flag(260, -120, 1);
      const [hx, hz] = walkTo([-280, 110], [200, -90], 0.2, 9);
      a.hero(hx, hz, t, 1);
      [0, 1, 2].forEach(k => a.crystal(-150 + k * 140, 70 - k * 60, 30 + Math.sin(t * 2 + k) * 5, 1 - r(1.5 + k * 2.4, 2 + k * 2.4)));
    } else if (ch === 4 && beat <= 1) {
      // A path between "staging/story first" and "play first"; the chosen point is decided on purpose.
      a.floor('stone'); a.path([[-270, 90], [270, -90]], 24);
      screen(-280, 20, 120, 90, 0.5, '연출');
      pad(290, -40, 0, 0.4);
      label('연출·이야기 먼저', -250, 80, 20, P.ink, 19); label('조작 먼저', 290, -40, 130, P.blue, 19);
      const swing = beat === 0 ? (t < 1.6 ? r(0.1, 1.6) : 1 - 0.55 * r(1.8, 3)) : 0.45;
      const mx = lerp(-230, 230, swing), mz = lerp(77, -77, swing);
      a.ring(mx, mz, 1);
      if (beat === 1) { flag(mx, mz, r(0.2, 0.9), P.blue); fade(r(0.6, 1.2), () => label('의도해서 정한 지점', mx, mz, 185, P.blue)); }
      a.hero(mx - 40, mz + 60, t, 0);
    } else if (ch === 4 && beat === 2) {
      // The first-three-minutes checklist: each sign is ticked as the adventurer reaches it.
      a.floor('grass'); a.path([[-280, 120], [-80, 40], [100, -30], [270, -110]]);
      const qs: [number, number, string][] = [[-110, 110, '언제 처음 움직이나?'], [70, 40, '그 움직임이 재미를 말하나?'], [240, -40, '이야기는 조작 뒤에 와도 되나?']];
      const [hx, hz, walk] = walkTo([-280, 120], [270, -110], 0.3, 7.5);
      qs.forEach(([x, z, s], k) => post(x, z, s, P.blue, hx > x - 60 ? 1 : 0));
      a.hero(hx, hz, t, walk);
    } else {
      // Final: the adventurer runs off into the world.
      a.floor('grass'); a.path([[-260, 110], [270, -120]]);
      a.tree(-280, -120, 0.9); a.tree(-150, -170, 0.7); a.tree(290, 130, 0.8);
      a.tower(250, -140, 110);
      const [hx, hz, walk] = walkTo([-260, 110], [200, -90], 0.3, 9);
      a.hero(hx, hz, t, walk);
    }
    c.restore();
    this.drawChildren(c);
  }
}
