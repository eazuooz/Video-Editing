"""Remove three repeated teaching chapters, preserving the later complete versions.

This is an editorial deletion authorized on 2026-10-03. Old v2 files remain
immutable. Audio is rebuilt from unchanged reviewed scene WAVs, never a mixed MP4.
"""
from pathlib import Path
import json, copy, hashlib, re, shutil
import numpy as np
import soundfile as sf

W = Path(__file__).resolve().parent
R = W.parents[3]
B = W.parent / 'original-restored-v2'
REV = 'deduplicated-v3'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def rel(p): return p.relative_to(R).as_posix()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

old = read(B/'plan.json')
removed_ids = {str(i).zfill(2) for i in range(31, 38)}
removed = [s for s in old['scenes'] if s['id'] in removed_ids]
cut_start = removed[0]['startFrame']
cut_end = removed[-1]['startFrame'] + removed[-1]['frames']
delta = cut_end - cut_start
assert (cut_start, cut_end, delta) == (41693, 50320, 8627)
plan = copy.deepcopy(old)
plan['revision'] = REV
plan['scenes'] = [s for s in plan['scenes'] if s['id'] not in removed_ids]
plan['cuts'] = [c for c in plan['cuts'] if c['scene'] not in removed_ids]
plan['paragraphs'] = [p for p in plan['paragraphs'] if p['scene'] not in removed_ids]
for s in plan['scenes']:
    s['baselineStartFrame'] = s['startFrame']
    if s['startFrame'] >= cut_end: s['startFrame'] -= delta
    s['start'] = s['startFrame']/60
for c in plan['cuts']:
    c['baselineCutId'] = c['id']
    c['baselineStartFrame'] = c['timelineStartFrame']
    if c['timelineStartFrame'] >= cut_end:
        c['timelineStartFrame'] -= delta
        c['timelineEndFrame'] -= delta
    c['timelineStart'] = c['timelineStartFrame']/60
    c['timelineEnd'] = c['timelineEndFrame']/60
for p in plan['paragraphs']:
    if p['start'] >= cut_end/60-.001:
        p['start'] -= delta/60
        p['end'] -= delta/60

# Deleting the earlier versions removes slightly more explanation than footage.
# Reuse two of their now-unseen teaching diagrams during the same later claim.
# Narration length does not change; no artificial waiting or new speech is added.
body = sum(s['frames'] for s in plan['scenes'])
excess = sum(c['frames'] for c in plan['cuts'] if c['classification']=='actual') - round(body*.6)
assert excess == 549
target = next(c for c in plan['cuts'] if c['id']=='091')
replacements = []
position = target['timelineStartFrame']
for cid, original_id, frames in [('091a','076',329),('091b','079',220)]:
    original = next(c for c in old['cuts'] if c['id']==original_id)
    c = copy.deepcopy(original)
    c.update(id=cid, scene='38', chapter=17, frames=frames, seconds=frames/60,
             timelineStartFrame=position, timelineEndFrame=position+frames,
             timelineStart=position/60, timelineEnd=(position+frames)/60,
             baselineCutId=original_id, baselineSource=original['source'],
             source=rel(W/'cuts'/f'{cid}.mp4'), sourceTrimStartFrame=0,
             headerChapterOverride=17,
             claim='1·2학년은 정답을 닫고 백지에서 구조와 구현을 직접 결정하는 훈련이 필요하다.',
             viewerFocus='AI를 잠시 끄고 구조를 정하는 단계와 따라 쓰기/직접 구현의 차이를 본다.',
             visualReview='pending-current-caption-and-join-review')
    replacements.append(c)
    position += frames
c = copy.deepcopy(target)
c.update(id='091c', frames=target['frames']-excess,
         seconds=(target['frames']-excess)/60,
         timelineStartFrame=position, timelineStart=position/60,
         baselineSource=target['source'], sourceTrimStartFrame=excess,
         source=rel(W/'cuts'/'091c.mp4'),
         sourceIn=target['sourceIn']+excess/60, localIn=target['localIn']+excess/60,
         visualReview='pending-current-caption-and-join-review')
