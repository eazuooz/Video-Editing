"""Short source-level playback excerpts, never a delivery/master substitute."""
import html
from polish_common import *

e=Episode('M08');e.authorized()
rendered=read(e.H/'conversions-legibility-render.json')
audio=read(e.H/'restoration.json');assert sha(R/audio['audioFile'])==audio['audioSha256']
out=e.O/'conversions-legibility-moving';out.mkdir(exist_ok=True)
records=[]
for sid,start,seconds in [('IP04',9,7),('18',27,7),('19',8,7),('IP08',25,13)]:
    slot=next(s for s in e.T['scenes'] if s['id']==sid)
    seconds=min(seconds,slot['seconds']-start)
    item=rendered['scenes'][sid];src=R/item['path'];assert sha(src)==item['sha256']
    dst=out/(sid+'.mp4');absolute=slot['start']+start
    e.ff(['-ss',start,'-i',src,'-ss',absolute,'-i',R/audio['audioFile'],
          '-t',seconds,'-map','0:v:0','-map','1:a:0',
          '-vf',f'setpts=PTS+{absolute}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS',
          *ENC,'-c:a','aac','-b:a','192k',dst],f'moving-legibility-{sid}.log',e.O)
    records.append({'scene':sid,'sourceSha256':item['sha256'],'sourceSeconds':start,'globalSeconds':absolute,
                    'seconds':seconds,'reviewClip':rel(dst),'reviewClipSha256':sha(dst)})
buttons=''.join(f'<button onclick="play(\'{r["scene"]}\')">{html.escape(r["scene"])}</button>' for r in records)
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>M08 explanation source review</title>
<style>body{margin:15px;background:#222;color:white;font:16px system-ui}video{display:block;width:min(100%,900px);margin:15px 0}button{padding:10px;margin-right:8px}#state{white-space:pre-wrap}</style>
<h1>M08 설명 원본 재생 점검</h1><p>최종 영상 아님 · 기존 음성에서 같은 구간을 발췌 · 1배속</p>'''+buttons+'''
<button onclick="v.pause()">일시정지</button><button onclick="v.style.width='375px'">375px</button><button onclick="v.style.width='min(100%,900px)'">확대</button>
<video id="v" muted playsinline></video><p id="state"></p><script>
function play(id){v.src=id+'.mp4';v.playbackRate=1;v.play()}
setInterval(()=>{document.getElementById('state').textContent=JSON.stringify({source:v.getAttribute('src'),time:v.currentTime,duration:v.duration,rate:v.playbackRate,paused:v.paused,ended:v.ended,width:v.videoWidth,height:v.videoHeight,error:v.error?v.error.code:null})},200);
</script>''',encoding='utf8')
save(e.H/'conversions-legibility-moving-samples.json',{'scope':'Four playback excerpts only; not full master approval',
     'audioSha256':audio['audioSha256'],'captionSha256':sha(e.O/'captions.ko.ass'),'samples':records,'reviewStatus':'await-direct-playback'})
