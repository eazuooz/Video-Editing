"""Scoped8s native framing proof; preserves actual source colors/data/speed.

The enlargement copies panels from the same frame. It is not a replacement
table and no final actual-footage quota, narration timing or overlay is approved.
"""
from pathlib import Path
import json,hashlib,subprocess,datetime,os
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-native-framing-v1/renderdoc125-133-same-frame-table-proof.mp4'
RECORD=ROOT/'projects/game-lighting-history-04/production/renderdoc-native-framing-proof-v1.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if OUT.exists() or RECORD.exists():raise RuntimeError('Preserve prior native framing proof')
if sha(SRC)!='4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8':raise RuntimeError('Reviewed native source changed')
import psutil
if any(p.name().lower()=='ffmpeg.exe' and 'game-lighting-history' in ' '.join(p.cmdline()) for p in psutil.process_iter()):raise RuntimeError('Own single-render slot already occupied')
OUT.parent.mkdir(parents=True,exist_ok=True)
lines=['아래 가운데 자막은 고정합니다.','입력과 출력은 같은 프레임의 원본 표를 확대했습니다.']
textfiles=[]
for i,text in enumerate(lines):
 p=OUT.parent/f'caption-proof-line{i+1}.txt';p.write_text(text,'utf-8');textfiles.append(p)
# Source pixels: RenderDoc window, shader area, actual input/output panels.
# Move copied panels to upper blank/code-structure area, preserving the active
# return line lower down. Source event identity at the top remains visible.
filters="[0:v]trim=start=125:end=133,setpts=PTS-STARTPTS,split=2[base][table];[base]crop=1570:923:244:123,scale=1920:1080[editor];[table]crop=920:175:592:861,scale=1840:350[values];[editor][values]overlay=40:195:shortest=1,drawbox=x=38:y=193:w=1844:h=354:color=0x72c6c2:t=2,drawbox=x=219:y=912:w=1500:h=134:color=0x164b35:t=fill,drawbox=x=210:y=903:w=1500:h=134:color=white:t=fill,drawbox=x=210:y=903:w=1500:h=134:color=black:t=2"
for i,p in enumerate(textfiles):
 rel=p.relative_to(ROOT).as_posix();filters+=f",drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel}':fontsize=48:fontcolor=black:x=(w-text_w)/2:y={912+i*58}"
filters+='[out]'
cmd=['ffmpeg','-v','error','-threads','1','-i',str(SRC),'-filter_complex_threads','1','-filter_complex',filters,'-map','[out]','-an','-r','60','-frames:v','480','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(OUT)]
r=dict(status='rendering-scoped-native-framing-proof',startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=dict(path=SRC.relative_to(ROOT).as_posix(),sha256=sha(SRC)),sourceRange=[125,133],command=cmd,cpuThreads=1,gpuJobs=0,narrationIncluded=False,finalTimingApproved=False,actualFootageQuotaApproved=False,allFinalPixelsReviewed=False,annotationScope='Same-frame table magnification only; narration-timed red code/teal input/orange output annotations still pending.')
p=subprocess.Popen(cmd,cwd=ROOT);r['actualIdentity']=dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),command=psutil.Process(p.pid).cmdline(),cwd=str(ROOT));RECORD.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
code=p.wait();r.update(exitCode=code,endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='scoped-proof-rendered-awaiting-native-pixel-review' if code==0 else 'failed-preserving-source')
if code==0:r['output']=dict(path=OUT.relative_to(ROOT).as_posix(),sha256=sha(OUT))
RECORD.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(exitCode=code,status=r['status'],actualPid=p.pid,finalApproved=False)),flush=True)
raise SystemExit(code)
