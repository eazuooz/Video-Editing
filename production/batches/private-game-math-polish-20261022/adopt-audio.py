"""Recover only original uploaded audio; review pixels never enter production."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ident,source=sys.argv[1:3];q=read(B/'queue.json');entry=next(x for x in q['entries'] if x['id']==ident)
auth=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][q['authorization']['id']];assert auth['status']=='active' and ident in auth['ids']
P=R/'projects'/entry['slug'];O=P/'production/local/private-polish-v1';H=P/'production/private-polish-v1';O.mkdir(parents=True,exist_ok=True)
src=Path(source);d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]))
assert abs(float(d['format']['duration'])-entry['seconds'])<.2
ref=O/'baseline-upload-review.mp4';shutil.copy2(src,ref)
audio=O/'baseline-audio.m4a';subprocess.run(['ffmpeg','-v','error','-y','-i',str(ref),'-map','0:a:0','-c:a','copy',str(audio)],check=True)
a=next(x for x in d['streams'] if x['codec_type']=='audio');v=next(x for x in d['streams'] if x['codec_type']=='video')
save(H/'restoration.json',dict(baselineVideoId=entry['videoId'],baselinePage='https://studio.youtube.com/video/'+entry['videoId']+'/edit',downloadMethod='Observed playable media exported by browser pageAssets capability; not a new recording',reviewFile=ref.relative_to(R).as_posix(),reviewSha256=sha(ref),reviewDimensions=[v['width'],v['height']],reviewPixelsProductionAllowed=False,audioFile=audio.relative_to(R).as_posix(),audioSha256=sha(audio),duration=float(a['duration']),originalPcmAvailable=False,newTts=False,originalTimelineSha256=entry['originalTimelineSha256']))
entry.update(stage='restore-visual-code-and-FHD-sources',status='audio-recovered',audioRecovered=True,restoration=(H/'restoration.json').relative_to(R).as_posix());q['updatedAt']=datetime.now(timezone.utc).isoformat();save(B/'queue.json',q)
print(ident,'existing narration recovered; review video',v['width'],v['height'],'excluded from production pixels.')
