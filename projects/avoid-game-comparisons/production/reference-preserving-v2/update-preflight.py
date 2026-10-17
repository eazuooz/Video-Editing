from pathlib import Path
import json,hashlib,datetime,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';L=P/'production/local/reference-preserving-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
plan=read(P/'planning/chapter-plan.json');v=plan['currentRevision'];sel=v['sourceSelection']
def media(name):
 f=L/(name+'.mp4');q=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));s=next(s for s in q['streams'] if s['codec_type']=='video')
 assert s['width']>=1920 and s['height']>=1080
 return dict(path=f.relative_to(R).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),width=s['width'],height=s['height'],fps=s['r_frame_rate'],seconds=float(q['format']['duration']),bytes=f.stat().st_size)
od=sel[0]
for name in ['odyssey-switch2-360-440','odyssey-switch2-705-820']:
 m=media(name);od['files']=[x for x in od['files'] if x['path']!=m['path']]+[m]
official='https://www.nintendo.com/kr/switch/aaaca/sp/action/index.html'
od['mechanicEvidence']=list(dict.fromkeys(od['mechanicEvidence']+[official]))
od['screenReview']['additionalObserved']='Frog capture changes the controlled character and enables high jumps onto raised platforms. T. rex capture changes the controlled character and breaks stone blocks. Inspected4-second contact sequence across new windows and browser playback samples. Full final-cut motion review remains separate.'
nes=dict(id='nes-gameplay-project',game='Super Mario Bros.',version='NES original gameplay in genuine1080p capture; retain original game aspect ratio',classification='independent-gameplay',sourceUrl='https://www.youtube.com/watch?v=HGmyQS09VGQ',uploader='Gameplay Project',status='selected',format='299+140',files=[media('nes-gameplay-project')],rights=dict(recorderPermission='Actual YouTube metadata: Creative Commons Attribution license (reuse allowed). Public description offers original NES1080p60 recordings for reviews/discussions with attribution.',metadataEvidence=(L/'HGmyQS09VGQ.info.json').relative_to(R).as_posix(),requiredCredit='Gameplay Project / source URL / CC BY; Nintendo game rights separate.',gamePolicy='https://www.nintendo.co.jp/networkservice_guideline/en/index.html'),observed='1-1 side-view jumps, pipes, enemies and flag;1-2 underground platforms;1-3 elevated platforms and gaps.245.087s capture decoded1920x1080 at60000/1001. No source upscale or stretched game pixels.',fullFinalMotionReviewComplete=False)
v['sourceSelection']=[s for s in sel if s.get('id')!='nes-gameplay-project']+[nes]
v['timingAndAudio'].update(defaultBodyRatio={'actual':60,'explanation':40},exceptionGranted=False,userRatioConfirmation={'at':now,'answer':'기본 실제 영상 60%·설명 40% 유지'},paddingAllowed=False)
v['scriptDraft']['status']='full-bilingual-text-and-11-boundaries-read; technical speech review pending'
v['scriptDraft']['hashes']={lang:hashlib.sha256((P/f'script/reference-preserving-v2/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']}
for s in v['scenePlan']:
 s['savedScene']=f"motion-canvas/src/projects/avoid-game-comparisons/revision-v2/scene{s['id']}.tsx"
 s['captionSpace']='960,970;48px;max2lines; representative1080p/375px sample inspected'
 s['transitionReview']='Adjacent closing/opening read together; content handoff retained without resetting music/title on every internal scene.'
v['sceneDesign']['sceneFilesSaved']=True
v['sceneDesign']['mobileCheck']='Representative direction/condition diagram with actual draft wording in fixed48px boxed caption inspected at1920x1080 and375x211. Arrow/text overlap found and repaired before full production; all final scenes remain pending.'
v['sceneDesign']['preflightEvidence']=[(L/f).relative_to(R).as_posix() for f in ['preflight-caption.png','preflight-mobile.png']]
v['terminology']=[dict(ko=k,en=e,meaning=m,firstScene=s,source=official if s!='03' else None,pronunciation=k) for k,e,m,s in [('피치','Pitch','프로젝트의 핵심 매력과 방향을 짧게 전달','03'),('캡처','Capture','특정 대상을 조종해 그 능력을 사용','07'),('티라노사우루스','T. rex','캡처할 수 있는 공룡; 돌을 부수는 행동','07'),('멍멍이','Chain Chomp','쇠사슬에 묶인 캡처 대상','08'),('파워문','Power Moon','달 모양 수집 목표물','08')]]
v['preflightComplete']=False
v['remainingBeforeFullTts']=['Complete representative footage callout/caption clearance sample; narration draft and source checks complete.']
v['nextAction']='Finish actual-footage sample, then single approved-voice batch; measure frame timeline with exact60:40 and complete cut review.'
plan['updatedAt']=now;save(P/'planning/chapter-plan.json',plan)
ledger=read(P/'production/script-source-review.json');rv=ledger['currentRevision'];rv.update(status='independent-bilingual-script-and-editable-scene-design-complete',newScriptApproved=True,scriptHashes=v['scriptDraft']['hashes'],continuousRead={'all68ParagraphPairs':True,'all11AdjacentJoins':True,'sourceCreatorFraming':False,'personalExperienceRelabeled':False,'officialTermsChecked':official,'unrelatedGamesAdded':False},sourceRights={'nesResolved':True,'odysseyRecordingReuseEvidencePreserved':True},representativeDiagram={'reviewed1080p':True,'reviewed375px':True,'overlapRepaired':True,'allScenePixelsApproved':False},humanWholeListening=False)
save(P/'production/script-source-review.json',ledger)
cp=read(P/'production/latest-checkpoint.json');cp.update(stage='current-rule-script-and-scene-design-complete',updatedAt=now)
cp['currentRevision'].update(status='script-and-scene-design-complete',fhd60ClipsAcquired=5,nesRecordingRightsResolved=True,scriptWritten=True,editableScenesSaved=12,ttsStarted=False,fullRenderStarted=False,ratio={'actual':60,'explanation':40,'userConfirmed':True},baselinePreserved=True)
save(P/'production/latest-checkpoint.json',cp)
wl=read(R/'shared/publishing/video-worklist.json');row=next(r for r in wl['rows'] if r['slug']=='avoid-game-comparisons')
row.update(reviewStatus='독립FHD자료5개·사용권 확인 / KOEN대본68문단·연결 검토 / 설명 샘플1080p·모바일 확인',executionStatus='선택됨 · 12개 편집 가능 씬 저장 / 음성·최종 편집 준비',notes='실제60·설명40 사용자 재확인. NES·오디세이 독립1080p 녹화 확보. 새 음성·최종 렌더·전체 검수는 진행 전. 기존 비공개본 보존; 이후 편 자동 시작 없음.')
row['currentRevision'].update(scriptComplete=True,editableScenes=12,ratioUserConfirmed=True)
wl['updatedAt']=now;save(R/'shared/publishing/video-worklist.json',wl)
control=read(R/'shared/publishing/video-production-control.json');control['selectedVideoAuthorization']['latestUserMessage']='다음 게임디자인영상 진행해줘~';control['selectedVideoAuthorization']['bodyRatioConfirmation']={'at':now,'actual':60,'explanation':40,'userAnswer':'기본 실제 영상 60%·설명 40% 유지'};save(R/'shared/publishing/video-production-control.json',control)
print('Updated selected script/source/scene progress; no final QA or platform claims.')
