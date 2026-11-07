"""11.05 read-only composition data. No process, decoder, model, renderer or writes.

Native frame numbers are capture clocks, never invented speech timestamps.
The future timeline builder must supply independently verified PCM/ASR timing.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, struct, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
PHYSICAL = '0fdfd4b196c4daa61a9a2ec01982592c60bb476131178d2002ed04229fadee0b'
PINS = {
    'narration-final-v4.json': '8a35438d9b12131a60a1ec817aaa11d2f4df21b59c2f645dfd69143a71d92a53',
    'scene-plan-v4.json': '76aa4137264f65fd34fef41154d8b4990c07c420831d529650dceb04c3d2cc48',
    'native-presentation-plan-v4.json': '0fa402e73a812fa28d55670104df7ef83af09f47f995f7ca3853006ab0fdd3b4',
    'audio-asset-preparation-v1.json': '1238dff5f598d437418eddfb75f7ec27c99676cb2c082b29b4a54253c895728a',
    'native-evidence-v4.json': 'acbaa5d35763b3f20c5c6d4075bcb10275517ae125b729e0b765ed738dcd7087',
}
CAPTION_TOP = 1527
RAIL = 936
# Exact final-narration glossary. Meaning breaks are authored at semantic
# boundaries, never inferred from a character fraction or a smaller font.
TERM_DEFINITIONS = (
    ('Level Chunk', '레벨 조각', ('작은 플레이 상황을 담은 방 규모의 묶음',)),
    ('Solution Path', '출구 연결 경로', ('생성기가 입구에서 출구로 이어지게', '준비하는 경로')),
    ('Room Type', '방 연결 유형', ('어느 방향 출입구를 지켜야 하는지', '정하는 구분')),
    ('Room Template', '방 템플릿', ('연결 조건 안에서 고르는 내부 설계안',)),
    ('Connectivity', '연결성', ('방과 통로가 서로 이어진 성질',)),
    ('Probabilistic Tile', '확률 타일', ('추첨 결과에 따라 배치가 달라지는', '타일 규칙')),
)
LAYOUTS = {
    'single-player': [('player', [0, 0, 1920, 1080], [48, 410, 880, 495])],
    'dual': [('player', [0, 0, 1920, 1080], [48, 410, 880, 495]),
             ('observer', [420, 0, 1500, 1080], [48, 992, 880, 495])],
    'observer': [('observer', [420, 0, 1500, 1080], [48, 410, 880, 880])],
    'ab-player': [('player', [0, 0, 1920, 1080], [48, 410, 880, 495]),
                  ('player', [0, 0, 1920, 1080], [48, 992, 880, 495])],
    'ab-observer': [('observer', [420, 0, 1500, 1080], [48, 410, 880, 495]),
                    ('observer', [420, 0, 1500, 1080], [48, 992, 880, 495])],
}


class Pending(ValueError):
    pass


def need(value, reason):
    if not value:
        raise Pending(reason)


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode('utf8')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def checked(row, root=None):
    path = Path(row['path']).resolve()
    need(root is None or path.is_relative_to(Path(root).resolve()), 'Input escaped selected scope')
    need(path.is_file() and sha(path) == row['sha256'], 'Missing/changed input: ' + str(path))
    return path


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def project(matrix, world):
    """Same Float32 arithmetic order as the reviewed actual native validator."""
    need(len(matrix) == 16 and len(world) == 3 and
         all(type(v) in (int, float) and math.isfinite(v) for v in matrix + list(world)), 'Finite matrix/world required')
    point = list(world) + [1.]
    clip = []
    for row in range(4):
        value = f32(matrix[row * 4] * point[0])
        for k in range(1, 4):
            value = f32(value + f32(matrix[row * 4 + k] * point[k]))
        clip.append(value)
    need(abs(clip[3]) > 1e-10, 'Zero projection W')
    return [f32(f32(f32(clip[k] / clip[3]) + 1.) * .5) for k in (0, 1)]


def fit(crop, container):
    need(len(crop) == len(container) == 4 and all(math.isfinite(v) for v in crop + container), 'Finite crop/container required')
    x0, y0, x1, y1 = crop
    x, y, w, h = container
    need(0 <= x0 < x1 <= 1920 and 0 <= y0 < y1 <= 1080 and w > 0 and h > 0, 'Invalid source crop')
    scale = min(w / (x1 - x0), h / (y1 - y0))
    width, height = (x1 - x0) * scale, (y1 - y0) * scale
    return dict(crop=list(crop), scale=scale, rect=[x + (w - width) / 2, y + (h - height) / 2, width, height])


def mapped(viewport, transform):
    u, v, depth = viewport
    need(all(math.isfinite(x) for x in viewport), 'Nonfinite viewport')
    if not (.04 < depth < 100 and 0 <= u <= 1 and 0 <= v <= 1):
        return None
    sx, sy = u * 1920, (1 - v) * 1080
    x0, y0, x1, y1 = transform['crop']
    if not (x0 <= sx <= x1 and y0 <= sy <= y1):
        return None
    x, y = transform['rect'][:2]
    return [x + (sx - x0) * transform['scale'], y + (sy - y0) * transform['scale']]


def caption_contract(cue):
    if cue is None:
        return
    need(isinstance(cue.get('text'), str) and 1 <= len(cue.get('lines', [])) <= 2
         and ' '.join(cue['lines']) == cue['text'], 'Exact one/two-line authored clause required')
    need(len(cue.get('emphasis', [])) <= 1, 'Only one caption emphasis span')
    for span in cue.get('emphasis', []):
        line, start, end = span['line'], span['start'], span['end']
        need(all(type(v) is int for v in (line, start, end)) and 0 <= line < len(cue['lines'])
             and 0 <= start < end <= len(cue['lines'][line]) and span['role'] in ('term', 'result', 'problem'),
             'One exact caption line/span/semantic role required')


def definition_rows(term):
    """One English (Korean) heading, then one/two exact authored meaning lines."""
    need(term.get('presentation') == 'definition', 'Explicit term definition required')
    matches = [lines for en, ko, lines in TERM_DEFINITIONS
               if term.get('english') == en and term.get('korean') == ko
               and term.get('meaning') == ' '.join(lines)]
    need(len(matches) == 1, 'Definition must preserve an exact current glossary term/meaning')
    return [term['english'] + ' (' + term['korean'] + ')', *matches[0]]


def cat_allowed(layout, purpose, term=None):
    return layout == 'single-player' and purpose == 'hero' and (term is None or term.get('presentation') == 'chip')


def validate_selection(layout, modes, frame, purpose='explanation', cat_pose=None, term=None):
    need(layout in LAYOUTS and type(frame) is int and 0 <= frame < 3120, 'Current capture frame/layout required')
    count = 2 if layout.startswith('ab-') else 1
    need(len(modes) == count and len(set(modes)) == count, 'A/B uses two distinct modes at the same frame')
    if 'broken-link' in modes and any(c == 'player' for c, _, _ in LAYOUTS[layout]):
        need(frame < 2880, 'Late broken-link player view is excluded, not held or replaced')
    need(cat_pose is None or cat_allowed(layout, purpose, term), 'Large cat is off for maps, dual/A-B and definition cards')
    need(cat_pose is None or cat_pose in ('puzzled', 'realize', 'relief'), 'Only approved original cat poses')


def packet_contract(packet):
    need(packet.get('schemaVersion') == '11-05-native-composition-packet-v1'
         and packet.get('physicalInputFingerprint') == PHYSICAL
         and packet.get('fingerprint') == digest({k: v for k, v in packet.items() if k != 'fingerprint'}),
         'Current unmodified native composition packet required')
    validate_selection(packet['layout'], packet['modes'], packet['nativeFrame'], packet['purpose'], packet['catPose'], packet['term'])
    if packet['term'] and packet['term'].get('presentation') == 'definition':
        definition_rows(packet['term'])
    need(len(packet['panels']) == len(LAYOUTS[packet['layout']]), 'Panel count differs')
    keys = []
    for i, (panel, (camera, crop, container)) in enumerate(zip(packet['panels'], LAYOUTS[packet['layout']])):
        mode = packet['modes'][i if packet['layout'].startswith('ab-') else 0]
        frame = packet['nativeFrame']
        need(panel['mode'] == mode and panel['camera'] == camera and panel['nativeFrame'] == frame
             and panel['key'] == f'{mode}/{camera}/{frame:04}' and panel['transform'] == fit(crop, container),
             'Source cut/frame/camera/crop changed without clearing and rebuilding its packet')
        path = Path(panel['sourceImage']['path']).resolve()
        need(path.is_relative_to((MEDIA / 'native-attempts').resolve())
             and path.parts[-4:] == ('capture', mode, camera, f'{frame:04}.jpg')
             and re.fullmatch('[0-9a-f]{64}', panel['sourceImage']['sha256']), 'Selected actual source panel pin required')
        keys.append(panel['key'])
    need(len(set(keys)) == len(keys) and len(packet['commands']) <= 2, 'Duplicate panels or excessive marks')
    need(all(v['sourcePanel'] in keys for v in packet['commands']), 'Guide survived a source cut')
    need(not (packet['catPose'] and packet['commands']), 'Show the hero reaction after clearing essential target marks')
    need(not (packet['term'] and packet['term'].get('presentation') == 'definition' and packet['commands']),
         'Clear target marks for the definition focus')


def measured_label_width(text):
    from PIL import ImageFont
    spec = read(ROOT / 'projects/shorts-leveldesign-03-02/visual-layout-v1.json')
    row = next(v for v in spec['fontMeasurement']['fontFiles'] if Path(v['path']).name == 'NotoSansKR-VF.ttf')
    path = checked(row)
    font = ImageFont.truetype(str(path), 46)
    font.set_variation_by_axes([700])
    return math.ceil(font.getlength(text)) + 24


class DecodedPanels(dict):
    def __init__(self, packet):
        super().__init__()
        self.packetFingerprint = packet['fingerprint']
        self.sourcePins = {v['key']: v['sourceImage']['sha256'] for v in packet['panels']}


def visibility(anchor, state, camera, frame, mode, source_image, guide_kind, policies):
    if anchor.get('active') is not True:
        return False, 'inactive'
    viewport = [anchor[camera + 'Viewport'][k] for k in ('x', 'y', 'z')]
    if not (.04 < viewport[2] < 100 and 0 <= viewport[0] <= 1 and 0 <= viewport[1] <= 1):
        return False, 'outside-camera'
    uv = project(state[camera + 'VP'], [anchor['world'][k] for k in ('x', 'y', 'z')])
    need(max(abs(a - b) for a, b in zip(uv, viewport[:2])) <= .0002, 'Projection differs from actual current matrix')
    ray = anchor[camera + 'Ray']
    if camera == 'player':
        return (False, 'earlier-occluder') if ray['hitBeforeTarget'] else (True, 'actual-perspective-point-ray')
    # Preserve the recorded diagonal query. It is not an orthographic pixel ray.
    for policy in policies:
        collider = policy.get('targetSurfaceCollider', policy.get('requiredObservedColliderName'))
        if (policy.get('method') == 'reviewed-frame-set' and policy.get('mode') == mode
                and policy.get('camera') == camera and policy.get('anchorId') == anchor['id']
                and frame in policy.get('visibleFrames', []) and guide_kind in policy.get('allowedGuideKinds', [])
                and policy.get('sourceImage', {}).get('sha256') == source_image['sha256']
                and Path(policy['sourceImage']['path']).resolve() == Path(source_image['path']).resolve()
                and ray['hit'] is True and ray['hitBeforeTarget'] is True and ray['hitCollider'] == collider):
            return True, 'reviewed-held-surface-only'
    return False, 'orthographic-pixel-visibility-unverified'


class JsonLines:
    """Read-only in-memory offset index; one sequential hash pass, no sidecar writes."""
    def __init__(self, row):
        self.path = Path(row['path'])
        self.offsets = []
        h = hashlib.sha256()
        with self.path.open('rb') as handle:
            while True:
                offset = handle.tell()
                line = handle.readline()
                if not line:
                    break
                self.offsets.append(offset)
                h.update(line)
        need(len(self.offsets) == 3120 and h.hexdigest() == row['sha256'], 'Actual trace count/hash differs')
        self.stat = (self.path.stat().st_size, self.path.stat().st_mtime_ns)

    def at(self, frame):
        need((self.path.stat().st_size, self.path.stat().st_mtime_ns) == self.stat, 'Trace changed while composing')
        with self.path.open('rb') as handle:
            handle.seek(self.offsets[frame])
            row = json.loads(handle.readline())
        need(row['frame'] == frame, 'Native frame clock differs')
        return row


class NativeData:
    def __init__(self):
        self.inputs = []
        for name, expected in PINS.items():
            row = dict(path=str(PROJECT / name), sha256=expected)
            checked(row, PROJECT)
            self.inputs.append(row)
        self.narration = read(PROJECT / 'narration-final-v4.json')
        self.plan = read(PROJECT / 'native-presentation-plan-v4.json')
        self.evidence = read(PROJECT / 'native-evidence-v4.json')
        e = self.evidence
        need(e['captureComplete'] is True and e['remainingModes'] == [] and len(e['capturedModes']) == 8
             and e['physicalInputFingerprint'] == PHYSICAL, 'Exact current full8-mode capture required')
        for i, row in enumerate(self.plan['paragraphPresentation']):
            need(row['canonicalNarrationKo'] == self.narration['narrationKo'][i]
                 and row['canonicalNarrationEn'] == self.narration['paragraphsEn'][i], 'Current final narration text differs')
        checked(e['frameHashManifest'], MEDIA)
        frames = read(e['frameHashManifest']['path'])
        need(frames['physicalInputFingerprint'] == PHYSICAL and len(frames['frames']) == 49920, 'Complete frame proof required')
        self.images = {(row['mode'], row['camera'], Path(row['path']).stem): row for row in frames['frames']}
        need(len(self.images) == 49920, 'Duplicate source image identity')
        self.policies = self.plan['bindingAndVisibility']['targetSurfaceExceptions']
        self.proofs = {str(Path(row['path']).resolve()): row for row in e['captureProofs']}
        self.streams = {}

    def frame(self, mode, frame):
        need(mode in self.evidence['capturedModes'] and type(frame) is int and 0 <= frame < 3120, 'Unknown actual mode/frame')
        folder = Path(self.evidence['modeSources'][mode]['attempt']) / 'capture' / mode
        need(folder.resolve().is_relative_to((MEDIA / 'native-attempts').resolve()), 'Native folder escaped current scope')
        for name in ('states.jsonl', 'projected-anchors.jsonl'):
            key = (mode, name)
            if key not in self.streams:
                self.streams[key] = JsonLines(self.proofs[str((folder / name).resolve())])
        state = self.streams[(mode, 'states.jsonl')].at(frame)
        anchors = self.streams[(mode, 'projected-anchors.jsonl')].at(frame)['anchors']
        need(state['mode'] == mode and state['appliedCommandFrame'] == frame - 1, 'State/mode command clock differs')
        return dict(mode=mode, frame=frame, physicalInputFingerprint=PHYSICAL,
                    originalRequestFingerprint=self.evidence['modeSources'][mode]['originalRequestFingerprint'],
                    state=state, anchors=anchors, images={camera: self.images[(mode, camera, f'{frame:04}')] for camera in ('player', 'observer')})

    def packet(self, layout, modes, frame, guides=(), purpose='explanation', cat_pose=None, term=None):
        validate_selection(layout, modes, frame, purpose, cat_pose, term)
        need(not (term and term.get('presentation') == 'definition' and guides), 'Definition card is the focus; clear target marks first')
        need(not (cat_pose and guides), 'Clear source-attached target marks before the hero cat reaction')
        rows = [self.frame(mode, frame) for mode in modes]
        panels = []
        for index, (camera, crop, container) in enumerate(LAYOUTS[layout]):
            record = rows[index if layout.startswith('ab-') else 0]
            panels.append(dict(key=f'{record["mode"]}/{camera}/{frame:04}', mode=record['mode'], camera=camera,
                               nativeFrame=frame, sourceImage=record['images'][camera], transform=fit(crop, container)))
        commands = []
        need(len(guides) <= 2, 'At most two object-attached labels')
        for cue in guides:
            need(type(cue['panel']) is int and 0 <= cue['panel'] < len(panels), 'Current panel index required')
            need(cue['role'] in ('term', 'result', 'problem') and isinstance(cue['label'], str) and cue['label'].strip(), 'Semantic target label required')
            panel = panels[cue['panel']]
            record = next(row for row in rows if row['mode'] == panel['mode'])
            matches = [row for row in record['anchors'] if row['id'] == cue['anchorId']]
            need(len(matches) == 1, 'Unique actual anchor required')
            anchor = matches[0]
            ok, reason = visibility(anchor, record['state'], panel['camera'], frame, panel['mode'], panel['sourceImage'], cue['kind'], self.policies)
            point = mapped([anchor[panel['camera'] + 'Viewport'][k] for k in ('x', 'y', 'z')], panel['transform']) if ok else None
            if point is not None:
                need(cue['kind'] in ('point-label', 'blocked-port-label'), 'Outline needs separately verified saved mesh corners; never invent a bounding box')
                commands.append(dict(kind='point-label', point=point, label=cue['label'], labelCenter=cue['labelCenter'],
                                     labelWidth=measured_label_width(cue['label']), role=cue['role'], anchorId=anchor['id'], sourcePanel=panel['key'], visibilityReason=reason))
        packet = dict(schemaVersion='11-05-native-composition-packet-v1', physicalInputFingerprint=PHYSICAL,
                      nativeFrame=frame, modes=list(modes), layout=layout, panels=panels, commands=commands,
                      purpose=purpose, catPose=cat_pose, term=term, speechFrame=None, actualSpeechTimingVerified=False,
                      routeMeaning='intended-reference-input-only' if 'broken-link' in modes else 'source-bound-current-model-route')
        packet['fingerprint'] = digest(packet)
        packet_contract(packet)
        return packet

    def decoded_panels(self, packet):
        """Future explicit caller only; no call from preflight/tests and no subprocess."""
        from PIL import Image
        packet_contract(packet)
        images = DecodedPanels(packet)
        for panel in packet['panels']:
            path = checked(panel['sourceImage'], MEDIA)
            with Image.open(path) as source:
                need(source.size == (1920, 1080) and source.format == 'JPEG', 'Actual FHD JPEG required')
                images[panel['key']] = source.convert('RGB')
        return images


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    # Metadata/source preparation only. No trace indexing or source image decode.
    data = NativeData()
    print(json.dumps(dict(topicId='11.05', sourceMetadataBound=True, capturedModes=data.evidence['capturedModes'],
                          readyForFinalTimeline=False, reason='Current voice PCM, blind-ASR clause clocks and accepted mix are not bound here',
                          actualSpeechTimingVerified=False, imageDecoded=False, renderStarted=False, jobLaunched=False)))


if __name__ == '__main__':
    main()
