"""One CPU2 batch for two held source windows and timed screen roles."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os,psutil,ctypes,traceback
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/remaining-action-roles-v3'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stamp=lambda:datetime.now(timezone.utc).isoformat()
sp=R/'remaining-action-roles-execution-v3.json';assert not sp.exists() and not OUT.exists()
cpu=psutil.cpu_percent(interval=1);ram=psutil.virtual_memory().available//1024;assert cpu<85 and ram>8000000,(cpu,ram)
busy=[]
for proc in psutil.process_iter(['pid','cmdline','create_time']):
 cmd=proc.info['cmdline'] or []
 if proc.pid!=os.getpid() and cmd and cmd[0].lower().endswith(('python.exe','node.exe')) and any(v in ' '.join(cmd) for v in ['render-motion-extra-annotation-pieces-v','render-motion-remaining-action-roles-v3.py','extract-motion-button-result-timing-v1.py']):busy.append(proc.info)
assert not busy,busy
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
for row in protected:assert sha(ROOT/row['path'])==row['sha256']
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],capture_output=True,text=True,check=True).stdout
(R/'remaining-action-roles-current-cim-v3.json').write_text(cim,'utf-8')
allocation=read(R/'paragraph-native-allocation-v4.json');anchors=read(R/'remaining-action-annotation-anchors-v2.json')
for tr in anchors['tracks']:
 for row in tr['rows']:assert sha(ROOT/row['path'])==row['sha256']
pieces=[]
for scene in allocation['newScenes']:
 for piece in scene['parts']:
  if piece['classification'].startswith('actual') and piece['sourceKey']!='powerwash' and piece['nativeInFrame']!=1289:
   pieces.append(dict(piece,sceneId=scene['id']))
pieces=[p for p in pieces if p['id'] in ['07b-laser-target','08b-board-removal']]
assert len(pieces)==2 and sum(p['frames'] for p in pieces)==1619
OUT.mkdir();ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',34);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',26);bf=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
state=dict(schemaVersion=1,startedAt=stamp(),pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=psutil.Process().cmdline(),cwd=str(ROOT),cpuThreads=2,gpuJobs=0,
 resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu,ownedHeavyOtherJobs=0),protected71ShaMatched=True,allocation='paragraph-native-allocation-v4.json',allocationSha256=sha(R/'paragraph-native-allocation-v4.json'),
 status='running',actualOuterExitCode=None,pieces=[],narrationWordTimingPrepared=True,allNarrationTimedMovingPixelsApproved=False,
 finalAudioUsed=False,finalCaptionsBurned=False,finalCueApproval=False,sourceAudioUsed=False,localOnly=True)
save=lambda:sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');save()
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(activeOwnedWorkers=1,ownedJob=dict(active=True,status='running',pid=state['pid'],createTime=state['createTime'],command=Path(__file__).name,sessionId=None,state=sp.relative_to(ROOT).as_posix()),next='Reuse actual narrow two-piece role repair worker; other six completed pieces stay unchanged. After actual exit directly review every encoded anchor/reveal/cut, normal1x, and current speech mapping; do not launch duplicate renderer. Existing PortalV2/PWashV4/comparisons/summary remain unchanged.');cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
def point(tr,n):
 rows=tr['rows']
 if 'segments' in tr and not any(s['start']<=n<s['endExclusive'] for s in tr['segments']):return None
 if n<rows[0]['nativeFrame'] or n>=tr['rangeEndExclusive']:return None
 for a,b in zip(rows,rows[1:]):
  if a['nativeFrame']<=n<=b['nativeFrame']:
   u=(n-a['nativeFrame'])/(b['nativeFrame']-a['nativeFrame']);xy=[a['screenPoint1280'][i]+u*(b['screenPoint1280'][i]-a['screenPoint1280'][i]) for i in [0,1]]
   return [round(xy[0]*1.25+160),round(xy[1]*1.25)]
 return None
def reveal(tr,n,piece):
 if tr['id']=='portal-held-cube':return n>=1159
 if tr['id']=='portal-target-status':return n>=2352
 if tr['id']=='portal-device-cue':return n>=1932
 if tr['id']=='alyx-board-object':return n>=3365
 return True
try:
 for piece in pieces:
  assert sha(ROOT/piece['sourcePath'])==piece['sourceSha256']
  folder=OUT/piece['id'];folder.mkdir();output=folder/'clean-role-annotation.mp4'
  first=piece['nativeInFrame'];last=piece['nativeOutFrameExclusive'];count=piece['frames'];fps=30000/1001 if piece['sourceKey']=='portal2' else 60000/1001
  dec=[FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/piece['sourcePath']),'-vf',f'trim=start_frame={first}:end_frame={last},setpts=PTS-STARTPTS,scale=1920:1080,fps=60','-frames:v',str(count),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
  enc=[FF,'-v','error','-threads','2','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-frames:v',str(count),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(output)]
  rec=dict(id=piece['id'],sceneId=piece['sceneId'],frames=count,sourcePath=piece['sourcePath'],sourceSha256=piece['sourceSha256'],nativeInFrame=first,nativeOutFrameExclusive=last,sourceFps=fps,status='rendering',decodeCommand=dec,encodeCommand=enc,samples=[],boards=[])
  state['pieces'].append(rec);save();active_tracks=[tr for tr in anchors['tracks'] if tr['sourceKey']==piece['sourceKey']]
  with (folder/'decode.log').open('wb') as dl,(folder/'encode.log').open('wb') as el:
   decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl);encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el);rec.update(decoderPid=decoder.pid,encoderPid=encoder.pid);save()
   for f in range(count):
    raw=bytearray();size=1920*1080*3
    while len(raw)<size:
     c=decoder.stdout.read(size-len(raw));assert c,'source EOF';raw.extend(c)
    src=Image.frombytes('RGB',(1920,1080),bytes(raw));im=src.resize((480,270)).filter(ImageFilter.GaussianBlur(8)).resize((1920,1080));im.paste(src.resize((1600,900)),(160,0));d=ImageDraw.Draw(im);native=first+f*fps/60
    for tr in active_tracks:
     pt=point(tr,native)
     if pt is None or not reveal(tr,native,piece):continue
     red=tr['color']=='red';color='#de3434' if red else '#159fcc';label=tr['label'];left=1060 if red else 180;right=1735 if red else 855
     d.rectangle((left,133,right,190),fill='white',outline=color,width=3);d.text((left+12,141),label,font=font,fill=color)
     origin=(left+40,190);d.line([origin,(origin[0]-25,224),tuple(pt)],fill=color,width=5);x,y=pt
     if red:d.line([(x-23,y+14),(x-23,y-14),(x+23,y-14)],fill=color,width=5)
     else:d.ellipse((x-17,y-17,x+17,y+17),outline=color,width=4)
    credit='Portal 2 · Valve' if piece['sourceKey']=='portal2' else 'Half-Life: Alyx · Valve'
    box=d.textbbox((0,0),credit,font=small);cw=box[2]-box[0];d.rectangle((960-cw/2-12,35,960+cw/2+12,76),fill='white');d.text((960-cw/2,39),credit,font=small,fill='black')
    if f<min(180,count):
     label='다른 시연 구간 · 실제 관찰';d.rectangle((180,810,830,865),fill='white');d.text((196,818),label,font=font,fill='#174735')
    encoder.stdin.write(im.tobytes())
   decoder.stdout.close();encoder.stdin.close();dc=decoder.wait();ec=encoder.wait();assert dc==ec==0,(dc,ec)
  wd=subprocess.run([FF,'-v','error','-threads','2','-i',str(output),'-f','null','-'],capture_output=True,text=True);assert wd.returncode==0 and not wd.stderr
  stream=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(output)]))['streams'][0]
  assert int(stream['nb_frames'])==count and stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
  selected={0,count-1}
  # Source/action changes, exact role anchors and timed reveals, at least1Hz.
  selected.update(range(0,count,60))
  # Dense quarter-second sampling through both repaired marker windows.
  if piece['id']=='07b-laser-target':selected.update(range(509,662,15))
  if piece['id']=='08b-board-removal':selected.update(range(120,302,15))
  for tr in active_tracks:
   for row in tr['rows']:
    q=round((row['nativeFrame']-first)/fps*60)
    if 0<=q<count:selected.update([max(0,q-1),q,min(count-1,q+1)])
  for threshold in [1159,2352,1932,3365,3418,3477,3537,3063,3069,2948]:
   q=round((threshold-first)/fps*60)
   if 0<=q<count:selected.update([max(0,q-1),q,min(count-1,q+1)])
  sampled=sorted(selected);sample_dir=folder/'samples';sample_dir.mkdir();sel='+'.join(f'eq(n\\,{n})' for n in sampled)
  run=subprocess.run([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(output),'-vf','select='+sel,'-fps_mode','passthrough','-an',str(sample_dir/'sample-%03d.png')],capture_output=True,text=True);assert run.returncode==0,run.stderr
  for f,p in zip(sampled,sorted(sample_dir.glob('sample-*.png'))):rec['samples'].append(dict(frame=f,pts=f*1500,nativeFrameEstimate=first+f*fps/60,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
  assert len(rec['samples'])==len(sampled)
  for start in range(0,len(rec['samples']),4):
   chunk=rec['samples'][start:start+4];board=Image.new('RGB',(1920,1160),'#e4e7ec');bd=ImageDraw.Draw(board)
   for k,s in enumerate(chunk):
    x=k%2*960;y=k//2*580;board.paste(Image.open(ROOT/s['path']).resize((960,540)),(x,y+40));bd.text((x+8,y+5),f"{piece['id']} encoded{s['frame']} PTS{s['pts']}",font=bf,fill='black')
   p=folder/f'board-{len(rec["boards"])+1:02d}.png';board.save(p);rec['boards'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=chunk))
  rec.update(status='completed-awaiting-direct-pixel-and-speech-review',path=output.relative_to(ROOT).as_posix(),sha256=sha(output),decodeExitCode=dc,encodeExitCode=ec,wholeDecodeExitCode=0,extractionExitCode=0,stream=stream);save()
 state.update(status='completed-awaiting-direct-review',exitCode=0,finishedAt=stamp(),encodedSampleCount=sum(len(p['samples']) for p in state['pieces']),boardCount=sum(len(p['boards']) for p in state['pieces']));save()
 print(json.dumps(dict(pieces=len(pieces),frames=1619,samples=state['encodedSampleCount'],boards=state['boardCount'],decodeEncodeExtraction=0)))
except BaseException:
 state.update(status='failed-preserve-all-evidence',exitCode=1,error=traceback.format_exc());save();raise
