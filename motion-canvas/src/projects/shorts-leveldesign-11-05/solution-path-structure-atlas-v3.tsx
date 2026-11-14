import {Node, makeScene2D} from '@motion-canvas/2d';
import {createSignal, tween, useScene} from '@motion-canvas/core';
import {StructurePacket, structuralDiagram, validateStructure} from './solution-path-structure';

/** Finite asset atlas. Asset index is not a native/speech/movie timestamp. */
export default makeScene2D(function* (view) {
  const variables = useScene().variables;
  const mode = variables.get('renderMode', 'unbound-preparation')();
  const fingerprint = variables.get('jobFingerprint', '')();
  const packets = variables.get<StructurePacket[]>('sourcePackets', [])();
  if (mode !== 'source-pinned-structural-atlas-v3' || !/^[0-9a-f]{64}$/.test(fingerprint) || !packets.length ||
      view.width() !== 1080 || view.height() !== 900) throw new Error('Pending actual source snapshot job; no default timing');
  const keys = new Set<string>();
  for (const packet of packets) {
    validateStructure(packet);
    const key = `${packet.mode}/${packet.nativeFrame}`;
    if (keys.has(key)) throw new Error('Atlas must contain each source snapshot only once');
    keys.add(key);
  }
  view.fill('#00000000');
  const screen = new Node({position: () => view.size().scale(-.5)});
  view.add(screen);
  const current = createSignal(-1);
  const show = (index: number) => {
    if (current() === index) return;
    current(index);
    screen.removeChildren();
    screen.add(structuralDiagram(packets[index]));
  };
  show(0);
  // The caller exports exactly packets.length frames at60fps. This ordinal
  // asset clock does not assign speech duration or interpolate native state.
  yield* tween(packets.length / 60, value => show(Math.min(packets.length - 1, Math.floor(value * packets.length))));
});