replacements.append(c)
idx = plan['cuts'].index(target)
plan['cuts'][idx:idx+1] = replacements
for s in plan['scenes']:
    cc = [c for c in plan['cuts'] if c['scene']==s['id']]
    assert sum(c['frames'] for c in cc)==s['frames']
    s['actualFrames'] = sum(c['frames'] for c in cc if c['classification']=='actual')
    s['explanationFrames'] = s['frames']-s['actualFrames']
    s['motionCanvasFrames'] = sum(c['frames'] for c in cc if c['key']=='motion-canvas')
for a,b in zip(plan['cuts'],plan['cuts'][1:]): assert a['timelineEndFrame']==b['timelineStartFrame']
actual = sum(c['frames'] for c in plan['cuts'] if c['classification']=='actual')
plan.update(bodyFrames=body,bodySeconds=body/60,bodyEnd=(body+120)/60,
            seconds=(body+720)/60,totalFrames=body+720,actualFrames=actual,
            explanationFrames=body-actual,gameplaySeconds=actual/60,
            explanationSeconds=(body-actual)/60,gameplayShare=actual/body,
            ratioErrorFrames=abs(actual-.6*body),
            explanationReelFrames=sum(c['frames'] for c in plan['cuts'] if c['key']=='motion-canvas'),
            manimExplanationFrames=sum(c['frames'] for c in plan['cuts'] if c['key']=='manim'))
assert plan['totalFrames']==68846 and plan['ratioErrorFrames']<=1
write(W/'plan.json', plan)
write(W/'footage-cuts.json', {k:plan[k] for k in ['revision','fps','bodyFrames','actualFrames','explanationFrames','cuts']})

for lang in ['ko','en','tts.ko']:
    script = read(B/f'narration.{lang}.json')
    script['scenes'] = [s for s in script['scenes'] if s['id'] not in removed_ids]
    script.update(revision=REV, sourcePolicy='User requested removal of three repeated sections. Earlier chapters14–16 removed; complete chapters17–19 retained. All retained scene wording/order unchanged.')
    write(W/f'narration.{lang}.json',script)
script = read(W/'narration.ko.json')
(W/'narration.review.txt').write_text('\n\n'.join(f'[{s["id"]}] {s["title"]}\n'+'\n\n'.join(s['lines']) for s in script['scenes'])+'\n',encoding='utf-8')
alignment = read(B/'caption-alignment.json')
alignment['entries'] = [e for e in alignment['entries'] if e['scene'] not in removed_ids]
for e in alignment['entries']:
    if e['start'] >= cut_end/60-.001:
        e['start'] -= delta/60; e['end'] -= delta/60
alignment.update(cues=len(alignment['entries']),kind='Unchanged reviewed v2 word alignment; deleted scenes31–37 and shifted later cues by8627/60seconds.')
write(W/'caption-alignment.json', alignment)
def stamp(t):
    n=round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang in ['ko','en']:
    (W/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(e["start"])} --> {stamp(e["end"])}\n{e[lang]}' for i,e in enumerate(alignment['entries']))+'\n',encoding='utf-8')
assert re.sub(r'\s','',''.join(l for s in script['scenes'] for l in s['lines'])) == re.sub(r'\s','',''.join(e['ko'] for e in alignment['entries']))

audio = R/'shared/output/narration/blank-project-coding'/REV
audio.mkdir(parents=True,exist_ok=True)
pieces=[]
for s in plan['scenes']:
    assert digest(R/s['voice'])==s['audioSha256']
    pcm,rate=sf.read(R/s['voice'],dtype='int16')
    assert rate==24000 and pcm.ndim==1
    pieces.append(np.pad(pcm,(0,s['frames']*400-len(pcm))))
body_wav=audio/f'blank-project-coding-{REV}-body.wav'
sf.write(body_wav,np.concatenate(pieces),24000,subtype='PCM_16')

