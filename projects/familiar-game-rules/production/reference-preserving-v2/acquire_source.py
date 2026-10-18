"""Cache a bounded independently recorded FHD excerpt and its provenance."""
from pathlib import Path
from fractions import Fraction
import argparse, datetime, hashlib, json, os, subprocess
import yt_dlp
from yt_dlp.utils import download_range_func

R=Path(__file__).resolve().parents[4]
L=R/'projects/familiar-game-rules/production/local/reference-preserving-v2'
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
ap=argparse.ArgumentParser()
ap.add_argument('name');ap.add_argument('url');ap.add_argument('start',type=float);ap.add_argument('end',type=float)
ap.add_argument('--game',required=True);a=ap.parse_args()
authorization=json.loads((R/'projects/familiar-game-rules/production/reference-preserving-v2/authorization.json').read_text(encoding='utf-8'))
assert authorization['fullRevisionAuthorized'] and authorization['scope']=='familiar-game-rules only through complete Google Drive final review'
assert 0<=a.start<a.end and a.end-a.start<=360
dest=L/'media'/a.name;dest.parent.mkdir(parents=True,exist_ok=True)
record=dest.with_suffix('.source.json')
if record.exists():
 d=json.loads(record.read_text(encoding='utf-8'));f=R/d['file']
 if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256']:
  print(json.dumps({'cached':True,'file':d['file'],'dimensions':d['dimensions']}));raise SystemExit
opts={'format':'bestvideo[height=1080][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[height=1080]+bestaudio/best[height>=1080]',
 'outtmpl':str(dest)+'.%(ext)s','ffmpeg_location':str(FF),'merge_output_format':'mp4',
 'download_ranges':download_range_func(None,[(a.start,a.end)]),
 'force_keyframes_at_cuts':True,'noplaylist':True,'concurrent_fragment_downloads':2,
 'external_downloader_args':{'ffmpeg_o':['-threads','4','-preset','veryfast','-crf','18']},
 'postprocessor_args':{'ffmpeg':['-threads','4']},'retries':2,'fragment_retries':2,
 'writesubtitles':False,'writeautomaticsub':False,'quiet':False,'noprogress':True}
with yt_dlp.YoutubeDL(opts) as ydl: info=ydl.extract_info(a.url,download=True)
candidates=[p for p in dest.parent.glob(a.name+'.*') if p.suffix in ['.mp4','.mkv','.webm']]
assert len(candidates)==1,candidates
f=candidates[0]
probe=json.loads(subprocess.check_output([str(FF/'ffprobe.exe'),'-v','error','-show_streams','-show_format','-of','json',str(f)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert v['width']>=1920 and v['height']>=1080,v
expected=a.end-a.start
video_duration=float(v.get('duration') or 0)
if not video_duration:
 video_duration=float(subprocess.check_output([str(FF/'ffprobe.exe'),'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','csv=p=0',str(f)]))/float(Fraction(v['r_frame_rate']))
assert video_duration>=expected-.6,('truncated video stream',video_duration,expected)
formats=[dict(id=x.get('format_id'),width=x.get('width'),height=x.get('height'),fps=x.get('fps'),vcodec=x.get('vcodec'),acodec=x.get('acodec')) for x in info.get('requested_formats',[])]
d={'game':a.game,'url':a.url,'id':info.get('id'),'title':info.get('title'),'uploader':info.get('uploader'),
 'channelUrl':info.get('channel_url'),'uploadDate':info.get('upload_date'),'license':info.get('license'),
 'description':info.get('description'),'classification':'independent-gameplay-candidate',
 'referenceLesson':False,'requestedOriginalRange':[a.start,a.end],
 'file':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
 'dimensions':[v['width'],v['height']],'fps':v['r_frame_rate'],'duration':float(probe['format']['duration']),
 'videoDuration':video_duration,'videoFrames':v.get('nb_frames'),
 'selectedFormats':formats,'actualBeforeActionResult':'pending-direct-view',
 'rightsReview':'pending; original uploader license and publisher rules are separate',
 'audioPolicy':'Preserve original locally; inspect before deciding game SFX/music/narration treatment',
 'downloadedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:d[k] for k in ['game','file','dimensions','duration','sha256']}))
