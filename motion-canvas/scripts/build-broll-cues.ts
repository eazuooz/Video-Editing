// Writes the gameplay B-roll cue sheet from src/broll.ts, so the shot list can
// never drift from what the video actually renders.
//
// Run with: npm run cues

import {writeFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {BROLL, absoluteEnd, absoluteStart, timecode} from '../src/broll.ts';
import {SEGMENTS} from '../src/narration.ts';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(here, '../../shared/output/narration/qwen3-balanced');

const rows = BROLL.map(window => ({
  clip: window.clip,
  label: window.label,
  hint: window.hint,
  segment: SEGMENTS[window.segment].label,
  start: absoluteStart(window),
  end: absoluteEnd(window),
  duration: window.duration,
}));

const md = [
  '# 게임 영상 자리 (B-roll) — 촬영/편집 큐 시트',
  '',
  '`npm run cues`로 생성됩니다. 직접 수정하지 마세요 — 값을 바꾸려면',
  '`motion-canvas/src/broll.ts`를 고치고 다시 생성하면 됩니다.',
  '',
  '영상 파일을 `motion-canvas/src/assets/gameplay/<파일명>.mp4`에 넣으면',
  '**Motion Canvas가 알아서 잡아서 재생합니다.** 파이널컷으로 안 가도 됩니다.',
  '파일이 없으면 같은 자리에 "게임 영상 자리" 안내판이 표시됩니다.',
  '',
  '타임코드는 나레이션 오디오',
  '(`jump-physics-qwen3-balanced.wav`) 기준 절대 시각입니다.',
  '',
  '| 파일명 | 시작 | 끝 | 길이 | 구간 | 넣을 내용 |',
  '| --- | --- | --- | --- | --- | --- |',
  ...rows.map(
    row =>
      `| \`${row.clip}.mp4\` | ${timecode(row.start)} | ${timecode(row.end)} | ` +
      `${row.duration.toFixed(1)}초 | ${row.segment} | ${row.hint} |`,
  ),
  '',
  '## 참고',
  '',
  '- 영상이 슬롯보다 길면 잘리고, 짧으면 반복(loop) 재생됩니다.',
  '- 슬롯 앞뒤 0.4초는 페이드에 쓰이므로, 중요한 장면은 살짝 안쪽에 두세요.',
  '- 슬롯 길이를 바꾸려면 `src/broll.ts`의 `duration`을 고친 뒤',
  '  `npm run check:narration`으로 씬 길이를 넘지 않는지 확인하세요.',
  '',
].join('\n');

const csv = [
  'clip,start_seconds,end_seconds,duration_seconds,start_timecode,end_timecode,segment,label,hint',
  ...rows.map(row =>
    [
      row.clip,
      row.start.toFixed(3),
      row.end.toFixed(3),
      row.duration.toFixed(3),
      timecode(row.start),
      timecode(row.end),
      `"${row.segment}"`,
      `"${row.label}"`,
      `"${row.hint}"`,
    ].join(','),
  ),
  '',
].join('\n');

writeFileSync(resolve(outDir, 'broll-cues.md'), md, 'utf8');
writeFileSync(resolve(outDir, 'broll-cues.csv'), csv, 'utf8');

// Legacy filenames from an earlier, hand-written cue sheet -- regenerated here
// from the same src/broll.ts data (same rows as above, English section slugs
// and mm:ss.mmm timecodes to match the original format) so anything already
// pointing at these paths keeps working instead of going stale.
function legacyTimecode(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds - minutes * 60;
  return `${String(minutes).padStart(2, '0')}:${rest.toFixed(3).padStart(6, '0')}`;
}

const totalDuration = Math.max(...BROLL.map(w => SEGMENTS[w.segment].end));

const legacyRows = BROLL.map(window => ({
  section: window.clip.replace(/-/g, '_'),
  start: absoluteStart(window),
  end: absoluteEnd(window),
  visual: window.hint,
}));

const legacyCsv = [
  'section,start,end,visual,source_footage_seconds',
  ...legacyRows.map(
    row =>
      `${row.section},${legacyTimecode(row.start)},${legacyTimecode(row.end)},` +
      `"${row.visual}",${row.end - row.start}`,
  ),
  '',
].join('\n');

const legacyMd = [
  '# 점프 물리 — Qwen3 음성본 편집 큐',
  '',
  `기준 음성: \`jump-physics-qwen3-balanced.wav\` (${legacyTimecode(totalDuration)})`,
  '',
  '게임 영상은 내레이션을 멈추게 하는 빈 구간이 아니라, 아래의 말 위에 겹쳐 보여 주는 B-roll로 사용한다. ' +
    '한 소스는 보통 8~15초가 가장 읽기 좋고, 설명이 긴 구간은 같은 장면을 슬로 모션·줌·리플레이로 나누어 쓴다.',
  '',
  '| 구간 | 실제 음성 타임코드 | 화면 제안 | 파일명 |',
  '| --- | --- | --- | --- |',
  ...BROLL.map(
    window =>
      `| ${window.label} | ${legacyTimecode(absoluteStart(window))}–${legacyTimecode(absoluteEnd(window))} | ` +
      `${window.hint} | \`${window.clip}.mp4\` |`,
  ),
  '',
  '## 전환과 사운드',
  '',
  '- 장면 전환은 0.5~0.7초 디졸브, 게임 플레이 내부 컷은 0.2~0.35초 하드 컷을 권장한다.',
  '- 게임 원음은 내레이션 아래에서 약 -16~-20 dB로 두고, 강조 효과음만 짧게 -10~-12 dB까지 올린다.',
  '- 게임 영상 1개를 30초 이상 그대로 쓰기보다, 설명 문장에 맞는 8~15초를 선택해 리플레이·크롭·프레임 스텝으로 나누는 편이 전달력이 좋다.',
  '',
].join('\n');

writeFileSync(resolve(outDir, 'jump-physics-qwen3-balanced-edit-cues.csv'), legacyCsv, 'utf8');
writeFileSync(resolve(outDir, 'jump-physics-qwen3-balanced-edit-cues.md'), legacyMd, 'utf8');

console.log(`Wrote broll-cues.md/csv and jump-physics-qwen3-balanced-edit-cues.md/csv to ${outDir}`);
for (const row of rows) {
  console.log(
    `  ${row.clip.padEnd(18)} ${timecode(row.start)} – ${timecode(row.end)}  (${row.duration.toFixed(1)}s)`,
  );
}
