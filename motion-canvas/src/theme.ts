// Reusable Motion Canvas text/color theme for this project's videos.
// Large-font convention validated on the jump-physics-showcase scenes:
// titles are ~1.5x a normal heading, yellow/accent text and near-white
// body text are ~2x — tuned so everything reads clearly on a 1920x1080
// canvas without overlapping graphs or images. Import these in new scenes
// instead of hardcoding fontSize/fill values, so future videos stay
// consistent with this look. Scale TEXT_SIZE together if you resize a
// layout instead of tweaking individual scenes.

export const FONT = 'Malgun Gothic';
export const MONO = 'Consolas';

export const COLORS = {
  bg: '#0b0d13',
  white: '#f5f7fb',
  text: '#cbd5e1',
  greyB: '#94a3b8',
  greyC: '#64748b',
  yellow: '#fbbf24',
  blue: '#60a5fa',
  green: '#34d399',
  orange: '#f59e0b',
  red: '#ef4444',
  purple: '#c084fc',
  codeBlue: '#8fd3ff',
  codeComment: '#8a97ab',
} as const;

export const TEXT_SIZE = {
  titleCard: 87, // opening title-card headline
  title: 81, // main per-scene title
  explanationTitle: 72, // "why / how" card heading
  endCard: 69, // closing card headline
  subtitle: 60, // near-white subtitle line under the title
  accentLabel: 60, // yellow section labels ("왜 이렇게...", "어떻게...")
  accent: 54, // yellow live readouts / stats
  legend: 26, // comparison-mode legend
  titleCardSub: 32,
  body: 38, // grey explanation bullet text ("왜 이렇게 만들었나" content)
  endCardSub: 26,
  caption: 24, // small muted caption line
  code: 24, // code block lines
  tick: 20, // axis tick numbers
} as const;
