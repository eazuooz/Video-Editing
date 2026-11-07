import {Line, Node, Rect, Txt} from '@motion-canvas/2d';

type Point = [number, number];
type Room = {id: number; label: string; center: Point; role: string; entrance: boolean; exit: boolean; templateVariant: number | null};
type Port = {a: number; b: number; open: boolean; role: string | null; center: Point; broken: boolean};
type Route = {a: number; b: number; connected: boolean};
export type StructurePacket = {
  schemaVersion: '11-05-structural-diagram-v1'; fingerprint: string; physicalInputFingerprint: string;
  mode: string; nativeFrame: number; sourceKind: 'structural-illustration-of-current-own-model';
  sourceKindLabel: '생성 규칙 설명도 · 자체 모형'; phase: string;
  rooms: Room[]; ports: Port[]; route: Route[];
  routeMeaning: 'intended-input-only' | 'currently-open-mandatory-ports'; routeLabel: string;
  exitRevealed: boolean; exitRoom: number | null; modelExitConnected: boolean; currentPortExitConnected: boolean;
  actualPlayerPoint: Point; exitReached: boolean;
  inputs: {path: string; sha256: string}[]; speechFrame: null;
  actualSpeechTimingVerified: false; nativePixelVisibilityClaim: false; actualPixelQaPassed: false; humanReviewed: false;
};

export const STRUCTURE_CONTENT_BOXES = [[130, 30, 780, 115], [145, 172, 750, 602], [110, 792, 860, 95]] as const;
export const STRUCTURE_CANVAS = [1080, 900] as const;
export const STRUCTURE_CAT_ALLOWED = false;
const PHYSICAL = '0fdfd4b196c4daa61a9a2ec01982592c60bb476131178d2002ed04229fadee0b';
const COLORS = {background: '#000000', text: '#f5f5f5', muted: '#b8b8b8', title: '#e8cf83',
  route: '#a4c6a0', side: '#73c7c2', closed: '#ef8585', sealed: '#737373'};
const FONT = 'Noto Sans KR';
const hash = (text: string) => /^[0-9a-f]{64}$/.test(text);
const center = (room: number): Point => [220 + (room % 4) * 200, 230 + Math.floor(room / 4) * 165];
const adjacent = (a: number, b: number) => Math.abs(Math.floor(a / 4) - Math.floor(b / 4)) + Math.abs(a % 4 - b % 4) === 1;
const key = (a: number, b: number) => `${Math.min(a, b)}-${Math.max(a, b)}`;

export function validateStructure(packet: StructurePacket): void {
  if (packet.schemaVersion !== '11-05-structural-diagram-v1' || packet.physicalInputFingerprint !== PHYSICAL ||
      !hash(packet.fingerprint) || !Number.isInteger(packet.nativeFrame) || packet.nativeFrame < 0 || packet.nativeFrame >= 3120 ||
      packet.sourceKind !== 'structural-illustration-of-current-own-model' || packet.sourceKindLabel !== '생성 규칙 설명도 · 자체 모형' ||
      packet.speechFrame !== null || packet.actualSpeechTimingVerified !== false || packet.nativePixelVisibilityClaim !== false ||
      packet.actualPixelQaPassed !== false || packet.humanReviewed !== false || !packet.inputs.length ||
      packet.inputs.some(row => !row.path || !hash(row.sha256))) throw new Error('Source-bound structural illustration required, no pixel/speech approval');
  if (packet.rooms.length !== 16 || packet.ports.length !== 24 ||
      packet.rooms.some((room, i) => room.id !== i || room.label !== `R${String(i).padStart(2, '0')}` ||
        JSON.stringify(room.center) !== JSON.stringify(center(i)) || !['mandatory', 'side', 'sealed', 'unclassified'].includes(room.role))) {
    throw new Error('Exact four-by-four actual room identities required');
  }
  const ports = new Map<string, Port>();
  for (const port of packet.ports) {
    if (!Number.isInteger(port.a) || !Number.isInteger(port.b) || port.a < 0 || port.a >= port.b || port.b >= 16 ||
        !adjacent(port.a, port.b) || ports.has(key(port.a, port.b)) || typeof port.open !== 'boolean' ||
        JSON.stringify(port.center) !== JSON.stringify(center(port.a).map((value, i) => (value + center(port.b)[i]) / 2)) ||
        typeof port.broken !== 'boolean' || (port.broken && port.open)) throw new Error('Actual adjacent open/closed port state required');
    ports.set(key(port.a, port.b), port);
  }
  const broken = packet.mode === 'broken-link';
  if (packet.routeMeaning !== (broken ? 'intended-input-only' : 'currently-open-mandatory-ports') ||
      ports.size !== 24 || [...ports.values()].filter(port => port.broken).length !== (broken ? 1 : 0) ||
      (broken && (packet.modelExitConnected || packet.currentPortExitConnected))) throw new Error('Intended broken route is not a connected path');
  for (const edge of packet.route) {
    if (!adjacent(edge.a, edge.b) || ports.get(key(edge.a, edge.b))?.open !== edge.connected ||
        (!broken && !edge.connected)) throw new Error('Route must retain the actual open-port distinction');
  }
  const exits = packet.rooms.filter(room => room.exit);
  if (exits.length !== (packet.exitRevealed ? 1 : 0) ||
      (packet.exitRevealed ? exits[0].id !== packet.exitRoom : packet.exitRoom !== null)) throw new Error('Do not reveal the derived exit early');
}

