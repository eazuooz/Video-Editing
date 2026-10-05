"""Preserve all current13 PCM samples in a native, word-aligned candidate.

This is an inspection plan. Source/caption/diagram pixels, new joins and final
mix remain unapproved. No source loop, speed change, synthesis or final render.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, math
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v2'
assert not WORK.exists(), 'Preserve prior measured candidates.'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()
measurement = read(BASE / 'measured-paragraphs-expanded13.json')
index = read(BASE / 'narration-expanded13-index.json')
wall = read(BASE / 'wall-word-boundary-v2.json')
assert wall['exitCode'] == 0 and wall.get('directlyReviewed')
bank_path = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/source-research/source-action-bank-v2.json'
bank = read(bank_path)
by_id = {c['id']: c for c in bank['candidates']}
groups = {}

def piece(i, a=None, z=None):
    c = copy.deepcopy(by_id[i])
    fps = float(c['nativeFrameRate'].split('/')[0]) / float(c['nativeFrameRate'].split('/')[1])
    start = c['localFrames']['startInclusive'] if a is None else round(a*fps)
    end = c['localFrames']['endExclusive'] if z is None else round(z*fps)
    if i == 7:
        assert c['localFrames']['startInclusive'] == 12600
        c['localFrames']['endExclusive'] = 12770
        c['wallEndpointEvidence'] = 'projects/making-game-sequels/production/wall-word-boundary-v2.json'
        if z is None:
            end = 12770
    assert c['localFrames']['startInclusive'] <= start < end <= c['localFrames']['endExclusive']
    c.update(bankCutId=i, sourceStartFrame=start, sourceEndFrameExclusive=end,
             nativeFps=fps, frames=round((end-start)/fps*60),
             nativeSeconds=(end-start)/fps, speed=1, sourceAudioStreams=0,
             classification='actual-existing-game', finalApproved=False,
             captionPixelsApproved=False, mediaCompiled=False)
    return c

def group(sid, ps, cuts=None, white=None):
    assert (sid, ps[0]) not in groups
    groups[(sid, ps[0])] = {'paragraphs': ps, 'cuts': cuts or [], 'whiteFrames': white}

#02: the literal wall clause ends5.58s. Native wall images now remain through
#5.666667s; reserved53 follows only under the general choose/place sentence.
group('02', [1], [piece(7), piece(53)])
group('02', [2], [piece(8), piece(9,571,573), piece(10,579,585)])
group('02', [3], [piece(9,573,577), piece(10,585,587), piece(11,587.5,590.5)])
group('02', [4], [piece(11,590.5,595.5), piece(12), piece(13)])
#04: green→blue around6.5s; staff→sword→Knight around2.7/7.3s
#inside p2. The personal design question becomes a readable white comparison.
group('04', [1], [piece(1), piece(2)])
group('04', [2], [piece(3,35,37.7), piece(5,69,73.6), piece(6,82,85+17/30)])
group('04', [3], [piece(3,37.7,41), piece(4), piece(5,73.6,75), piece(6,85+17/30,88.2)])
s4 = next(s for s in measurement['scenes'] if s['id']=='04')
group('04', [4], white=math.ceil(s4['paragraphs'][3]['pcmSeconds']*60))
#06: spike→tilted preview→invalid location under the specific first clause.
#The third paragraph shows wall, barricade, floor orientation, then the actual
#invalid wall preview. Source25 includes Spring/Floor Scorcher states; the
#selected floor excerpt is1081.5–1085, not an inferred item from the target HUD.
group('06', [1], [piece(14),piece(22,1061,1062+1/3),piece(15,622,626.1),piece(26)])
group('06', [2], [piece(17),piece(18),piece(20,842.5,845.5)])
group('06', [3], [piece(23,1064.5,1067.2),piece(24,1070,1072+1/30),
                  piece(25,1081.5,1085),piece(23,1067.2,1069)])
group('06', [4], [piece(16),piece(19),piece(20,845.5,847.5),
                  piece(21),
                  piece(24,1072+1/30,1076),piece(25,1077,1081.5)])
#13: shorter unique active excerpts replace the former long observation tails.
#Close combat→far route follows the p2 nouns; body turn is60 at1174–1176.5,
#between59 approach context and61/62 distant aim. All are separate OMD2 times.
group('13', [1], [piece(49,990,999.9),piece(50,1006,1014)])
group('13', [2], [piece(51,1030,1034),piece(55),piece(51,1034,1038+2/3),
                  piece(52,1046,1049+8/30),piece(56),piece(57),piece(58),piece(59,1168,1170.4)])
group('13', [3], [piece(59,1170.4,1172.5),piece(60),piece(61),piece(62)])
group('13', [4], [piece(54),piece(52,1049+8/30,1052+4/15)])
#08: assign original12's unique overhead footage to the overhead nouns.
#Keep p3/p4 PCM continuous; resource change→placement→sell prompt→placement.
#The selling prompt is not described as an actual sale.
group('08', [1], [piece(27),piece(28,438,443)])
group('08', [2], [piece(30),piece(47,316,319)])
group('08', [3,4], [piece(28,443,447),piece(29,454.5,457.4),piece(31),
                    piece(29,457.4,461.5),piece(47,319,323),piece(48,329+1/30,333)])
#10: Wave1 and Wave2 begin under their actual words. Surplus unique combat is
#reassigned only to12's general conclusion, never a claimed card effect.
group('10', [1], [piece(32)])
group('10', [2], [piece(34),piece(35,65,67.6)])
group('10', [3,4], [piece(37),piece(38,160,164),piece(33),piece(35,67.6,72)])
#12: wall→floor→object orientation→overhead preview under the first paragraph.
#Later generic writing/checking clauses use separate active combat intervals.
group('12', [1], [piece(41,273,275.6),piece(42,277,279+1/6),piece(44),piece(48,325.5,329+1/30)])
group('12', [2], [piece(41,275.6,277),piece(42,279+1/6,281),piece(43),piece(45),piece(46)])
group('12', [3], [piece(36),piece(38,164,165+1/3)])
group('12', [4], [piece(38,165+1/3,169),piece(39),piece(40)])

scenes, cursor, joins = [], 120, []
for s in measurement['scenes']:
    sid = s['id']
    assert sha(ROOT/s['audio']) == s['audioSha256']
    pcm_data,sr = sf.read(ROOT/s['audio'],dtype='float32')
    assert sr == 24000 and len(pcm_data) == s['samples']
    segments, placements, output, covered = [], [], 0, []
    def place(a,z):
        global output
        placements.append({'kind':'preserved-current-PCM','fromSample':a,'toSample':z,
                           'outputFromSample':output,'outputToSample':output+z-a})
        output += z-a
    def pad(n, reason):
        global output
        assert n >= 0, f'{sid}: missing{(-n)/24000:.6f}s'
        if n:
            placements.append({'kind':'inserted-silence','samples':n,'outputFromSample':output,
                               'outputToSample':output+n,'reason':reason})
            output += n
    if s['classification'] == 'explanation':
        segments = [{'id':sid+'-preserved-white','classification':'explanation',
                     'diagramId':sid,'frames':s['minimumSpeechFrames'],
                     'originalPcmAndExplanationPreserved':True,'finalApproved':False,'captionPixelsApproved':False}]
        place(0,s['samples'])
        pad(s['minimumSpeechFrames']*400-output,'At most one output frame of PCM endpoint quantization; original white explanation unchanged.')
        covered = [1,2,3,4]
    else:
        for p in range(1,5):
            if p in covered:
                continue
            g = groups[(sid,p)]
            before = output
            if g['whiteFrames']:
                cuts = [{'id':f'{sid}-p{p}-white-decision-comparison','classification':'explanation',
                         'diagramId':f'{sid}-{p}','frames':g['whiteFrames'],'paragraph':p,
                         'finalApproved':False,'captionPixelsApproved':False}]
            else:
                cuts = copy.deepcopy(g['cuts'])
                for c in cuts:
                    c.update(id=f'{sid}-p{p}-action-{c["bankCutId"]}-{c["sourceStartFrame"]}-{c["sourceEndFrameExclusive"]}',paragraph=p)
            segments.extend(cuts)
            a=s['paragraphs'][g['paragraphs'][0]-1]['pcmFromSample']
            z=s['paragraphs'][g['paragraphs'][-1]-1]['pcmToSample']
            place(a,z)
            target=sum(c['frames'] for c in cuts)*400
            pad(before+target-output,'Observe the related active native action at normal speed after the complete paragraph; no idle, loop or speed change. Inspection candidate, not final approval.')
            covered.extend(g['paragraphs'])
            if z < s['samples']:
                q=pcm_data[max(0,z-192):min(len(pcm_data),z+192)]
                joins.append({'scene':sid,'afterParagraph':g['paragraphs'][-1],'sample':z,
                              'rms16ms':float(np.sqrt(np.mean(q*q))),'peak16ms':float(np.max(np.abs(q))),
                              'newJoinAsrApproved':False,'allPcmPreserved':True})
    kept=[p for p in placements if p['kind']=='preserved-current-PCM']
    assert kept[0]['fromSample']==0 and kept[-1]['toSample']==s['samples']
    assert all(a['toSample']==b['fromSample'] for a,b in zip(kept,kept[1:]))
    assert sum(p['toSample']-p['fromSample'] for p in kept)==s['samples']
    local=0
    for c in segments:
        c.update(localFromFrame=local,startFrame=cursor+local,seconds=c['frames']/60)
        local+=c['frames'];c['endFrameExclusive']=cursor+local
    assert output==local*400
    scenes.append({'id':sid,'title':s['title'],'audio':s['audio'],'audioSha256':s['audioSha256'],
                   'sampleRate':24000,'samples':s['samples'],'currentPcmSeconds':s['speechSeconds'],
                   'startFrame':cursor,'endFrameExclusive':cursor+local,'frames':local,
                   'segments':segments,'pcmPlacement':placements,'speechEvidence':s['paragraphs'],
                   'asrEvidence':s['asrEvidence'],'allPcmSamplesPreserved':True})
    cursor+=local
actual=[c for s in scenes for c in s['segments'] if c['classification']=='actual-existing-game']
actual_frames=sum(c['frames'] for c in actual)
white_frames=sum(c['frames'] for s in scenes for c in s['segments'] if c['classification']=='explanation')
for asset in bank['assets']:
    spans=sorted((c['sourceStartFrame'],c['sourceEndFrameExclusive'],c['id']) for c in actual if c['assetId']==asset['assetId'])
    assert all(a[1]<=z[0] for a,z in zip(spans,spans[1:])), f'Duplicate native source time: {asset["assetId"]}'
assert actual_frames == 20918 and white_frames == 13945
assert abs(actual_frames-.6*(actual_frames+white_frames)) <= 1
assert len(scenes)==13 and sum(len(s['speechEvidence']) for s in scenes)==52
WORK.mkdir()
plan={'schemaVersion':1,'slug':'making-game-sequels','createdAt':now,
      'status':'current13-word-aligned-v2-no-subsecond-fragments-all-final-pixels-and-joins-pending',
      'fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,
      'actualFrames':actual_frames,'explanationFrames':white_frames,'bodyFrames':actual_frames+white_frames,
      'finalFrames':cursor+600,'finalSeconds':(cursor+600)/60,
      'ratioRoundingErrorFrames':actual_frames-.6*(actual_frames+white_frames),
      'originalSixMinimumFrames':13350,'allCurrentPcmSeconds':sum(s['speechSeconds'] for s in measurement['scenes']),
      'scenes':scenes,'assets':bank['assets'],'quietJoins':joins,
      'sourcePlanningBank':bank_path.relative_to(ROOT).as_posix(),
      'sourceIntervalsOmitted': [{'bankId':49,'seconds':[999.9,1006]}, {'bankId':50,'seconds':[1014,1021]},
                                {'bankId':51,'seconds':[1038+2/3,1046]}, {'bankId':52,'seconds':[1052+4/15,1053]},
                                {'bankId':15,'seconds':[626.1,627]}, {'bankId':22,'seconds':[1062+1/3,1063]},
                                {'bankId':24,'seconds':[1069,1070]}],
      'omissionReason':'Shorten redundant active observation tails without shortening a script, current PCM or any original white explanation. These unused intervals remain available for later necessary matching.',
      'sourceAudioStreams':0,'selfCreatedGames':0,'loops':0,'slowdown':0,
      'finalTimingApproved':False,'bodyRatioApproved':False,'allCaptionPixelsReviewed':False,
      'allSourceSegmentPixelsReviewed':False,'diagramPixelsReviewed':False,'finalMixBuilt':False,
      'newJoinAsrApproved':False,'rendered':False,'qaApproved':False,'collected':False,'privateUploaded':False,
      'humanWholeListening':'pending','humanPronunciation':'pending','newGitImages':0,
      'inputs': {str(p.relative_to(ROOT)):sha(p) for p in [BASE/'measured-paragraphs-expanded13.json',
                   BASE/'narration-expanded13-index.json',BASE/'current-asr-word-index.json',bank_path]}}
(WORK/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sceneCount':len(scenes),'paragraphs':52,'nativeCuts':len(actual),
                  'actualFrames':actual_frames,'whiteFrames':white_frames,'finalFrames':cursor+600,
                  'finalSeconds':plan['finalSeconds'],'ratioErrorFrames':plan['ratioRoundingErrorFrames'],
                  'allCurrentPcmPreserved':True,'finalApproved':False}))
