"""D22 measured, native-speed semantic edit builder. No media jobs.

--capacity-audit reads only current sources/scripts/banks, without inventing a
voice clock. --dry-run also allocates when actual reviewed48k timing exists.
Default builds edit-plan.json and independent Motion Canvas cut wrappers only
after that timing exists. Infeasible semantic/atomic/60:40 constraints are a
hard error, never a reason to loop, slow footage or accelerate the voice.

Optional --allocations is a reviewed JSON {allocations:[{bankId,paragraphIds,
startFrame,frames,sourceStart}]} on the actual global60fps clock. It replaces
the automatic proposal and must satisfy every invariant. This is an editing
override, not an estimated timing input. --audio-review accepts a hash-bound
{sources:{id:{sha256,sourceAudioEnabled,reason,reviewed:true}}} decision record.
Pending source audio is explicit in the edit and final mixing must reject it.
"""
from __future__ import annotations

import argparse
import copy
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
from storage_paths import (repo_path as routed_repo_path, relative as routed_relative,
                           logical_path, write_path as routed_write_path, same_logical_tree)
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
LOCAL = PROJECT / 'production/local/reference-preserving-v2'
MC = ROOT / 'motion-canvas/src/projects/similar-game-design/revision-v2'
NARRATION = ROOT / 'shared/output/narration/similar-game-design/reference-preserving-v2'
BANKS = PROJECT / 'planning/semantic-banks-v2.json'
FPS, RATE, INTRO, OUTRO = 60, 48000, 120, 600
MODES = {
    'overview-choice': 'choice', 'overview-three-experiences': 'overview',
    'route-goal-ab': 'purpose', 'familiar-loop': 'choice',
    'refinement-layer': 'effort', 'completion-flow': 'complete',
    'completion-to-choice': 'choice', 'repeatable-action': 'choice',
    'ore-before-after': 'purpose', 'purpose-summary': 'purpose',
    'role-player-author': 'role', 'world-choice': 'role',
    'competition-one-variable': 'competition', 'competition-rule': 'competition',
    'appeal-dimensions': 'appeals', 'goal-control-feedback': 'effort',
    'combination-identity': 'appeals', 'closing-answer': 'conclusion',
}
BOUNDARY_BRIDGES = {
    'engineer-extraction': {'from': '05-p04', 'to': '06-p01', 'throughCaptionUnit': 0,
        'expectedClause': '목적이 이동의 판단을 바꿨다면,',
        'reason': 'Keep the complete observed escape result under the next chapter’s inherited movement-purpose clause; finish before Mario is named or jumping is indicated.'},
}
EVENT_SPEECH_STARTS = {
    'mm-versus-start': {'paragraph': '07-p01', 'captionUnit': 2,
        'expectedClause': '멀티플레이 대전에서는 여러 캐릭터가,',
        'reason': 'Shared countdown/start must overlap the actual multiplayer/start-signal and relative-position clauses, not finish during the preceding designer-role transition.'},
}
VISUAL_STEPS = {'overview':3, 'complete':4, 'choice':4, 'purpose':4,
                'role':4, 'effort':4, 'competition':4, 'appeals':4, 'conclusion':3}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def path(value):
    return routed_repo_path(value)


def rel(value):
    return routed_relative(value)


