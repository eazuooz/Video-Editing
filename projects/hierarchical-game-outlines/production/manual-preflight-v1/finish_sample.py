from pathlib import Path
import datetime, hashlib, json, subprocess
import psutil
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
state=json.loads((O/'sample-state.json').read_text(encoding='utf8'))
assert state['exitCode']==0 and not (O/'lofi-comparison-matched.mp4').exists()
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
resource=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),cpu=psutil.cpu_percent(interval=1),memory=psutil.virtual_memory().available)
assert resource['cpu']<85 and resource['memory']>8_000_000_000
def run(args):
 p=subprocess.run([FF,'-hide_banner','-nostdin','-threads','2',*args],capture_output=True,text=True,encoding='utf8',errors='replace')
 if p.returncode: raise RuntimeError(p.stderr[-2000:])
 return p.stderr
def measure(path,target):
 t=run(['-i',str(path),'-vn','-af',f'loudnorm=I={target}:TP=-2:LRA=7:print_format=json','-f','null','-'])
 return json.loads(t[t.rfind('{'):t.rfind('}')+1])
dur=state['seconds'];voice=R/'projects/hierarchical-game-outlines/production/final-v1/narration-timed-body.wav'
if not (O/'sample-voice.wav').exists():
 run(['-loglevel','error','-i',str(voice),'-filter_complex_threads','2','-filter_complex','[0:a]asplit[a][b];[a]atrim=0:9.233333333333333,asetpts=PTS-STARTPTS[a0];[b]atrim=38.21666666666667:75.66666666666667,asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[out]','-map','[out]','-c:a','pcm_s16le',str(O/'sample-voice.wav')])
if not (O/'sample-music.wav').exists():
 run(['-loglevel','error','-i',str(O/'Late-Night-Radio.mp3'),'-t',str(dur),'-c:a','pcm_s16le',str(O/'sample-music.wav')])
mv=measure(O/'sample-voice.wav',-16);mm=measure(O/'sample-music.wav',-31)
def norm(m,i):return f"loudnorm=I={i}:TP=-2:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000"
flt=f"[0:a]{norm(mv,-16)},asplit=2[n][s];[1:a]{norm(mm,-31)},afade=t=in:d=0.45,afade=t=out:st={dur-.45}:d=0.45[m];[m][s]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[duck];[n][duck]amix=inputs=2:duration=first:normalize=0[out]"
run(['-loglevel','error','-i',str(O/'sample-voice.wav'),'-i',str(O/'sample-music.wav'),'-filter_complex_threads','2','-filter_complex',flt,'-map','[out]','-c:a','pcm_s16le','-ar','48000','-ac','2',str(O/'sample-mix-matched.wav')])
run(['-loglevel','error','-i',str(O/'original-comparison.mp4'),'-i',str(O/'sample-mix-matched.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(dur),'-movflags','+faststart',str(O/'lofi-comparison-matched.mp4')])
measurements={n:measure(O/n,-16) for n in ['original-comparison.mp4','lofi-comparison-matched.mp4']}
assert float(measurements['lofi-comparison-matched.mp4']['input_tp'])<=-1.5
run(['-loglevel','error','-i',str(O/'lofi-comparison-matched.mp4'),'-f','null','-'])
state.update(comparisonMixCorrection=dict(reason='Initial single-pass narration normalization resulted in -19.13 LUFS; use measured two-pass normalization for a fair comparison.',initialPreviewPreserved=True,resource=resource,voiceMeasurement=mv,musicMeasurement=mm),currentPreview='lofi-comparison-matched.mp4',comparisonMeasurements=measurements)
state['outputs']['lofi-comparison-matched.mp4']=hashlib.sha256((O/'lofi-comparison-matched.mp4').read_bytes()).hexdigest()
(O/'sample-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(measurements))
