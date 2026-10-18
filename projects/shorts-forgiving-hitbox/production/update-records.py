"""Record only this selected Short's observed production/delivery evidence."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat();mode=sys.argv[1]
plan=read(P/'planning/production-plan.json');ledger=read(P/'production/review-ledger.json');checkpoint=read(P/'production/checkpoint.json');manifest=read(P/'project.json')
if mode=='production':
 timing=read(L/'visual-timing.json');trace=read(L/'capture-full-v1/trace.json')['frames']
 plan['renderer']['savedScenes']=[rel(p) for p in sorted((R/'unity/VideoEditing/Assets/VideoScenes'/P.name/'Scenes').glob('*.unity'))]
 plan['renderer'].update(antiAliasing=4,sourceCapture=dict(width=1080,height=1920,fps=60,frames=1800),shader='CharacterSurface.shader: authored textured Lambert illumination')
 purposes={'01-hook':'Attack brushes armor; health100; exact opening question','02-reveal':'Green Hurtbox then red Hitbox; trace real projected bounds','03-wide':'Widen only receiving collider: overlap, health100→70 and actual Hit_A reaction','04-narrow':'Restore narrow receiving collider: same attack, health100','05-resolution':'Slow replay of opening configuration resolves why it survived'}
 plan['sceneBeats']=[dict(**s,purpose=purposes[s['id']],renderer='Unity + Motion Canvas',boundaryLink='Same knight, camera, projectile and coordinate system; prior question/state retained',visualEvidence=dict(source='capture-full-v1/unity-master.mp4',anchors='capture-full-v1/trace.json',meaning='actual collider query and health, not computer vision detection',captionClearance='Fixed captions below feet/platform; labels left/right of knight')) for s in timing['shots']]
 plan['visualPreflight']=dict(status='passed corrected composed native sample',preview='production/local/motion-preview-v2-captioned.png',observed='Readable two-line canonical labels, real collider outlines, textured knight, fixed caption box clear of demonstration',fullMovingReview='pending')
 voice=next(L.glob('asr-voice-425592c58dca.json'));mix=next(L.glob('asr-mix-3b313d1591e6.json'))
 plan['narrationRevision'].update(fullSourceAsr=rel(voice),fullFinalMixAsr=rel(mix),asrReview='Complete recognized text read; only orthographic 예요/에요 and spacing differ. No semantic omissions or repeated words. Human listening remains pending.')
 physics={s['id']:dict(healthMinimum=min(x['health'] for x in trace if x['shot']==s['id']),hitFrames=sum(bool(x['hitApplied']) for x in trace if x['shot']==s['id'])) for s in timing['shots']}
 ledger['entries'].append(dict(kind='actual-production-and-preflight',at=now,unityMasterSha256=sha(L/'capture-full-v1/unity-master.mp4'),traceSha256=sha(L/'capture-full-v1/trace.json'),physics=physics,narrationAssembly=read(L/'pcm-edit.json'),sourceAsr=dict(path=rel(voice),inputSha256=read(voice)['sha256'],status='full-text-reviewed'),mixAsr=dict(path=rel(mix),inputSha256=read(mix)['sha256'],status='full-text-reviewed'),audioBuild=read(L/'audio-build.json'),phraseLevelReview=read(L/'phrase-level-review.json'),humanListening='pending'))
 ledger['pending']=['current final pair visual/decode/audio QA','Drive upload and playback','human final review and listening']
 checkpoint.update(stage='full-composite-rendering',updatedAt=now,next='Encode fixed captions, full integrity and moving visual QA, collect and upload exact master for Drive review.')
 manifest['status']='production-rendering'
elif mode=='delivery':
 delivery=read(P/'production/delivery-output.json');pair=read(L/'pair-build.json');q=L/'qa'/pair['captionedSha256'][:16]
 technical=read(q/'technical.json');assert technical['status']=='technical-pass-pixel-review-pending'
 visual=read(P/'production/visual-review.json');assert visual['status']=='pass'
 ledger['entries'].append(dict(kind='current-final-internal-review',at=now,pair=pair,technical=technical,visual=visual,audioContinuity=dict(path=rel(q/'audio-continuity.json'),sha256=sha(q/'audio-continuity.json'),sustainedAttenuationFlags=read(q/'audio-continuity.json')['sustainedAttenuationFlags']),delivery=delivery,wholeHumanListening='pending'))
 manifest.update(status='awaiting-drive-final-review',publishReady=False,finalRender=dict(knownIssues=[],openItems=['사용자 최종 시청·청취 검수 대기']))
 checkpoint.update(stage='local-complete-drive-upload-pending',updatedAt=now,masterSha256=pair['captionedSha256'],next='Upload the exact captioned master to Google Drive and verify access, revision and playback.')
 ledger['pending']=['Drive upload and playback','human final review and listening'];plan['visualPreflight']['fullMovingReview']='production/visual-review.json'
elif mode=='drive':
 receipt=read(P/'publishing/drive-review.json');assert receipt['playback']['status']=='verified'
 checkpoint.update(stage='awaiting-human-drive-final-review',updatedAt=now,driveId=receipt['fileId'],driveUrl=receipt['url'],next='Wait for user review of this exact version; no YouTube upload or next Short before authorization.')
 ledger['entries'].append(dict(kind='drive-final-review-delivery',at=now,receipt='publishing/drive-review.json',fileId=receipt['fileId'],revisionId=receipt['revisionId'],sha256=receipt['localSha256'],playback='verified',userReview='pending'))
 ledger['pending']=['human final review and listening'];manifest['status']='awaiting-human-drive-final-review';manifest['publishing']['driveReview']='projects/'+P.name+'/publishing/drive-review.json'
 workfile=R/'shared/publishing/shorts-worklist.json';work=read(workfile);row=next(x for x in work['rows'] if x['slug']==P.name);row.update(productionStatus='30초·1080×1920 60fps·4파일·Drive 완료',reviewStatus='사용자 최종 시청·청취 검수 대기',driveId=receipt['fileId'],driveRevisionId=receipt['revisionId'],captionedSha256=receipt['localSha256']);work['updatedAt']=now;save(workfile,work)
else:raise ValueError(mode)
save(P/'planning/production-plan.json',plan);save(P/'production/review-ledger.json',ledger);save(P/'production/checkpoint.json',checkpoint);save(P/'project.json',manifest)
print(json.dumps(dict(stage=checkpoint['stage']),ensure_ascii=False))