manifest=read(B/'final.manifest.json')
manifest.update(status=REV+'-render-pending',scriptRevision=3)
for key,value in list(manifest['paths'].items()):
    if isinstance(value,str) and rel(B) in value:
        manifest['paths'][key]=value.replace(rel(B),rel(W))
manifest['paths'].update(narration=rel(body_wav),audioMix=rel(audio/'final-mix.m4a'),
    editorAudioMix=rel(audio/'final-mix.wav'),sourceMap=rel(W/'duplicate-removal-audit.json'),
    videoClean=f'shared/output/motion-canvas/blank-project-coding-{REV}.mp4',
    videoBurnedCaptions=f'shared/output/motion-canvas/blank-project-coding-{REV}-subtitled.mp4',
    motionCanvasProject=f'motion-canvas/src/projects/blank-project-coding/{REV}/full/project.ts')
# Original explanation source remains editable in v2; the v3 full editor selects
# its retained cuts plus the documented two header-adjusted diagrams.
manifest['paths']['explanationProject']='motion-canvas/src/projects/blank-project-coding/restored-v2/project.ts'
manifest['tts']['outputDir']=rel(audio)
manifest['tts']['filenameStem']='blank-project-coding-'+REV
manifest['tts']['reuseSceneWavsFrom']=rel(B/'plan.json')
manifest['video'].update(durationSeconds=plan['seconds'],targetDurationSeconds=plan['seconds'],
    durationEstimateRangeSeconds=[plan['seconds'],plan['seconds']],durationEstimateStatus='measured49-retained-scenes')
manifest['editing'].update(actualGameplaySeconds=actual/60,actualExplanationSeconds=(body-actual)/60,
    actualGameplayShare=actual/body,actualCommercialGameplaySeconds=sum(c['seconds'] for c in plan['cuts'] if c['key']=='tetris'),
    actualDevelopmentFootageSeconds=sum(c['seconds'] for c in plan['cuts'] if c['classification']=='actual' and c['key']!='tetris'),
    actualManimExplanationSeconds=plan['manimExplanationFrames']/60,scenePlan=rel(W/'plan.json'),
    plannedBodySeconds=body/60,plannedActualSeconds=actual/60,plannedExplanationSeconds=(body-actual)/60,
    preserveExplanationTime='Retained sections unchanged; explicitly requested duplicates removed.',timingStatus='deduplicated-timeline-ready')
manifest['editing']['exampleExpansion']={'method':'Remove duplicate chapters14–16 per latest request, retain later full chapters17–19. No retained speech rewritten or resynthesized.',
    'preserveRetainedWordingAndOrder':True,'baseline':rel(B/'final.manifest.json'),'latestUserEvidence':'이영상 3부분 중복이 있어 중복제거해줘'}
manifest['editing']['exampleInterleaving'].update(planningPath=rel(W/'concept-connections.json'),storyboard=rel(W/'plan.json'),reviewStatus='pending-current-cut-review')
manifest['delivery']['gitEvidence']=rel(W/'git-delivery.json')
manifest['audio'].update(mixStatus='pending-deduplicated-remix')
manifest['audio'].pop('finalMeasurement',None)
manifest['approvals'].update(script='Latest explicit duplicate-removal request',fullNarration='49 unchanged current-hash reviewed scene WAVs; full human listening pending',
    translation='Retained bilingual wording unchanged; cues jointly retimed',render='pending',platform='pending-new-private-upload')
manifest['publishing']={'status':'pending-new-private-revision-upload','defaultPrivacyStatus':'private',
    'publicPublicationOrSchedulingAuthorized':False,'receipt':'projects/blank-project-coding/publishing/youtube-upload-deduplicated-v3.json',
    'coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True,'defaults':'shared/publishing/youtube-defaults.json',
    'pinnedCommentStatus':'pending-video-publication','previousPrivateVideoId':'bbpKRhlxeCs',
    'previousReceiptPreserved':'projects/blank-project-coding/publishing/youtube-upload-original-restored-v2.json'}
