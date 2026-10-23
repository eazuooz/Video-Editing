"""Record current v2 evidence and preserve the v1 upload receipt."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/gameplay-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return Path(p).relative_to(R).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat();cp=read(P/'production/checkpoint.json')
assert cp['revision']=='flow-map-gameplay-v2'
pub=P/'publishing';old=pub/'youtube-upload.flow-map-v1.json'
if not old.exists():shutil.copyfile(pub/'youtube-upload.json',old)
plan=read(P/'planning/production-plan.json');m=read(P/'project.json')
source=dict(id='scuprikov-l4d2-swamp',kind='independent-gameplay',url='https://www.youtube.com/watch?v=e60Q8pwGMsI',title='Left 4 Dead 2 (Swamp Fever) Part 4',creator='SCuprikov',channelUrl='https://www.youtube.com/channel/UCZvUfr-iZdqTPsrrl9qu7kQ',originalUpload='2021-06-04',file=rel(L/'l4d2-swamp-526-556.mp4'),sha256=sha(L/'l4d2-swamp-526-556.mp4'),recordingSize=[1920,1080],decodedFps='29863/500',playbackSpeed=1,originalWindow=[526,556],license='Creative Commons Attribution license (reuse allowed)',licenseEvidence=rel(L/'e60Q8pwGMsI.info.json'),licenseDefinition='https://support.google.com/youtube/answer/2797468?hl=en',licenseDefinitionLink='https://creativecommons.org/licenses/by/4.0/',publisherPolicy='https://store.steampowered.com/video_policy?l=english',adaptation='Short excerpts, fit16:9, educational narration, editorial water contour, original audio ducked; no endorsement implied.',classification='Valve FPS survival-horror; real water appearance only, not measured shader buffers',gameTechniqueEvidence='Valve2010 Water Flow in Portal2: Flowing Normal Maps in Left4Dead2. Our shader is an independently authored simplified illustration, not the commercial implementation.',audio='Original gameplay retained at gain0.035, speech and BGM unchanged; includes game character calls and gun/ambience sounds. No source lesson narration.',viewingEvidence=[rel(L/'water-contact-526.jpg'),rel(L/'start-detail.jpg'),rel(L/'end-detail.jpg')],reason='Verified flow-map use and licensed native FHD recording; earlier720pPortal2 candidate rejected. Water undulations visible while passing trees; no direction magnitude inferred from camera movement.')
sources=read(P/'sources/sources.json');sources['sources']=[s for s in sources['sources'] if s.get('id')!=source['id']]+[source];save(P/'sources/sources.json',sources)
cuts=[dict(id='game-shader-result',startFrame=1526,endFrame=1812,sourceIn=529.5,sourceOut=534.2666666667,speech=['p4-1','p4-2'],beforeActionResult='Water surface visible between trees; camera traverses swamp and rippled reflections persist. Shown as real-game appearance; shader input/value change is demonstrated in preceding/following Unity.',annotation={'meaning':'Editorial water-surface focus, not velocity','times':[27.4,30.1],'sourceRegion':[300,600,500,240],'occlusion':'Hide before27.4 while enemy crosses and at source cut.'}),dict(id='game-closing-return',startFrame=2836,endFrame=3067,sourceIn=542.5,sourceOut=546.35,speech=['p6-3','p6-4'],beforeActionResult='Return to the real swamp after updating our map; visible water ripples and reflections provide the closing application, no claim this shot proves an internal simulation toggle.',annotation={'meaning':'Same editorial focus on visible water','times':[47.7,49.1],'occlusion':'Hide before camera reaches tree/boat; no persistent box on occluded target.'})]
for cut in cuts:cut.update(sourceId=source['id'],kind='independent-gameplay',renderer='FFmpeg composite over preserved Unity/MotionCanvas master',aspect='1040x58516:9at20,630; no stretch/crop',captionClearance='Caption anchor remains510,1380; gameplay ends1215; game-name at572',hold=0,speechVisualOverlap=True)
if 'baselineV1' not in plan:plan['baselineV1']=dict(revision=plan['revision'],finalMaster=plan['finalMaster'],receipt=rel(old),driveFileId='1Eo3ulWHvj0S758NvRUPXj69jhp4pb25t',gitCommit='fa9ce4072a82a28907aae38bbb681fdfa8fd8c8d')
plan.update(revision='flow-map-gameplay-v2',status='rendering-gameplay-revision',latestUserSteering=cp['revisionAuthorization'],gameplayCuts=cuts)
plan['screenShare'].update(independentGameplay=517/3067,explanation=2550/3067,independentGameplaySeconds=517/60,explanationSeconds=2550/60,reason='User requested actual game evidence. Two meaningful inserts preserve all RG decoding, two-phase blending and moving-obstacle limit; no quota padding.')
plan['continuity']+=' V2: worked RG values → real L4D2 water appearance during shader explanation → original same-river arrows around rock → stretching/blending/limit → real-game closing confirmation. Voice and24cue timings unchanged.'
plan['recommendedChoices'].append(dict(choice='Keep all approved narration PCM and insert517frames of real gameplay at existing sentence boundaries',reason='Visual-only request; retain learning order, worked examples, current natural voice and runtime. No extra TTS/GPU job. Preserve source aspect and speed; mask focus annotation at occlusions.'))
save(P/'planning/production-plan.json',plan)
m.update(currentRevision='flow-map-gameplay-v2',status='rendering-gameplay-revision',updatedAt=now);m['baselineV1']=plan['baselineV1'];save(P/'project.json',m)
cp.update(stage='rendering-gameplay-revision',updatedAt=now,nextAction='Inspect corrected1080x1920/60master and changed audio, deliver4files and upload replacement privately. Old9cRdnf8wKEI remains until replacement verified and action-time deletion confirmation.');save(P/'production/checkpoint.json',cp)
ko='- 실제 게임 녹화: SCuprikov, Left 4 Dead 2 (Swamp Fever) Part 4: https://www.youtube.com/watch?v=e60Q8pwGMsI\n  Creative Commons Attribution (YouTube CC BY): https://support.google.com/youtube/answer/2797468\n  구간 발췌·크기 조정·설명 및 표식 합성·음량 조절. 원작자와의 제휴·보증을 의미하지 않습니다.\n- Valve 영상 이용 정책: https://store.steampowered.com/video_policy\n'
en='- Gameplay recording: SCuprikov, Left 4 Dead 2 (Swamp Fever) Part 4: https://www.youtube.com/watch?v=e60Q8pwGMsI\n  Creative Commons Attribution (YouTube CC BY): https://support.google.com/youtube/answer/2797468\n  Excerpted, resized, annotated and mixed under narration; no endorsement implied.\n- Valve Video Policy: https://store.steampowered.com/video_policy\n'
for lang,credit in [('ko',ko),('en',en)]:
 for name in [f'description.{lang}.txt',f'upload-description.{lang}.txt']:
  path=pub/name;text=path.read_text(encoding='utf-8')
  if 'SCuprikov' not in text:
   text=text.replace('- Alex Vlachos',credit+'- Alex Vlachos')
   if lang=='ko':text=text.replace('방법을 직접 만든 Unity 장면으로 보여드립니다.','방법을 《레프트 4 데드 2》 실제 게임 장면과 직접 만든 Unity 시연으로 보여드립니다.')
   else:text=text.replace('Our Unity shader demonstration reveals the direction texture behind the effect: a flow map.','Real Left 4 Dead 2 footage and our Unity shader demonstration reveal the direction texture behind the effect: a flow map.')
   path.write_text(text,encoding='utf-8')
print('V2 plan, source/rights evidence and description credits recorded; v1 preserved.')
