"""Package and verify the current A03 picture, both subtitle streams and one encoded mix."""
from assembly import H,P,R,L,read,save,sha,ff,rel
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import re,subprocess,shutil,json,sys,difflib
import numpy as np
B=R/'projects/animation-assigning/production/local/grid-v1/edit';QA=L/'qa';QA.mkdir(exist_ok=True)
def probe(f):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))
def packet(f):return subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def pair():
 p=read(L/'timeline.json');cuts=read(H/'edit-plan-final.json');n=p['totalFrames'];parts=[B/'branding.mp4',L/'body.mp4',B/'membership.mp4']
 for f,frames in zip(parts,[120,p['bodyFrames'],600]):
  v=probe(f)['streams'][0];assert (v['width'],v['height'],Fraction(v['avg_frame_rate']),int(v['nb_frames']))==(1920,1080,60,frames)
 assert cuts['totalFrames']==n and sha(L/'audio.m4a')==read(L/'mix.json')['aacSha256']
 graph=';'.join(f'[{i}:v]setsar=1,format=yuv420p,settb=1/60,setpts=N[v{i}]' for i in range(3))+';[v0][v1][v2]concat=n=3:v=1:a=0,settb=1/60,setpts=N,split=2[c][b];[b]ass='+rel(L/'captions.ko.ass')+'[baked]'
 args=['-loglevel','warning','-filter_complex_threads','2']
 for f in parts:args+=['-threads','3','-i',f]
 args+=['-i',L/'audio.m4a','-filter_complex',graph]
 for tag,file in [('c','clean.mp4'),('baked','captioned.mp4')]:
  args+=['-map','['+tag+']','-map','3:a','-frames:v',n,'-t',n/60,'-r','60','-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',L/file]
 ff(*args,log='pair')
def listen():
 from audio_pipeline import full_asr
 ff('-i',L/'audio.m4a','-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',L/'encoded.wav',log='readback-pcm')
 result=full_asr(L/'encoded.wav',L/'encoded-asr.json',final=True)
 assert result['completeAudioSubmitted']
 expected=' '.join(s['lines'][0] for s in read(H/'final.spoken-ko.json')['scenes'])
 def normalized(text):
  text=re.sub(r'\s+','',text.lower())
  for a,b in [('마흔여덟','48'),('서른여섯','36'),('예순','60'),('영점팔','08'),('영점육','06'),('영점이','02'),('cancel','캔슬')]:text=text.replace(a,b)
  return re.sub(r'[^가-힣a-z0-9]','',text)
 ref=normalized(expected);spoken=normalized(result['text'])
 match=difflib.SequenceMatcher(None,ref,spoken,autojunk=False)
 report={'aacSha256':sha(L/'audio.m4a'),'decodedPcmSha256':sha(L/'encoded.wav'),'coverage':sum(b.size for b in match.get_matching_blocks())/len(ref),
         'differences':[(ref[i:j],spoken[k:l]) for z,i,j,k,l in match.get_opcodes() if z!='equal'],'humanListening':False}
 save(L/'encoded-text-review.json',report)