manifest['production']={'currentStage':'deduplicated-timeline-ready','ttsGenerated':True,'rendered':False,'collected':False,'uploaded':False}
manifest['finalRender'].update(revision=REV,seconds=plan['seconds'],technicalQa=rel(W/'qa.json'),
    mixAlignmentReview=rel(W/'mix-alignment-review.json'),directVisualReview=rel(W/'direct-visual-review.json'),
    originalPreservationAudit=rel(W/'duplicate-removal-audit.json'))
write(W/'final.manifest.json',manifest)

groups=[]
for chapter,retained in [(14,17),(15,18),(16,19)]:
    rs=[s for s in removed if s['chapter']==chapter]
    ks=[s for s in plan['scenes'] if s['chapter']==retained]
    groups.append({'removedChapter':chapter,'removedSceneIds':[s['id'] for s in rs],
      'baselineStart':rs[0]['start'],'baselineEnd':rs[-1]['start']+rs[-1]['seconds'],
      'retainedChapter':retained,'retainedSceneIds':[s['id'] for s in ks],
      'newStart':ks[0]['start'],'title':ks[0]['title'],
      'reason':'Same teaching argument and example immediately repeated; retain the later complete user-supplied version.'})
audit={'revision':REV,'userEvidence':'이영상 3부분 중복이 있어 중복제거해줘','baseline':rel(B/'final.manifest.json'),
    'baselineSha256':digest(B/'final.manifest.json'),'removedGroups':groups,
    'removedFrames':delta,'removedSeconds':delta/60,'oldSeconds':old['seconds'],'newSeconds':plan['seconds'],
    'retainedScenes':49,'allRetainedWordsAndOrderUnchanged':True,'retainedWavHashesVerified':True,
    'captionWordsExactlyMatchRetainedScript':True,'truncatedSourceReconstructionRemoved':True,
    'visualAdjustment':{'scene':'38','actualFramesReplaced':excess,'explanationSources':['076','079'],
        'reason':'Reuse now-unseen diagrams illustrating the same claim; preserve exact body60:40 without changing narration duration.',
        'header':'Original17 chapter label retained'},
    'sourceWavs':[{'scene':s['id'],'path':s['voice'],'sha256':s['audioSha256']} for s in plan['scenes']],
    'oldUploadAndLocalFilesPreserved':True}
write(W/'duplicate-removal-audit.json',audit)
for name in ['sources.json','source-candidates.txt','pronunciation-map.json','thumbnail.png','.gitignore']:
    shutil.copy2(B/name,W/name)
connections=read(B/'concept-connections.json')
connections['chapters']=[c for c in connections['chapters'] if c['chapter'] not in [14,15,16]]
write(W/'concept-connections.json',connections)
for name in ['mix-audio.cjs','caption-video.cjs','verify-video.py','make-caption-strips.py']:
    shutil.copy2(B/name,W/name)
editor=(B/'build-editor.cjs').read_text(encoding='utf-8').replace('restored-v2/full','deduplicated-v3/full').replace('original-restored-v2/final-mix.wav','deduplicated-v3/final-mix.wav').replace('original-restored-v2-full','deduplicated-v3-full')
editor=editor.replace("'./src/projects/blank-project-coding/restored-v2/project.ts',",'').replace('56 independent','49 independent')
(W/'build-editor.cjs').write_text(editor,encoding='utf-8')
write(W/'checkpoint.json',{'stage':'prepared','completed':['duplicate-content-review','three-group-removal','retained-word-and-wav-audit','retimed-bilingual-captions','exact60:40-plan'],
    'remaining':['render-and-remix','current-visual-and-audio-QA','collect','private-upload','git-delivery']})
print(json.dumps({'removedSeconds':delta/60,'seconds':plan['seconds'],'scenes':49,'cues':alignment['cues'],'ratioErrorFrames':plan['ratioErrorFrames']},ensure_ascii=False))
