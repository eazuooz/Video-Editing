"""Download only a selected short window from our published video and decode a frame."""
import argparse, hashlib, json, subprocess
from pathlib import Path

ROOT=Path('D:/Github/VideoEditing')
HERE=Path(__file__).resolve().parent

def capture(ident,video_id,second):
    target=HERE/'evidence'/f'{ident}-{second:07.2f}'
    jpg=target.with_suffix('.jpg')
    record=Path(str(jpg)+'.json')
    if jpg.exists() and record.exists():return json.loads(record.read_text(encoding='utf8'))
    template=str(target)+'.%(ext)s'
    result=subprocess.run(['yt-dlp','--quiet','--no-progress','--no-warnings','--no-playlist',
        '-f','bv[height=1080]/bv[height<=1080]/best[height<=1080]',
        '--download-sections',f'*{second}-{second+.15}', '--force-keyframes-at-cuts',
        '-o',template,'https://www.youtube.com/watch?v='+video_id],cwd=ROOT,capture_output=True)
    if result.returncode:
        record.write_text(json.dumps({'status':'download-failed','videoId':video_id,'seconds':second,
            'returnCode':result.returncode,'message':'Selected public video window unavailable; no fabricated frame.'},indent=2),encoding='utf8')
        raise RuntimeError(f'{ident}: selected public frame download failed')
    clips=list(target.parent.glob(target.name+'.*'))
    clip=next((x for x in clips if x.suffix in {'.mp4','.webm','.mkv'}),None)
    if clip is None:raise RuntimeError('No captured clip for '+ident)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(clip),'-frames:v','1','-q:v','2',str(jpg)],check=True,cwd=ROOT)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(jpg)]))['streams'][0]
    d=dict(status='captured-pending-visual-review',videoId=video_id,sourceUrl='https://www.youtube.com/watch?v='+video_id,
        seconds=second,path=str(jpg),width=probe['width'],height=probe['height'],
        sha256=hashlib.sha256(jpg.read_bytes()).hexdigest(),clip=str(clip),
        clipSha256=hashlib.sha256(clip.read_bytes()).hexdigest(),
        source='Our actual uploaded video, selected original timeline timestamp; no invented game frame.')
    record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return d

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('video');p.add_argument('seconds',type=float);a=p.parse_args()
    print(json.dumps(capture(a.id,a.video,a.seconds),ensure_ascii=False))