def verify():
 p=read(L/'timeline.json');n=p['totalFrames'];cues=read(L/'captions.json')['cues'];masters={}
 for name in ['captioned','clean']:
  f=L/(name+'.mp4');info=probe(f);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],Fraction(v['avg_frame_rate']),int(v['nb_frames']))==(1920,1080,60,n)
  assert a['codec_name']=='aac' and a['channels']==2 and a['sample_rate']=='48000' and abs(float(a['duration'])-n/60)<.08
  ff('-v','error','-xerror','-threads','5','-i',f,'-map','0:v','-map','0:a','-f','null','-',log='decode-'+name)
  pts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(f)]).splitlines()
  step=Fraction(1,60)/Fraction(v['time_base']);assert sorted(map(int,pts))==[int(i*step) for i in range(n)]
  masters[name]={'sha256':sha(f),'frames':n,'audioPacketHash':packet(f),'fullDecode':True,'cfr60':True}
 assert masters['clean']['audioPacketHash']==masters['captioned']['audioPacketHash']==packet(L/'audio.m4a')
 ff('-i',L/'captioned.mp4','-vn','-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-',log='encoded-levels')
 txt=(L/'encoded-levels.log').read_text(encoding='utf-8',errors='replace');levels=json.loads(txt[txt.rfind('{'):txt.rfind('}')+1]);assert float(levels['input_tp'])<=-1.5
 chosen=[round((c['start']+c['end'])*30) for c in cues]
 exp=[f'eq(n\\,{t})' for t in chosen]
 while len(exp)>1:exp=['('+exp[i]+'+'+exp[i+1]+')' if i+1<len(exp) else exp[i] for i in range(0,len(exp),2)]
 ff('-v','error','-i',L/'captioned.mp4','-vf','select='+exp[0]+',scale=960:540','-fps_mode','vfr','-q:v','3',QA/'cue-%03d.jpg',log='mobile-select')
 frames=sorted(QA.glob('cue-*.jpg'));assert len(frames)==len(cues)
 for i,f in enumerate(frames):
  im=Image.open(f);inside=np.asarray(im)[448:529,70:900,:3]
  assert (inside.min(axis=2)>220).sum()>750,(i,f)
 for start in range(0,len(frames),18):
  sheet=Image.new('RGB',(375*3,232*6),'#19211d');d=ImageDraw.Draw(sheet)
  for j,f in enumerate(frames[start:start+18]):
   x=j%3*375;y=j//3*232;sheet.paste(Image.open(f).resize((375,211),Image.Resampling.LANCZOS),(x,y));d.text((x+4,y+212),f'{j+start+1}  {chosen[j+start]/60:.1f}s',fill='white')
  sheet.save(QA/f'mobile-{start//18+1}.jpg',quality=88)
 def mono(f):
  return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ac','1','-ar','24000','-f','f32le','-']),dtype='<f4')
 stem=mono(L/'narration-stem.wav');final=mono(L/'audio.m4a');voiceGain=[]
 for r in p['paragraphs']:
  values=[]
  for i in range(round(r['start']*24000),round(r['end']*24000)-9600,4800):
   u=stem[i:i+9600];y=final[i:i+9600];power=np.sum(u*u,dtype=np.float64)
   if power>2 and len(y)==len(u):values.append(float(20*np.log10(max(.00001,abs(np.sum(u*y,dtype=np.float64)/power)))))
  voiceGain.append({'paragraph':r['id'],'medianVoiceGainDb':round(float(np.median(values)),2),'minimumVoiceGainDb':round(min(values),2)})
 save(L/'verification.json',{'masters':masters,'audioLevels':levels,'sourceStemToEncodedVoice':voiceGain,'allCaptionSamples':len(cues),'wholeHumanListening':False})