function portSegment(a: number, b: number): Point[] {
  const first = center(a), last = center(b);
  const horizontal = first[1] === last[1];
  const dx = Math.sign(last[0] - first[0]) * (horizontal ? 75 : 0);
  const dy = Math.sign(last[1] - first[1]) * (horizontal ? 0 : 58);
  return [[first[0] + dx, first[1] + dy], [last[0] - dx, last[1] - dy]];
}

/** Static actual-native-frame snapshot, top-left origin, 1080x900.
 * The future verified timeline supplies successive snapshots at native1x or a
 * labelled hold. No interpolation, default duration or object-visibility claim.
 * This is an alternative structural companion: do not double-stack UI layers.
 */
export function structuralDiagram(packet: StructurePacket): Node {
  validateStructure(packet);
  const node = new Node({});
  node.add(new Rect({position: [540, 450], size: [1080, 900], fill: COLORS.background, opacity: .9}));
  node.add(new Txt({x: 520, y: 62, text: 'Solution Path (출구 연결 경로)',
    fontFamily: FONT, fontSize: 48, fontWeight: 700, fill: COLORS.title}));
  node.add(new Txt({x: 520, y: 121, text: packet.sourceKindLabel,
    fontFamily: FONT, fontSize: 32, fontWeight: 500, fill: COLORS.muted}));
  // Open ports are actual graph-prefix states, not the recorded camera-origin ray.
  for (const port of packet.ports.filter(value => value.open)) {
    node.add(new Line({points: portSegment(port.a, port.b), stroke: port.role === 'mandatory' ? COLORS.route : COLORS.side,
      lineWidth: 12, lineCap: 'round'}));
  }
  for (const edge of packet.route) {
    node.add(new Line({points: portSegment(edge.a, edge.b), stroke: COLORS.route, lineWidth: 9,
      lineDash: packet.routeMeaning === 'intended-input-only' ? [9, 7] : [], endArrow: true, arrowSize: 15}));
  }
  for (const room of packet.rooms) {
    const color = room.role === 'mandatory' ? COLORS.route : room.role === 'side' ? COLORS.side : room.role === 'sealed' ? COLORS.sealed : COLORS.muted;
    const role = room.entrance ? '입구' : room.exit ? '출구' : room.role === 'sealed' ? '봉인' : room.role === 'side' ? '옆방' : room.role === 'mandatory' ? '경로' : '';
    node.add(new Rect({position: room.center, width: 150, height: 116, fill: COLORS.background, stroke: color, lineWidth: 5}));
    node.add(new Txt({position: [room.center[0], room.center[1] - 17], text: room.label,
      fontFamily: FONT, fontSize: 48, fontWeight: 700, fill: COLORS.text}));
    node.add(new Txt({position: [room.center[0], room.center[1] + 32], text: role,
      fontFamily: FONT, fontSize: 30, fontWeight: 700, fill: color}));
  }
  for (const port of packet.ports.filter(value => value.broken)) {
    node.add(new Rect({position: port.center, width: 23, height: 46, fill: COLORS.background, stroke: COLORS.closed, lineWidth: 7}));
    node.add(new Line({points: [[port.center[0] - 14, port.center[1] - 24], [port.center[0] + 14, port.center[1] + 24]], stroke: COLORS.closed, lineWidth: 7}));
  }
  node.add(new Txt({x: 520, y: 819, text: packet.routeLabel, fontFamily: FONT, fontSize: 34,
    fontWeight: 700, fill: packet.routeMeaning === 'intended-input-only' ? COLORS.closed : COLORS.route}));
  node.add(new Txt({x: 520, y: 869, text: '초록 경로 · 청록 옆방 · 빨강 닫힘',
    fontFamily: FONT, fontSize: 28, fontWeight: 500, fill: COLORS.muted}));
  return node;
}