def artifact(value):
    return {'path': rel(value), 'sha256': digest(value)}


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def checked_write(destination, content, *, generated=False):
    """No incompatible media/plan replacement. Generated source may be refreshed."""
    destination = routed_write_path(destination)
    if destination.exists() and destination.read_text('utf-8-sig') == content:
        return
    if destination.exists() and not generated:
        raise ValueError(f'Existing incompatible output is preserved: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def frame(seconds):
    return int(math.floor(float(seconds) * FPS + .5))


def native_frames(seconds):
    return int(Decimal(str(seconds)) * FPS)


def validate_inputs(bank_path):
    import audio_pipeline as audio
    ko, en, spoken, files = audio.scripts()
    plan = read(bank_path)
    if (plan.get('project'), plan.get('revision')) != ('similar-game-design', 'reference-preserving-v2'):
        raise ValueError('Semantic banks belong to another project/revision')
    paragraphs = {f"{s['id']}-p{i+1:02d}": line for s in ko['scenes'] for i, line in enumerate(s['lines'])}
    if {p['id']: p['ko'] for p in plan['paragraphs']} != paragraphs:
        raise ValueError('Bank bindings differ from the current complete Korean script')
    banks = {b['id']: b for b in plan['banks']}
    if len(banks) != len(plan['banks']):
        raise ValueError('Duplicate semantic bank ID')
    by_hash = {}
    for sid, source in plan['sources'].items():
        source_file = path(source.get('relativePath', source['path']))
        if not source_file.is_file() or digest(source_file) != source['sha256']:
            raise ValueError(f'Missing/changed actual source: {sid}')
        if source['width'] < 1920 or source['height'] < 1080:
            raise ValueError(f'Underlying source is not genuine FHD: {sid}')
        if not source.get('rightsEvidenceFile') or not source.get('sourceUrl'):
            raise ValueError(f'Missing original URL/rights evidence: {sid}')
        if not path(source['rightsEvidenceFile'].split('#')[0]).is_file():
            raise ValueError(f'Missing primary rights record: {sid}')
        if 'independent-gameplay' not in source.get('provenance', ''):
            raise ValueError(f'Research reference cannot enter actual banks: {sid}')
    for bank in banks.values():
        source = plan['sources'][bank['sourceId']]
        if not (0 <= bank['in'] < bank['out'] <= source['seconds'] + .001):
            raise ValueError(f'Bank outside actual source: {bank["id"]}')
        if not set(bank['allowedParagraphIds']) <= paragraphs.keys():
            raise ValueError(f'Unknown paragraph binding: {bank["id"]}')
        guard = bank.get('eventGuard', {})
        if guard.get('atomic') and not (bank['in'] <= guard['in'] < guard['out'] <= bank['out']):
            raise ValueError(f'Atomic event outside eligible bank: {bank["id"]}')
        by_hash.setdefault(source['sha256'], []).append((bank['in'], bank['out'], bank['id']))
    for ranges in by_hash.values():
        ranges.sort()
        for left, right in zip(ranges, ranges[1:]):
            if right[0] < left[1] - 1e-7:
                raise ValueError(f'Overlapping source bank intervals: {left[2]} / {right[2]}')
    return plan, ko, files


def capacity_report(plan, files):
    sources = plan['sources']
    total = sum(Decimal(str(b['out'])) - Decimal(str(b['in'])) for b in plan['banks'])
    rows = []
    for p in plan['paragraphs']:
        eligible = [b for b in plan['banks'] if p['id'] in b['allowedParagraphIds']]
        rows.append({'paragraph': p['id'], 'preferredMode': p['preferredMode'],
                     'eligibleBankIds': [b['id'] for b in eligible],
                     'eligibleNativeSeconds': float(sum(Decimal(str(b['out']))-Decimal(str(b['in'])) for b in eligible)),
                     'note': 'Overlapping paragraph eligibility is not additive source capacity.'})
    return {'status': 'capacity-only-no-invented-timing', 'scripts': files,
            'semanticBanks': artifact(BANKS), 'globalUniqueNativeSeconds': float(total),
            'maximumBodySecondsAt60PercentIfAllEligible': float(total / Decimal('.6')),
            'requiredAtomicBanks': plan['constraints']['requiredAtomicEvents'],
            'sourceAudioPending': [sid for sid, s in sources.items() if s.get('sourceAudioReviewStatus') == 'pending'],
            'paragraphs': rows, 'timingPresent': (NARRATION/'source-scene-timings.json').is_file(),
            'sourceNativeDimensionsAndHashesChecked': True,
            'actualDecodedFhdReprobe': 'Performed again by video_pipeline immediately before source rendering',
            'ratioFeasibility': 'Unknown until measured48k paragraph/caption windows are available.',
            'noMediaJobs': True}


def measured_clock(plan, ko, script_files, timing_path):
    import soundfile as sf
    import caption_pipeline as captions
    timing = read(timing_path)
    review = read(NARRATION / 'scene-split-review.json')
    if timing['sampleRate'] != RATE or review.get('decodedSourceReconstructionIdentical') is not True:
        raise ValueError('Require reviewed48k scene split with exact sample reconstruction')
    if review['inputs']['scripts'] != script_files:
        raise ValueError('Timing review is bound to another narration revision')
    if [s['id'] for s in ko['scenes']] != [s['id'] for s in timing['scenes']]:
        raise ValueError('Measured scene order differs from complete narration')
    units = read(HERE / 'caption-units.json')
    if units['scriptInputs'] != script_files:
        raise ValueError('Authored caption clauses have stale script hashes')
    aliases = read(PROJECT / 'script/reference-preserving-v2/caption-aliases.json')
    if isinstance(aliases.get('aliases'), dict):
        aliases = aliases['aliases']
    rows, scenes, previous_sample = [], [], 0
    for scene, script_scene in zip(timing['scenes'], ko['scenes']):
        source = path(scene['path'])
        info = sf.info(source)
        if (scene['startSample'] != previous_sample or scene['samples'] != scene['endSample'] - previous_sample
                or info.samplerate != RATE or info.frames != scene['samples'] or info.channels != 1
                or digest(source) != scene['sha256']):
            raise ValueError(f'Noncontinuous/stale actual48k scene PCM: {scene["id"]}')
        previous_sample = scene['endSample']
        recognition = read(path(scene['wordFile']))
        if recognition['audio_sha256'] != scene['sha256']:
            raise ValueError('Scene words no longer describe the actual PCM')
        origin = INTRO / FPS + scene['startSample'] / RATE
        scenes.append({'id': scene['id'], 'title': scene['title'], 'voiceStart': origin,
                       'voiceDuration': scene['samples'] / RATE,
                       'sourceStartSample': scene['startSample'], 'sourceEndSample': scene['endSample'],
                       'startFrame': INTRO + scene['startSample'] // (RATE // FPS),
                       'endFrame': INTRO + math.ceil(scene['endSample'] / (RATE // FPS)),
                       'audioFile': scene['path'], 'audioSha256': scene['sha256'],
                       'paragraphStarts': scene['paragraphStarts']})
        paras = scene['paragraphs']
        for i, para in enumerate(paras):
            pid = f"{scene['id']}-p{i+1:02d}"
            if para['text'] != script_scene['lines'][i]:
                raise ValueError(f'Measured paragraph text mismatch: {pid}')
            lower = (paras[i-1]['end'] + para['start'])/2 if i else 0
            upper = (para['end'] + paras[i+1]['start'])/2 if i+1 < len(paras) else scene['duration']
            words = [w for w in recognition['words'] if lower < w['timestamp'][1] <= upper + 1e-7]
            # The canonical caption bridge groups pathological ASR fragments.
            # Do the same here, preserving complete text and measured union times.
            grouped, pending = [], None
            for original in words:
                w = copy.deepcopy(original); a, b = w['timestamp']
                if a == b:
                    if pending is not None:
                        raise ValueError(f'Consecutive untimed ASR fragments: {pid}')
                    pending = w; continue
                if pending is not None:
                    if abs(pending['timestamp'][1]-a) > .002:
                        raise ValueError(f'Nonadjacent untimed ASR fragment: {pid}')
                    w['text'] = pending['text'] + w['text']; pending = None
                if grouped and a < grouped[-1]['timestamp'][1] - .002:
                    prior = grouped.pop()
                    if a < prior['timestamp'][0]:
                        raise ValueError(f'Reversed ASR phrase: {pid}')
                    w = {'text': prior['text']+w['text'], 'timestamp': [prior['timestamp'][0], max(b,prior['timestamp'][1])]}
                grouped.append(w)
            if pending is not None:
                raise ValueError(f'Trailing untimed ASR fragment: {pid}')
            starts, ends, evidence = captions.align_characters(para['text'], grouped, scene['duration'], aliases, .93)
            paired = units['paragraphs'][pid]
            if not paired.get('semanticPairingReviewed'):
                raise ValueError(f'Unreviewed bilingual clauses: {pid}')
            cursor, cues = 0, []
            for unit in paired['captionUnits']:
                count = len(captions.normalized(unit['ko'], aliases))
                cues.append({'ko': unit['ko'], 'start': origin+starts[cursor], 'end': origin+ends[cursor+count-1]})
                cursor += count
            if cursor != len(starts):
                raise ValueError(f'Caption clauses changed whole paragraph: {pid}')
            rows.append({'id': pid, 'scene': scene['id'], 'text': para['text'],
                         'startFrame': frame(origin+lower), 'endFrame': frame(origin+upper),
                         'speechStart': origin+para['start'], 'speechEnd': origin+para['end'],
                         'captionCues': cues, 'characterStarts': [origin+x for x in starts],
                         'normalizedText': captions.normalized(para['text'], aliases),
                         'alignment': evidence})
    body = math.ceil(previous_sample / (RATE // FPS))
    # Visual boundaries form a single contiguous60fps clock. Fractional sample
    # scene edges remain exact in voiceStart and may share one visual frame.
    rows[0]['startFrame'] = INTRO
    for left, right in zip(rows, rows[1:]):
        right['startFrame'] = left['endFrame']
    rows[-1]['endFrame'] = INTRO + body
    if any(p['endFrame'] <= p['startFrame'] for p in rows):
        raise ValueError('Collapsed actual paragraph visual interval')
    return timing, scenes, rows, body


def subtract(interval, occupied):
    result = [interval]
    for a, b in sorted(occupied):
        result = [(x, min(y, a)) for x, y in result if x < a and min(y,a)>x] + [
            (max(x,b), y) for x,y in result if y>b and y>max(x,b)]
    return sorted(result)


def merge_intervals(intervals):
    result = []
    for a,b in sorted(intervals):
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0],max(b,result[-1][1]))
        else:
            result.append((a,b))
    return result


def permitted_windows(bank, specs, measured, *, required=False, mixed_reserve_frames=0):
    """Only spoken claims explicitly bound to this source; no quota padding."""
    import caption_pipeline as captions
    allowed = bank.get('reservedForParagraphIds') if required else bank['allowedParagraphIds']
    allowed = allowed or bank['allowedParagraphIds']
    result = []
    for pid in allowed:
        if pid not in measured:
            raise ValueError(f'Unknown actual paragraph: {pid}')
        spec, row = specs[pid], measured[pid]
        if spec['preferredMode'] == 'diagram':
            continue
        a,b = row['startFrame'],row['endFrame']
        event_start=EVENT_SPEECH_STARTS.get(bank['id']) if required else None
        if event_start and pid==event_start['paragraph']:
            cue=row['captionCues'][event_start['captionUnit']]
            if cue['ko']!=event_start['expectedClause']:
                raise ValueError('The exact actual-event introduction clause changed')
            a=max(a,frame(cue['start']))
        bridge=BOUNDARY_BRIDGES.get(bank['id']) if required else None
        if bridge and pid==bridge['from']:
            next_row=measured[bridge['to']]
            cue=next_row['captionCues'][bridge['throughCaptionUnit']]
            if cue['ko']!=bridge['expectedClause'] or next_row['startFrame']!=row['endFrame']:
                raise ValueError('The exact measured chapter-inheritance clause changed; re-review atomic carry')
            b=frame(cue['end'])
        guards = spec.get('beatOrderGuard', [])
        if guards:
            for i, guard in enumerate(guards):
                if bank['sourceId'] not in guard['allowedSourceIds']:
                    continue
                token = captions.normalized(guard['speechContains'])
                index = row['normalizedText'].find(token)
                if index < 0:
                    raise ValueError(f'Source-order cue not present: {pid}/{token}')
                left = frame(row['characterStarts'][index])
                right = b
                if i+1 < len(guards):
                    next_token = captions.normalized(guards[i+1]['speechContains'])
                    next_index = row['normalizedText'].find(next_token)
                    right = frame(row['characterStarts'][next_index])
                if right>left:
                    result.append((left,right))
            continue
        # Mixed paragraphs retain their last directly authored clause for the
        # adjacent abstraction. Required complete native events take priority.
        if spec['preferredMode']=='mixed' and not required and mixed_reserve_frames:
            reserve = min(mixed_reserve_frames, max(1,b-a-1))
            b -= reserve
        if b>a:
            result.append((a,b))
    # An uninterrupted non-atomic movement beat may inherit the same source's
    # explicitly eligible adjacent claim. Paragraph IDs are editing metadata,
    # not a reason to insert a fraction-second diagram. Atomic continuation
    # remains limited to its explicitly declared native-event group.
    continuing=(required and bank.get('atomicContinuationParagraphGroup')) or not bank.get('eventGuard',{}).get('atomic')
    return merge_intervals(result) if continuing else result


def minimum_frames(bank):
    seconds = float(bank['minMeaningfulSeconds'])
    guard = bank.get('eventGuard', {})
    if guard.get('atomic'):
        seconds = max(seconds,float(guard['out'])-float(guard['in']))
    return math.ceil(seconds*FPS-1e-7)


def source_inpoint(bank, length):
    duration = length/FPS
    guard=bank.get('eventGuard',{})
    if guard.get('atomic'):
        # Balance spare before/after around the verified complete event.
        spare=duration-(guard['out']-guard['in'])
        start=max(float(bank['in']),float(guard['in'])-spare/2)
        start=min(start,float(bank['out'])-duration)
        if start>guard['in']+1e-7 or start+duration<guard['out']-1e-7:
            raise ValueError(f'Cannot preserve native atomic guard: {bank["id"]}')
        return round(start,9)
    return float(bank['in'])


def automatic_allocation(plan, rows, target):
    """Finite deterministic proposals. A failed greedy proposal is a blocker,
    not a proof that all possible edits are impossible; a reviewed override can
    resolve it without changing any validation requirement.
    """
    specs={p['id']:p for p in plan['paragraphs']}
    measured={p['id']:p for p in rows}
    banks={b['id']:b for b in plan['banks']}
    required=list(plan['constraints']['requiredAtomicEvents'])
    best=None;best_feasible=None
    for trial in range(192):
        rng=random.Random(trial)
        # Three seconds is the first compositional preference, not a rule or a
        # false feasibility bound. Actual meaningful events may use more of a
        # mixed passage; the complete body still retains exactly40% explanation.
        mixed_reserve_frames=[180,120,60,0][trial//48]
        selected=[]
        failed=[]
        optional=[b for b in banks if b not in required]
        # Most-constrained banks first; deterministic alternative orders handle
        # the competing familiar-loop/reprise capacities without extra footage.
        if trial:
            rng.shuffle(optional)
        else:
            optional.sort(key=lambda bid:(len(banks[bid]['allowedParagraphIds']),-minimum_frames(banks[bid])))
        ordering=required+optional
        for bid in ordering:
            bank=banks[bid]; is_required=bid in required
            windows=permitted_windows(bank,specs,measured,required=is_required,
                                      mixed_reserve_frames=mixed_reserve_frames)
            free=[(a,b) for window in windows for a,b in subtract(window,[(s['startFrame'],s['endFrame']) for s in selected])]
            candidates=[]
            for a,b in free:
                cap=min(b-a,native_frames(Decimal(str(bank['out']))-Decimal(str(bank['in']))))
                if cap<minimum_frames(bank):
                    continue
                # Prefer direct primary paragraphs and leaving larger optional
                # claim windows available for their less-flexible neighbours.
                preferred=any(measured[p]['startFrame']<=a<measured[p]['endFrame'] for p in bank.get('preferredParagraphIds',[]) if p in measured)
                candidates.append((cap,preferred,a,b))
            if not candidates:
                if is_required:
                    failed.append(bid)
                continue
            if is_required:
                # Earliest truthful passage, not a later recap, anchors the event.
                cap,_preferred,a,_b=min(candidates,key=lambda v:v[2])
            else:
                cap,_preferred,a,_b=max(candidates,key=lambda v:(v[1],v[0],-v[2]))
            if is_required:
                cap=minimum_frames(bank)
            selected.append({'bankId':bid,'startFrame':a,'endFrame':a+cap,
                             'minFrames':minimum_frames(bank),'maxFrames':cap,'requiredAtomic':is_required})
            # Reserve ALL complete required events before spending spare space
            # on one longer event (world branch and course placement overlap
            # the same truthful paragraph group). Extend only into free space.
            if required and bid==required[-1]:
                for prior in selected:
                    prior_bank=banks[prior['bankId']]
                    windows=permitted_windows(prior_bank,specs,measured,required=True)
                    window=next((w for w in windows if w[0]<=prior['startFrame'] and prior['endFrame']<=w[1]),None)
                    if not window:
                        continue
                    following=min([c['startFrame'] for c in selected if c['startFrame']>=prior['endFrame'] and c is not prior]+[window[1]])
                    cap=min(following-prior['startFrame'],window[1]-prior['startFrame'],
                            native_frames(Decimal(str(prior_bank['out']))-Decimal(str(prior_bank['in']))))
                    prior['endFrame']=prior['startFrame']+cap;prior['maxFrames']=cap
        # Eligibility banks are not forced shots. A non-atomic long interval may
        # provide several DIFFERENT contiguous movement/action beats, each with
        # its own minimum meaningful length. Spend only its previously unused
        # native tail, never repeat an interval or split an atomic event.
        for bid in optional:
            bank=banks[bid]
            if bank.get('eventGuard',{}).get('atomic'):
                continue
            used=sum(c['maxFrames'] for c in selected if c['bankId']==bid)
            native_capacity=native_frames(Decimal(str(bank['out']))-Decimal(str(bank['in'])))
            while native_capacity-used>=minimum_frames(bank):
                windows=permitted_windows(bank,specs,measured,mixed_reserve_frames=mixed_reserve_frames)
                free=[(a,b) for w in windows for a,b in subtract(w,[(c['startFrame'],c['endFrame']) for c in selected])]
                candidates=[(min(b-a,native_capacity-used),a) for a,b in free
                            if min(b-a,native_capacity-used)>=minimum_frames(bank)]
                if not candidates:
                    break
                cap,a=max(candidates)
                selected.append({'bankId':bid,'startFrame':a,'endFrame':a+cap,
                    'sourceBaseStart':float(bank['in'])+used/FPS,
                    'minFrames':minimum_frames(bank),'maxFrames':cap,'requiredAtomic':False})
                used+=cap
        maximum=sum(c['maxFrames'] for c in selected)
        minimum=sum(c['minFrames'] for c in selected)
        score=(not failed, maximum>=target and minimum<=target,maximum)
        candidate={'allocations':selected,'failedRequired':failed,'minimumFrames':minimum,'maximumFrames':maximum}
        if best is None or score>best[0]:
            best=(score,candidate)
        if failed or not minimum<=target<=maximum:
            continue
        # Begin with the complete meaningful proposal. Remove only optional
        # extension frames beside an existing explanation, avoiding a series
        # of blink-length new diagram tails produced by expanding from minima.
        remaining=maximum-target
        selected.sort(key=lambda c:c['startFrame'])
        for i,cut in enumerate(selected):
            cut['leftGap']=cut['startFrame']-(selected[i-1]['endFrame'] if i else rows[0]['startFrame'])
            cut['rightGap']=(selected[i+1]['startFrame'] if i+1<len(selected) else rows[-1]['endFrame'])-cut['endFrame']
            cut['frames']=cut['maxFrames']
        for cut in sorted(selected,key=lambda c:(c['requiredAtomic'],-max(c['leftGap'],c['rightGap']),-(c['maxFrames']-c['minFrames']))):
            remove=min(remaining,cut['maxFrames']-cut['minFrames'])
            cut['frames']-=remove
            if cut['leftGap']>cut['rightGap']:
                cut['startFrame']+=remove
            else:
                cut['endFrame']-=remove
            remaining-=remove
        for cut in selected:
            cut['sourceStart']=cut.get('sourceBaseStart',source_inpoint(banks[cut['bankId']],cut['frames']))
        assert remaining==0
        gaps=subtract((rows[0]['startFrame'],rows[-1]['endFrame']),[(c['startFrame'],c['endFrame']) for c in selected])
        short=[b-a for a,b in gaps if 0<b-a<90]
        quality=(len(short),sum(short),len(selected),-mixed_reserve_frames)
        receipt={'method':'finite semantic interval allocation; exact integer-frame length within each native guard',
                         'proposalTrial':trial,'minimumMeaningfulFrames':minimum,'selectedMaximumFrames':maximum,
                         'optionalMixedParagraphDiagramReserveFrames':mixed_reserve_frames,
                         'targetActualFrames':target,'shortExplanationGapCount':len(short),
                         'alternation':'Meaningful event completion takes priority over5–10s guidance.'}
        if best_feasible is None or quality<best_feasible[0]:
            best_feasible=(quality,copy.deepcopy(selected),receipt)
    if best_feasible:
        return best_feasible[1],best_feasible[2]
    detail=best[1]
    raise ValueError('Automatic semantic allocation needs review; no render allowed. '+json.dumps({
        'targetFrames':target,'maximumProposedFrames':detail['maximumFrames'],
        'minimumMeaningfulFrames':detail['minimumFrames'],'requiredEventsUnplaced':detail['failedRequired'],
        'remedy':'Inspect measured windows/source evidence; provide reviewed --allocations or obtain more concept-matched footage. Do not pad, loop, slow or change narration speed.'}))


def validate_allocation(allocations, plan, rows, target):
    banks={b['id']:b for b in plan['banks']};specs={p['id']:p for p in plan['paragraphs']}
    measured={p['id']:p for p in rows}; occupied=[];native={}; seen=set()
    required=set(plan['constraints']['requiredAtomicEvents'])
    for cut in sorted(allocations,key=lambda c:c['startFrame']):
        bank=banks[cut['bankId']];minimum=minimum_frames(bank)
        cut['endFrame']=cut['startFrame']+cut['frames']
        if cut['bankId'] in seen and bank.get('eventGuard',{}).get('atomic'):
            raise ValueError(f'Atomic event is replayed/fragmented: {cut["bankId"]}')
        seen.add(cut['bankId'])
        if cut['frames']<minimum:
            raise ValueError(f'Incomplete meaningful native event: {cut["bankId"]}')
        windows=permitted_windows(bank,specs,measured,required=cut['bankId'] in required)
        if not any(a<=cut['startFrame'] and cut['endFrame']<=b for a,b in windows):
            raise ValueError(f'Actual cut leaves its semantically bound spoken passage: {cut["bankId"]}')
        if occupied and cut['startFrame']<occupied[-1][1]:
            raise ValueError('Overlapping output actual cuts')
        occupied.append((cut['startFrame'],cut['endFrame']))
        start,end=cut['sourceStart'],cut['sourceStart']+cut['frames']/FPS
        if start<bank['in']-1e-7 or end>bank['out']+1e-7:
            raise ValueError(f'Actual source interval exceeds inspected bank: {cut["bankId"]}')
        guard=bank.get('eventGuard',{})
        if guard.get('atomic') and (start>guard['in']+1e-7 or end<guard['out']-1e-7):
            raise ValueError(f'Atomic before/action/result cut away: {cut["bankId"]}')
        source=plan['sources'][bank['sourceId']]
        native.setdefault(source['sha256'],[]).append((start,end,cut['bankId']))
        cut['paragraphIds']=[p['id'] for p in rows if p['startFrame']<cut['endFrame'] and p['endFrame']>cut['startFrame']]
    if not required<=seen:
        raise ValueError(f'Missing complete required native events: {sorted(required-seen)}')
    for ranges in native.values():
        ranges.sort()
        for a,b in zip(ranges,ranges[1:]):
            if b[0]<a[1]-1e-7:
                raise ValueError(f'Reused native source intervals: {a[2]}/{b[2]}')
    if sum(c['frames'] for c in allocations)!=target:
        raise ValueError('Actual allocation does not meet exact frame target')


def audio_decisions(plan, review_path):
    review=read(review_path) if review_path and Path(review_path).is_file() else {'sources':{}}
    decisions={}
    for sid,source in plan['sources'].items():
        decision=review['sources'].get(sid)
        if decision:
            if (decision.get('sha256')!=source['sha256'] or decision.get('reviewed') is not True
                    or not isinstance(decision.get('sourceAudioEnabled'),bool) or not decision.get('reason')):
                raise ValueError(f'Unverified/stale audio retain/mute decision: {sid}')
            decisions[sid]={**decision,'reviewStatus':'verified','evidence':artifact(review_path)}
        elif source.get('sourceAudioReviewStatus') in ('verified','reviewed','complete'):
            decisions[sid]={'sha256':source['sha256'],'sourceAudioEnabled':source['sourceAudioEnabled'],
                            'reason':source['sourceAudioReason'],'reviewStatus':'verified',
                            'evidence':artifact(BANKS)}
        else:
            decisions[sid]={'sha256':source['sha256'],'sourceAudioEnabled':False,'reviewStatus':'pending',
                            'reason':'Original stream preserved; final retain/mute review is required before mix.'}
    return decisions


def compose(plan, scenes, rows, body, allocations, allocation_receipt, decisions, inputs):
    banks={b['id']:b for b in plan['banks']};specs={p['id']:p for p in plan['paragraphs']}
    cuts=[];native=sorted(allocations,key=lambda c:c['startFrame'])
    # Include every paragraph edge unless an intact required actual event spans
    # it. That event retains all paragraph IDs instead of being cut in half.
    edges={INTRO,INTRO+body}
    for p in rows:
        edges.update([p['startFrame'],p['endFrame']])
    for c in native:
        edges={e for e in edges if not c['startFrame']<e<c['endFrame']}
        edges.update([c['startFrame'],c['endFrame']])
    edges=sorted(edges); mc_cursor=0
    assets=read(HERE/'visual-assets.json')
    image_paths={a['key']:'/'.join(['/@fs',str(logical_path(a['path'])).replace('\\','/')]) for a in assets['assets']}
    for a in assets['assets']:
        if digest(path(a['path']))!=a['sha256']:
            raise ValueError('Inspected explanation screenshot bytes changed')
    for a,b in zip(edges,edges[1:]):
        if b<=a:
            continue
        related=[p for p in rows if p['startFrame']<b and p['endFrame']>a]
        actual=next((c for c in native if c['startFrame']==a and c['endFrame']==b),None)
        cut={'id':f'cut{len(cuts):03d}','scene':related[0]['scene'], 'paragraphIds':[p['id'] for p in related],
             'startFrame':a,'endFrame':b,'frames':b-a,'playbackSpeed':1,'loop':False,
             'clearAtSourceCut':True,'marks':[], 'captionProtectedRect':[150,892,1784,1060]}
        if actual:
            bank=banks[actual['bankId']];source=plan['sources'][bank['sourceId']];audio=decisions[bank['sourceId']]
            if audio['reviewStatus']=='verified' and not audio['sourceAudioEnabled']:
                selected=(actual['sourceStart'],actual['sourceStart']+(b-a)/FPS)
                muted=merge_intervals([(r['in'],r['out']) for r in audio.get('muteRanges',[])])
                if not any(x<=selected[0]+1e-7 and selected[1]<=y+1e-7 for x,y in muted):
                    raise ValueError(f'Source mute leaves explicitly reviewed native ranges: {bank["id"]}')
            cut.update({'kind':'independent-gameplay','classification':'independent-gameplay',
                        'bankId':bank['id'],'source':bank['sourceId'],
                        'sourceFile':rel(path(source.get('relativePath',source['path']))),
                        'sourceStart':actual['sourceStart'],'sourceSha256':source['sha256'],
                        'sourceUrl':source['sourceUrl'],'sourceAttribution':{'game':source['game'],
                        'originalSourceUrl':source['sourceUrl'],'rightsEvidence':source['rightsEvidenceFile'],
                        'placement':'description-bottom-only'},'game':source['game'],
                        'sourceAudioEnabled':audio['sourceAudioEnabled'],'sourceAudioReviewStatus':audio['reviewStatus'],
                        'sourceAudioReason':audio['reason'],'sourceAudioReview':audio.get('evidence'),
                        'sourceAudioReviewScope':audio.get('reviewScope','Hash-bound source editorial decision'),
                        'sourceAudioActualListeningPending':True,
                        'sourceAudioMuteRanges':audio.get('muteRanges',[]),
                        'gameTitleChipPending':True,'viewport':[0,0,1920,1080],
                        'before':bank['before'],'action':bank['action'],'result':bank['result'],
                        'atomicGuard':bank.get('eventGuard'),'sourceNativeDimensions':[source['width'],source['height']],
                        'sourceNativeFps':source['nativeFPS'],'sourceFrameEvidence':bank['frameEvidence'],
                        'plannedAnnotationTrackIds':bank.get('annotationTrackIds',[]),
                        'annotationStatus':'anchors-only; moving tracking/occlusion/UI/caption clearance pending',
                        'protectedUI':source['protectedUI']})
            if bank['id']=='mm-versus-later':
                cut['nativeContinuity']='Separate later-race montage shot; timer/state jumps. Do not imply continuous elapsed race time.'
                cut['editorialTransitionLabel']='다른 대전 장면'
            bridge=BOUNDARY_BRIDGES.get(bank['id'])
            if bridge:
                preceding=next(p for p in rows if p['id']==bridge['from'])
                following=next(p for p in rows if p['id']==bridge['to'])
                cut['chapterBoundaryCarry']={**bridge,'carriedFrames':max(0,b-preceding['endFrame']),
                    'allowedThroughMeasuredSeconds':following['captionCues'][bridge['throughCaptionUnit']]['end'],
                    'actualCarryEndSeconds':b/FPS,'narrationPcmChanged':False,'addedSilence':False}
        else:
            p=max(related,key=lambda item:min(b,item['endFrame'])-max(a,item['startFrame']))
            spec=specs[p['id']];diagram=spec['diagramId']
            if diagram not in MODES:
                raise ValueError(f'No authored Motion Canvas mode for {diagram}')
            # Real authored clause starts relative to the CUT, including negatives
            # so a returning explanation keeps the already-revealed state.
            cues=[round(c['start']-a/FPS,9) for c in p['captionCues']]
            cut.update({'kind':'explanation','renderer':'Motion Canvas','implementationKind':'independently authored abstract relationship diagram',
                        'diagramId':diagram,'visual':MODES[diagram], 'cues':cues,
                        'title':next(s['title'] for s in scenes if s['id']==p['scene']),
                        'imagePaths':image_paths,'mcStartFrame':mc_cursor,'mcEndFrame':mc_cursor+b-a,
                        'renderedStartFrame':mc_cursor,
                        'renderedSource':rel(LOCAL/'rendered/similar-game-design-production-v2.mp4'),
                        'screenshotSourceRecords':assets['assets'],
                        'pictureKind':'our illustration with independently inspected gameplay screenshots',
                        'gameplayFrameAccounting':False})
            mc_cursor+=b-a
        cuts.append(cut)
    # A paragraph boundary is not a visual reset. Join a sub1.5s explanation
    # tail to the adjoining substantive explanation, carrying the main lesson's
    # actual clause cues rather than flashing an unreadable independent slide.
    joined=[]
    for cut in cuts:
        if (joined and joined[-1]['kind']==cut['kind']=='explanation'
                and (joined[-1]['frames']<90 or cut['frames']<90)):
            previous=joined.pop()
            primary=cut if cut['frames']>=previous['frames'] else previous
            merged=copy.deepcopy(primary)
            merged['startFrame']=previous['startFrame'];merged['endFrame']=cut['endFrame']
            merged['frames']=merged['endFrame']-merged['startFrame']
            merged['paragraphIds']=list(dict.fromkeys(previous['paragraphIds']+cut['paragraphIds']))
            merged['sceneIds']=list(dict.fromkeys([previous['scene'],cut['scene']]))
            merged['cues']=[cue+(primary['startFrame']-merged['startFrame'])/FPS for cue in primary['cues']]
            merged['boundaryLink']='A brief inherited clause joins the next/previous substantive explanation; no PCM, source interval or timing change.'
            joined.append(merged)
        else:
            joined.append(cut)
    cuts=joined;mc_cursor=0
    for index,cut in enumerate(cuts):
        cut['id']=f'cut{index:03d}'
        if cut['kind']=='explanation':
            overlaps=[(min(cut['endFrame'],p['endFrame'])-max(cut['startFrame'],p['startFrame']),p)
                      for p in rows if p['startFrame']<cut['endFrame'] and p['endFrame']>cut['startFrame']]
            overlap,primary=max(overlaps,key=lambda item:item[0])
            diagram=specs[primary['id']]['diagramId']
            cut.update({'primaryParagraphId':primary['id'],'primaryScene':primary['scene'],
                'primaryOverlapFrames':overlap,
                'paragraphOverlapFrames':{p['id']:n for n,p in overlaps},
                'primarySelection':'Greatest actual paragraph overlap in this unchanged cut interval',
                'diagramId':diagram,'visual':MODES[diagram],
                'title':next(s['title'] for s in scenes if s['id']==primary['scene']),
                'cues':[round(c['start']-cut['startFrame']/FPS,9) for c in primary['captionCues']]})
            count=VISUAL_STEPS[cut['visual']]
            def cue_at(c,i):
                return c['cues'][min(i,len(c['cues'])-1)]
            visible={i for i in range(count) if cue_at(cut,i)<=0}
            previous=cuts[index-1] if index else None
            if (previous and previous['kind']=='explanation' and previous['visual']==cut['visual']
                    and previous['endFrame']==cut['startFrame']):
                previous_duration=previous['frames']/FPS
                fully_shown={i for i in range(count) if i in previous.get('initialVisible',[])
                    or cue_at(previous,i)+.55*min(1,previous_duration/8)<=previous_duration}
                visible.update(fully_shown)
                cut['visibilityContinuity']={'fromCut':previous['id'],
                    'strategy':'Keep previously revealed diagram nodes visible; retain new paragraph speech cues and mechanic motion.',
                    'carriedStepIndices':sorted(fully_shown)}
            cut['initialVisible']=sorted(visible)
            cut['mcStartFrame']=mc_cursor;cut['renderedStartFrame']=mc_cursor
            mc_cursor+=cut['frames'];cut['mcEndFrame']=mc_cursor
    actual_frames=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')
    music=ROOT/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
    license_file=music.with_name('Nimbus-Eveningland.LICENSE.md')
    if digest(music)!='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08' or not license_file.is_file():
        raise ValueError('Approved original Nimbus music/license unavailable')
    branding=ROOT/'projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'
    membership=branding.with_name('membership.mp4')
    if not branding.is_file() or not membership.is_file():
        raise ValueError('Approved exact branding/member video segments unavailable')
    aliases=read(PROJECT/'script/reference-preserving-v2/caption-aliases.json')
    result={'schemaVersion':1,'slug':'similar-game-design','revision':'reference-preserving-v2',
            'status':'measured-internal-edit-pending-moving-review', 'timing':'actual48k-sample-clock-and-reviewed-full-source-ASR',
            'fps':FPS,'width':1920,'height':1080,'introFrames':INTRO,'outroFrames':OUTRO,
            'totalFrames':body+INTRO+OUTRO,'bodyFrames':body,'actualFrames':actual_frames,
            'explanationFrames':body-actual_frames,'mcFrames':mc_cursor,'expectedGameplayShare':.6,
            'ratioToleranceFrames':1,'ratioErrorFrames':actual_frames-.6*body,
            'scenes':scenes,'cuts':cuts,'captionAliases':aliases,
            'captionProtectedRect':[150,892,1784,1060],
            'brandingFile':rel(branding),'membershipFile':rel(membership),
            'brandingMembershipBytePreservation':[artifact(branding),artifact(membership)],
            'outputDir':rel(LOCAL/'edit'),'outputStem':'similar-game-design-v2',
            'mixFile':rel(LOCAL/'edit/final-mix.wav'),'captionsAss':rel(LOCAL/'edit/captions.ko.ass'),
            'audio':{'preserveGameAudio':True,'targetLufs':-16,'voicePeakDbfs':-2.5,
                     'gameLufs':-23,'gameNarrationRelativeDb':-10,'matchSceneRms':False,
                     'musicLufs':-31,'music':{'path':rel(music),'sha256':digest(music),
                     'licenseRecord':rel(license_file),'title':'Nimbus','artist':'Eveningland'}},
            'audioSourceReviewPending':sorted({c['source'] for c in cuts if c['kind']=='independent-gameplay' and c['sourceAudioReviewStatus']=='pending'}),
            'measuredParagraphs':rows, 'inputRecords':inputs,'allocation':allocation_receipt,
            'noLoops':True,'sourceRatePreserved':True,'narrationTimeStretch':False,
            'continuousVoiceSamples':True,'bodyEndPaddingSamples':body*(RATE//FPS)-scenes[-1]['sourceEndSample'],
            'editorAddedSourceCreditsRendered':False,'sourceCreditsPlacement':'bottom of upload description',
            'gameTitleChipLayout':'pending source-specific placement with actual game UI and fixed captions',
            'annotationReview':'Planned source anchors retained; no unverified tracking is rendered.',
            'humanReview':'pending; code/timing completion is not evidence of human viewing/listening',
            'baselineUploadPreserved':'_p1IqDeg6YE','automaticNextVideo':False}
    import video_pipeline as video
    video.validate_plan(result)
    return result


def wrappers(edit):
    outputs={};names=[]
    for c in edit['cuts']:
        if c['kind']!='explanation':
            continue
        name='production-'+c['id'];names.append(name)
        options={k:c[k] for k in ('cues','title','imagePaths','initialVisible') if k in c}
        options['duration']=c['frames']/FPS
        outputs[MC/(name+'.tsx')]=("// Generated only from the current measured48k edit-plan.\n"
            "import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\n"
            "export default makeScene2D(function*(view) {\n  yield* lesson(view, "
            +json.dumps(c['visual'])+", "+json.dumps(options,ensure_ascii=False)+");\n});\n")
    outputs[MC/'production-project.ts']=("// Independent explanation cuts, in the measured edit order.\n"
        "import {makeProject} from '@motion-canvas/core';\n"
        +'\n'.join(f"import s{i} from './{n}?scene';" for i,n in enumerate(names))
        +"\nexport default makeProject({scenes: ["+','.join('s'+str(i) for i in range(len(names)))+"]});\n")
    return outputs


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--capacity-audit',action='store_true',help='Verify local source hashes and native eligibility only; no fake timing')
    parser.add_argument('--dry-run',action='store_true',help='Read/allocate measured inputs if present, otherwise report only capacity; write no files')
    parser.add_argument('--allocations',type=Path,help='Optional reviewed exact-frame allocation override within D22')
    parser.add_argument('--audio-review',type=Path,default=HERE/'source-audio-review.json')
    parser.add_argument('--timing',type=Path,default=NARRATION/'source-scene-timings.json')
    parser.add_argument('--output',type=Path,default=HERE/'edit-plan.json')
    args=parser.parse_args(argv)
    import audio_pipeline as audio
    audio.require_authorized('measured semantic edit preparation')
    plan,ko,files=validate_inputs(BANKS)
    report=capacity_report(plan,files)
    if args.capacity_audit or not args.timing.is_file():
        print(json_text(report))
        if not(args.capacity_audit or args.dry_run):
            raise ValueError('Actual reviewed source-scene-timings.json absent. No edit/wrappers were written.')
        return
    timing_path=path(args.timing)
    if not timing_path.is_relative_to(NARRATION):
        raise ValueError('Only current D22 measured narration timing is accepted')
    timing,scenes,rows,body=measured_clock(plan,ko,files,timing_path)
    target=round(body*.6)
    if target/FPS>report['globalUniqueNativeSeconds']+1/FPS:
        raise ValueError(f'Actual60% target {target/FPS:.3f}s exceeds unique semantic source capacity {report["globalUniqueNativeSeconds"]:.3f}s; no render allowed')
    if args.allocations:
        override=path(args.allocations)
        if not same_logical_tree(override, PROJECT):
            raise ValueError('Reviewed allocation override must stay in D22')
        allocations=read(override)['allocations'];allocation_receipt={'method':'reviewed exact-frame override','input':artifact(override)}
    else:
        allocations,allocation_receipt=automatic_allocation(plan,rows,target)
    validate_allocation(allocations,plan,rows,target)
    decisions=audio_decisions(plan,path(args.audio_review))
    inputs={'scripts':files,'semanticBanks':artifact(BANKS),'captionUnits':artifact(HERE/'caption-units.json'),
            'sourceTiming':artifact(timing_path),'splitReview':artifact(NARRATION/'scene-split-review.json'),
            'builder':artifact(__file__),'visuals':artifact(MC/'visuals.tsx'),
            'sourceAudioReview':artifact(args.audio_review) if args.audio_review.is_file() else None}
    edit=compose(plan,scenes,rows,body,allocations,allocation_receipt,decisions,inputs)
    summary={'status':'measured-allocation-preview' if args.dry_run else edit['status'],
             'bodySeconds':body/FPS,'actualSeconds':target/FPS,'explanationSeconds':(body-target)/FPS,
             'ratioErrorFrames':edit['ratioErrorFrames'],'cuts':len(edit['cuts']),'mcFrames':edit['mcFrames'],
             'audioReviewPending':edit['audioSourceReviewPending'], 'allocation':allocation_receipt,
             'sourcesReused':False,'mediaJobsStarted':False,'movingPixelAndAudioReview':'pending'}
    if args.dry_run:
        print(json_text(summary));return
    output=path(args.output)
    if output.parent!=HERE:
        raise ValueError('Edit-plan output must remain in current scoped revision folder')
    # Check the immutable plan destination BEFORE generating any cut wrappers.
    content=json_text(edit)
    if output.exists() and output.read_text('utf-8-sig')!=content:
        raise ValueError(f'Existing incompatible plan preserved: {output}; choose a versioned --output')
    for destination,source in wrappers(edit).items():
        checked_write(destination,source,generated=True)
    checked_write(output,content)
    checked_write(HERE/(output.stem+'-allocation-review.json'),json_text(summary))
    print(json_text(summary))


if __name__=='__main__':
    try:
        main()
    except (ValueError,FileNotFoundError,KeyError) as error:
        print('D22 edit preparation stopped: '+str(error),file=sys.stderr)
        sys.exit(2)