def collect():
 plan=read(L/'timeline.json');cuts=read(H/'edit-plan-final.json');v=read(L/'verification.json');a=read(L/'encoded-asr.json')
 assert a['completeAudioSubmitted'] and v['masters']['captioned']['sha256']==sha(L/'captioned.mp4')
 project=read(P/'project.json');project.update(status='local-review-delivered',publishReady=False,platformStatus='local-only')
 project['paths']={'script':rel(H/'final.spoken-ko.json'),'scriptKo':rel(H/'final.ko.json'),'scriptEn':rel(H/'final.en.json'),'videoClean':rel(L/'clean.mp4'),'videoBurnedCaptions':rel(L/'captioned.mp4'),'captionsKo':rel(L/'captions.ko.srt'),'captionsEn':rel(L/'captions.en.srt'),'audioMix':rel(L/'final-mix.wav'),'narration':rel(L/'voice/narration.wav'),'timeline':rel(H/'edit-plan-final.json')}
 project['delivery']={'status':'four-outputs-complete','localStorageRoot':rel(L/'delivery'),'captionedMasterSha256':v['masters']['captioned']['sha256']};project['voice']={'provider':'Local Qwen3-TTS 1.7B Base, transcript-assisted own voice','manifest':rel(H/'tts-manifest.json'),'generated':True}
 project['editing']={'targetGameplayShare':.6,'measuredBodyGameplayShare':cuts['gameFrames']/cuts['bodyFrames'],'resolution':[1920,1080],'fps':60,'sixEditableUnityScenes':[f'Assets/VideoScenes/animation-breaking-down-attack-animations/Scenes/Attack-{i}.unity' for i in range(1,7)]}
 save(P/'project.json',project);subprocess.run(['node','scripts/collect-video-output.cjs',P.name],cwd=R,check=True)
 dest=L/'delivery/output'/P.name;shutil.copyfile(H/'sources.txt',dest/'sources.txt')
 ix=dest/'index.html';page=ix.read_text('utf-8');anchors=' · '.join(f'<a href="{P.name}.captioned.mp4#t={s["f0"]/60:.2f}">{s["title"]}</a>' for s in plan['scenes'])
 ix.write_text(page.replace('</h1>','</h1><p>'+anchors+'</p>',1)+'<p><a href="sources.txt">영상과 에셋 출처</a></p>',encoding='utf-8')
 report=read(P/'production/delivery-output.json');assert all(sha(dest/f['name'])==f['sha256'] for f in report['files'])
 native={}
 for traceFile in sorted((L/'native').glob('ch*.json')):
  tr=read(traceFile);samples=tr['samples']
  source=R/'unity/VideoEditing'/tr['scene']
  native[traceFile.stem]={'scene':rel(source),'sceneSHA256':sha(source),'filmSHA256':sha(Path(tr['video'])),'traceSHA256':sha(traceFile),'recordedFrames':len(samples),'contact':next((s['contactFrame'] for s in samples if s['hit']),None),'release':next((s['simulationFrame'] for s in samples if s['transitionAccepted']),None)}
 assert native['ch3']['contact']==14 and native['ch5-early']['release']==36 and native['ch5-wait']['release']==48 and native['ch5-noinput']['release'] is None
 save(H/'native-evidence.json',native)
 teaching=read(P/'planning/production-plan.json')
 teaching['status']='delivered-for-local-review';teaching['updatedOnKst']='2026-11-05'
 teaching['nativeImplementationContract'].update(status='implemented-and-captured',createdSceneFiles=project['editing']['sixEditableUnityScenes'],runtimeEvidence=rel(H/'native-evidence.json'))
 teaching['productionSelectedSources']=read(H/'selection.json')['sources'];teaching['currentEdit']=rel(H/'edit-plan-final.json');teaching['currentVoice']=project['voice'];teaching['blockers']=[];teaching['nextAction']='Review the local captioned A03 master.'
 save(P/'planning/production-plan.json',teaching)
 ledger={'episode':'A03','slug':P.name,'title':project['title'],'revision':'grid-v1','status':'local-delivery-user-review-pending','checkedAt':datetime.now(timezone.utc).isoformat(),'directory':rel(dest),'captioned':rel(dest/(P.name+'.captioned.mp4')),'captionedMasterSha256':v['masters']['captioned']['sha256'],'durationSeconds':plan['totalFrames']/60,'frames':plan['totalFrames'],'format':'1920x1080 60fps','bilingualCues':v['allCaptionSamples'],'gameplayShare':project['editing']['measuredBodyGameplayShare'],'sourceRecords':rel(H/'sources.txt'),'scenePlan':rel(H/'edit-plan-final.json'),'files':report['files'],'unity':project['editing']['sixEditableUnityScenes'],'encodedAudioReadback':rel(L/'encoded-asr.json'),'technicalQA':v,'humanReviewedThisHash':False,'platformMutation':False}
 save(H/'checkpoint.json',ledger);save(P/'production/review-ledger.json',ledger)
 print(ledger['durationSeconds'],ledger['captionedMasterSha256'])
if __name__=='__main__':{'pair':pair,'verify':verify,'asr':listen,'collect':collect}[sys.argv[1]]()
