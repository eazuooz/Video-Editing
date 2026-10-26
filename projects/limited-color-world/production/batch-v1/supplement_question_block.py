"""One inspected native question-block event; no jobs or file mutation."""
import copy


def apply(plan, sources):
    cuts = plan['cuts']
    group = [c for c in cuts if c['paragraphIds'] == ['05-p02']]
    assert sum(c['frames'] for c in group) == 698
    origin = group[0]['startFrame']
    before = next(c for c in group if c.get('source') == 'wonder-before')
    after = next(c for c in group if c.get('source') == 'wonder-after')
    source = sources['wonder-block-cc']

    def shot(template, start, frames, source_start):
        cut = copy.deepcopy(template)
        cut.update(startFrame=start, endFrame=start + frames, frames=frames,
                   sourceStart=source_start, marks=[])
        return cut

    flower = shot(after, origin, 92, 1.368033)
    first_result = shot(after, origin + 92, 23, 2.9029)
    block = shot(before, origin + 115, 234, 6.8)
    block.update(source=source['id'], sourceFile=source['path'],
                 sourceSha256=source['sha256'],
                 sourceAttribution=source['url'] + ' | ' + source['licenseLabel'],
                 sourceAudioReason=source['sourceAudioReason'],
                 protectedRects=[[256, 80, 491, 240], [1624, 840, 1664, 872]])
    world_start = 2.9029 + 23 / 60
    world = shot(after, origin + 349, 349, world_start)

    def frame_label(cut, text):
        cut['marks'].append({
            'id': 'case-cause', 'shape': 'rect', 't0': 0,
            't1': min(3, cut['frames'] / 60), 'color': '#e8cf83',
            'thickness': 6, 'label': text, 'fontSize': 42,
            'labelPosition': [275, 7], 'x': 256, 'y': 80, 'w': 1408, 'h': 792})

    frame_label(flower, '원더플라워 접촉')
    frame_label(world, '꽃의 결과: 세계가 바뀜')
    scale = 1408 / 1920

    def key(t, x, y):
        radius = 82
        return {'t': t, 'x': 256 + (x - radius) * scale,
                'y': 80 + (y - radius) * scale,
                'w': radius * 2 * scale, 'h': radius * 2 * scale}

    block['marks'] = [
        {'id': 'question-block-hit', 'shape': 'circle', 't0': 0, 't1': .95,
         'color': 'green', 'thickness': 8, 'label': '블록 두드림', 'fontSize': 48,
         'labelPosition': [1080, 240],
         'keyframes': [key(0, 932, 383), key(.2, 902, 383),
                       key(.6, 820, 383), key(.95, 774, 383)],
         'frameEvidence': ['wonder-block-inspect/7.jpg', 'wonder-block-inspect/8.jpg'],
         'movingPixelReview': 'pending'},
        {'id': 'block-item-result', 'shape': 'circle', 't0': 1.2, 't1': 2.2,
         'color': 'green', 'thickness': 8, 'label': '아이템 등장', 'fontSize': 48,
         'labelPosition': [1080, 240],
         'keyframes': [key(1.2, 774, 314), key(2.2, 880, 314)],
         'frameEvidence': ['wonder-block-inspect/8.jpg', 'wonder-block-inspect/9.jpg'],
         'movingPixelReview': 'pending'}]
    # Keep the approved green role while separating its pale line from the sky.
    # The matching black keyline is an editorial outline, not another detector.
    outlined = []
    for mark in block['marks']:
        keyline = copy.deepcopy(mark)
        keyline.update(id='keyline-' + mark['id'], color='#000000', thickness=16)
        outlined.extend([keyline, mark])
    block['marks'] = outlined

    shift = world_start + 349 / 60 - 8
    for cut in cuts:
        if (cut['startFrame'] >= group[-1]['endFrame']
                and cut.get('source') == 'wonder-after' and cut['sourceStart'] >= 8):
            cut['sourceStart'] += shift
            if cut['sourceStart'] + cut['frames'] / 60 > 18.284933:
                raise ValueError('Later confirmation crosses the next native shot change')
    index = cuts.index(group[0])
    cuts[index:index + len(group)] = [flower, first_result, block, world]
    for i, cut in enumerate(cuts):
        cut['id'] = f'cut{i:03d}'
    plan['questionBlockActionSupplement'] = {
        'source': source['id'], 'nativeWindow': [6.8, 10.7],
        'globalWindow': [block['startFrame'] / 60, block['endFrame'] / 60],
        'firstObservedUsedBlockAndMushroom': 8.0,
        'sourceCaseLabelsPreventMisattribution': True,
        'laterUniqueWorldSourceShiftSeconds': shift,
        'newFrames': 0, 'newVoice': False, 'actualAndMcTotalsUnchanged': True}
    return plan
