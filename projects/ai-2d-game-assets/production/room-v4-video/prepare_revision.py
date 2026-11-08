"""Isolate the latest public-game revision; preserve all earlier deliveries."""
from pathlib import Path
import json,shutil,hashlib,subprocess
H=Path(__file__).resolve().parent;P=H.parents[1];ROOT=P.parents[1]
L=P/'production/local/room-v4-video';OUT=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video')
L.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
for d in ['video/visual','video/final','video/review','site-snapshot','captures']: (OUT/d).mkdir(parents=True,exist_ok=True)
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,v):f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
auth=read(H/'authorization.json');assert auth['fullLocalProductionAuthorized'] and auth['renderAuthorized']
site=ROOT/'sites/yamyam-cartographers-room';commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=site,text=True).strip();assert commit==auth['siteCommit'],commit
snap=OUT/'site-snapshot';sources=[]
for f in (site/'dist').rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(site/'dist');digest=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();sources.append({'file':rel.as_posix(),'sha256':digest,'bytes':f.stat().st_size})
 if f.suffix.lower() in ['.mp3','.wav','.ogg']:continue
 target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
save(H/'source-snapshot.json',{'siteVersion':6,'siteCommit':commit,'publicUrl':auth['publicGameUrl'],'snapshot':str(snap),'files':sources,'audioNotCopied':'Canvas video is narration-only; original CC0 radio files remain in the public site.'})
base=read(P/'production/room-v3/revision-plan.json');tm=read(P/'production/local/room-v3/timeline.json')
replaced=['01','02','15','16','30','R01','R16','18','R18','R20','R21','26','R27','28','R28','V33','V34','V35','R30']
memo={
 'id':'W36','title':'기록을 남기는 작은 작업실',
 'ko':'기록하기는 움직임을 감상하는 데서 끝나지 않습니다. 캐릭터가 작업대에 앉으면 화면 안의 메모를 열고, 오늘의 생각을 오백 자까지 적을 수 있습니다. 저장 버튼을 누르면 지금 사용하는 브라우저에 남고, 다시 열어 이어서 볼 수 있습니다. 다른 기기로 자동 전송되지는 않습니다. 같은 화면의 라디오에서 음악을 고르고, 메모를 남기면 이 방이 잠깐 머물 수 있는 작은 작업실이 됩니다.',
 'en':'Writing is more than watching an animation. Once the character sits at the desk, you can open the on-screen memo and write up to five hundred characters. Press Save to keep it in the browser you are using, then reopen it later. It does not automatically transfer to other devices. Choose music on the radio in the same view and leave a note, and the room becomes a small workshop where you can spend a little time.',
 'audio':'new approved-reference Qwen3 TTS, CPU four threads',
 'visual':'Actual v6 browser screenshot sequence: writing active, memo opened, typed, explicit local save, reopened. Same-game Canvas capture remains distinct from browser UI.',
}
scenes=[]
for row in base['scenes']:
 row=dict(row);row['audio']='preserve exact room-v3 PCM and timing'
 row['visualRevision']='latest v6 replacement' if row['id'] in replaced else 'unchanged useful source/tool explanation'
 scenes.append(row)
 if row['id']=='V35':scenes.append(memo)
save(H/'revision-plan.json',{'revision':'room-v4-video','authorization':'authorization.json','baseline':'production/room-v3/checkpoint.json','siteSnapshot':'source-snapshot.json','original51PcmPreserved':True,'preservePreviousMasters':True,'replaceVisualIds':replaced,'scenes':scenes,'changes':{'background':'Separate v6 background and actual 166×66 desk; show intermediate background as explicitly earlier processing, never final v6 output.','desk':'Foreground center; writer213,220; correct feet/desk/hands draw order.','flame':'Lantern166,43 retained; desk candle250,162 instead of250,127.','sit':'Existing right stool pose now381,174; callouts derived from current coordinates.','radio':'Actual in-stage v6 DOM UI screenshot replacing obsolete below-game controls.','memo':'One adjacent new paragraph demonstrates500-character explicit browser-local save.'},'screenKindPolicy':'Runtime capture executes snapshotted actual game.js; browser controls shown only from genuine browser screenshots. No fabricated application UI.','newTtsCount':1,'humanReview':'pending','youtubeAuthorizedNow':False,'obsoletePrivateDraft':'t7Li-IzqJyk','boundaryLinks':[{'from':'V35','to':'W36','reason':'Existing closing introduces radio and writing; new paragraph turns writing into an actual saved note.'},{'from':'W36','to':'R30','reason':'A usable workshop leads to the existing direct-play invitation.'}]})
(H/'full-narration.ko.txt').write_text('\n\n'.join(s['ko'] for s in scenes),encoding='utf-8')
save(H/'added.ko.json',{'scenes':[{'id':memo['id'],'title':memo['title'],'lines':[memo['ko']]}]})
save(H/'narration-additions.ko-en.json',{'scenes':[memo]})
manifest=read(P/'production/room-v3/tts-manifest.json');manifest['paths']['script']=(H/'added.ko.json').relative_to(ROOT).as_posix();manifest['tts'].update(outputDir=(L/'voice').relative_to(ROOT).as_posix(),filenameStem='room-v4-video-memo');save(H/'tts-manifest.json',manifest)
save(L/'timeline.json',tm)
for name in ['captions.json','captions.ko.ass','captions.ko.srt','captions.en.srt']:shutil.copy2(P/'production/local/room-v3'/name,L/name)
save(H/'checkpoint.json',{'stage':'latest-game-replacement-prepared','revision':'room-v4-video','siteVersion':6,'siteCommit':commit,'baselineSha256':auth['baselineMasterSha256'],'replaceVisualIds':replaced,'existingAudioPreserved':51,'newAudio':['W36'],'next':'Generate memo narration on CPU; preflight v6 visuals before bounded render','youtubeAuthorizedNow':False,'oldUploadPreserved':'t7Li-IzqJyk'})
print('Prepared',len(scenes),'scenes;',len(replaced),'existing visual replacements; site',commit)
