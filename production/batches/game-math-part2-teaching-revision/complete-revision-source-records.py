"""Repair only this task's source/rebuild pointers; preserve media and approval."""
from pathlib import Path
import json,copy,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
base=read(B/'baselines/game-math-lines-bounds/sources/gameplay-cuts.json')
sources=copy.deepcopy(base['sources'])
portal=read(B/'baselines/game-math-camera-projection/sources/gameplay-cuts.json')['sources']['yFRbGppLaUI'];sources['yFRbGppLaUI']=copy.deepcopy(portal)
steam=ROOT/'shared/output/game-math-part2-full-series/sources/portal2-steam-5787.mp4';info=steam.with_suffix('.info.json')
sources['portal2-steam-5787']={'id':'portal2-steam-5787','game':'Portal 2','uploader':'Valve / official Steam store movie','url':'https://store.steampowered.com/app/620/Portal_2/','movieId':5787,'historicalPreview':True,'file':rel(steam),'sha256':sha(steam),'metadataProof':rel(info),'metadataSha256':sha(info),'nativeHighestSourceResolution':[940,528],'recordingAndGamePolicy':'https://store.steampowered.com/video_policy/','policyObservation':'Official Valve video policy permits video sharing/YouTube monetization under its terms; no game audio used; not an independent clearance of every game-IP element. Preserve human rights review as pending.','licenseLabel':'official Valve video policy, not a named CC license','sourceAudioUsed':False,'inspection':'F01 full105.672-second normal-rate playback ended plus dense2-second intervals and source75.5–87 fine moving-object observations before dependent TTS; selected48–88.5 input/button/cube travel/pickup/placement/receiver result; rejected0–17 explanation and89–105 branding','proofDirectory':'shared/output/game-math-part2-teaching-revision/lines-funnel-candidates','selectedBeforeNarration':True,'worldOrEngineMeasurementVerified':False,'humanRightsReviewComplete':False}
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json');ids={s['sourceId'] for s in lesson['scenes'] if s['kind']=='actual'}
 record={'sources':{i:sources[i] for i in ids},'newFootageSelection':rel(B/'lines-game-insertions.json'),'editableAnnotationRegistry':rel(B/'lines-annotation-tracks.json'),'priorUseComparisonsRecorded':True,'bodyActualShare':.4,'bodyExplanationShare':.6,'sourceAudioUsed':False,'backgroundMusic':False,'originalFootagePreserved':True,'currentMovingPixelApproval':False,'humanRightsReviewComplete':False}
 write(P/'production/footage-sources.json',record)
 timeline=P/'production/timeline.json'
 cuts={'status':'measured timeline pending','scenes':[]}
 if timeline.exists():cuts={'status':'measured native-rate cuts; final pixel review independent','scenes':[{k:s[k] for k in ['id','frames','seconds','start','cut','baselineClip','preservedOriginal'] if k in s} for s in read(timeline)['scenes'] if s['classification']=='actual']}
 write(P/'production/footage-cuts.json',cuts)
 m['paths']['sources']=rel(P/'production/footage-sources.json');m['paths']['footageCuts']=rel(P/'production/footage-cuts.json');lesson['part']=lesson['episode'];lesson['totalParts']=2
 write(P/'project.json',m);write(P/'production/lesson.json',lesson)
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
 P=ROOT/'projects'/slug;m=read(P/'project.json');before=copy.deepcopy(m['finalRender']);timeline=read(P/'production/timeline.json')
 cuts={'status':'completed actual native-rate cuts, referenced from current reviewed timeline','baselineSourceRecord':rel(B/'baselines/game-math-rotation-interpolation/sources/gameplay-cuts.json'),'newSourceRecord':rel(B/'interpolation-game-insertions.json'),'newSkateSourceRecord':rel(B/'interpolation-skate-source.json'),'scenes':[{k:s[k] for k in ['id','frames','seconds','start','cut','baselineClip','preservedOriginal'] if k in s} for s in timeline['scenes'] if s['classification']=='actual'],'currentPixelReview':rel(P/'production/current-pixel-review.json'),'humanRightsReviewComplete':False}
 write(P/'production/footage-cuts.json',cuts)
 m['paths'].update(sources=rel(B/'interpolation-game-insertions.json'),footageCuts=rel(P/'production/footage-cuts.json'),publishingKo=rel(P/'publishing/upload-description.ko.txt'),publishingEn=rel(P/'publishing/upload-description.en.txt'),audioReport=rel(P/'audio/mix-measurements.json'),productionBuilder=rel(B/'build-interpolation-episodes.py'))
 assert all((ROOT/path).exists() for path in m['paths'].values()),'Completed manifest still contains unavailable paths'
 assert before==m['finalRender'];write(P/'project.json',m)
print('Source/rebuild records updated; rendered media, original scripts and platform settings unchanged.')
