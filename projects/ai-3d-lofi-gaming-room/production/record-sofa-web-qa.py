"""Record observed v10 browser results separately from historical broader UI checks."""
from pathlib import Path
import json,hashlib,datetime,subprocess
H=Path(__file__).resolve().parent;P=H.parent;R=P.parents[1];L=H/'local/living-room-v10'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
previous=json.loads((H/'web-browser-qa.json').read_text('utf-8-sig'))
history=H/'web-browser-qa-v6-baseline.json'
if not history.exists():save(history,previous)
build=json.loads((L/'web-build.json').read_text('utf-8'));assert build['result']=='Succeeded' and build['errors']==0
checks={}
for name in ('unity-native-clean.mp4','walk-source/unity-native-clean.mp4'):
 f=L/name
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',str(f)],creationflags=subprocess.CREATE_NO_WINDOW))
 v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 checks[name]={'sha256':sha(f),'probe':probe,'fullDecodePassed':True}
screens=[]
for name in ('contact-book.png','contact-reverse.png','contact-cat.png','web-sofa.jpg','web-cat.jpg','web-room.jpg','web-memo-restored.jpg','web-timer-restored.jpg'):
 f=L/name;assert f.exists();screens.append({'path':f.relative_to(R).as_posix(),'sha256':sha(f)})
qa={'scope':'living-room-v10 actual Tripo calico and supported sofa reading','observedOnKst':now,'url':'http://127.0.0.1:9324/','browser':'Codex in-app desktop browser','buildSucceeded':True,'buildErrors':0,'compiledBytes':build['bytes'],'checks':{'loadingToReady':True,'userGestureAudioStartAndPlayingState':True,'actualTripoCatVisible':True,'supportedSofaReadingVisible':True,'readToStandToComputerObserved':True,'computerBackToSofaObserved':True,'memoKoreanLineBreaksSavedAndReopenedAfterReload':True,'testMemoRestoredToOriginalValue':True,'timerStartPauseResetUi':True,'rainButtonToggledOnce':True,'tenMusicOptionsAndAutomaticNextTrackObserved':True},'nativeMedia':checks,'screens':screens,'baselineBroaderUiQa':'production/web-browser-qa-v6-baseline.json','limits':['Sampled native motion and browser operation; no claim of whole real-time film listening or physical-mobile performance.','The observed FPS values are incidental samples while other user apps run, not a benchmark.','Current cat has subtle breathing; no generated cat rig or tail/ear animation is claimed.'],'publicDeployment':False,'youtubeUploaded':False,'humanFinalReview':False}
save(H/'web-browser-qa.json',qa);save(H/'sofa-v10-qa.json',qa)
j=json.loads((P/'project.json').read_text('utf-8'));j['paths']['webGameBuild']='projects/ai-3d-lofi-gaming-room/production/local/living-room-v10/webgl';j['review']['currentRevision']='v10 game ready; tutorial v4 voice and final film in progress; previous full-video-v2 preserved';save(P/'project.json',j)
j=json.loads((H/'checkpoint.json').read_text('utf-8'));j.update(status='sofa-cat-v10-game-ready-tutorial-v4-in-progress',currentGame='production/local/living-room-v10/webgl',currentGameQa='production/sofa-v10-qa.json',gameUrl='http://127.0.0.1:9324/',currentTutorial='script/tutorial-v4.json',updatedAtKst=now);j['pending']=['Changed local Qwen voice paragraphs, same-scene tutorial v4 final render and QA','Update the same 3D wiki with final-master frames','User full final review before YouTube or public game hosting'];save(H/'checkpoint.json',j)
print('Recorded v10 actual web QA and full native decode')
