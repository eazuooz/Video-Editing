"""Verify actual final media, speech coverage, captions and local-review delivery."""
from pathlib import Path
import json,subprocess,hashlib,re,html,math,difflib
import numpy as np
from PIL import ImageFont
from tutorial_speech_evidence import compare_speech
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v5';F=L/'final';Q=L/'qa';Q.mkdir(exist_ok=True)
def run(a):
 try:return subprocess.run(list(map(str,a)),check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
 except subprocess.CalledProcessError as e:raise RuntimeError(e.stderr.decode('utf-8','replace')[-4000:]) from e
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def norm(s):return ''.join(c.lower() for c in s if c.isalnum())
d=json.loads((P/'production/full-video-delivery.json').read_text('utf-8'));t=json.loads((L/'timeline.json').read_text());probes=[];audio=[]
for name in ('clean','captioned'):
 p=F/(P.name+'.'+name+'.mp4');j=json.loads(run(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',p]).stdout)
 v=next(s for s in j['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'60/1',t['frames']),(name,v,t['frames'])
 run(['ffmpeg','-hide_banner','-v','error','-i',p,'-f','null','-'])
 pts=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',p]).stdout.decode('utf-8')
 values=np.array([float(line.split(',')[0]) for line in pts.splitlines() if line.split(',')[0].strip()])
 assert len(values)==t['frames'] and np.max(np.abs(np.diff(values)-1/60))<.000003,(name,len(values),float(np.max(np.abs(np.diff(values)-1/60))))
 audio.append(run(['ffmpeg','-hide_banner','-v','error','-i',p,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.decode().strip());probes.append({'name':name,'probe':j,'fullDecodePassed':True})
assert audio[0]==audio[1],audio
cues=json.loads((L/'captions.json').read_text('utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',48)
try:font.set_variation_by_name('Medium')
except ValueError:pass
samples=[(v,round((v['start']+v['end'])/2*60)) for v in cues];frameNums=sorted(set(n for _,n in samples))
def balanced(items):
 if len(items)==1:return f'eq(n,{items[0]})'
 mid=len(items)//2;return '('+balanced(items[:mid])+'+'+balanced(items[mid:])+')'
sel=balanced(frameNums)
raw=run(['ffmpeg','-hide_banner','-v','error','-threads','2','-i',F/(P.name+'.captioned.mp4'),'-vf',f"select='{sel}',crop=1920:140:0:910",'-fps_mode','vfr','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-']).stdout
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,140,1920,3);assert len(frames)==len(frameNums);byFrame=dict(zip(frameNums,frames));pixel=[]
for v,n in samples:
 w=round(font.getlength(v['ko']))+44;x=960-w//2
 patch=byFrame[n][23:28,x+7:x+16];white=float((patch.mean(axis=2)>235).mean());pixel.append({'cue':v['index'],'frame':n,'whiteBoxCornerFraction':white});assert white>.6,(v,white)
align=json.loads((L/'alignment-review.json').read_text('utf-8'));narrAsr=json.loads((Q/'narration.timestamps.json').read_text('utf-8'));mixAsr=json.loads((Q/'mix.timestamps.json').read_text('utf-8'));assert mixAsr['audio_sha256']==sha(L/'final-mix.m4a') and narrAsr['audio_sha256']==sha(L/'narration-aligned.wav')
coverage=compare_speech(narrAsr,mixAsr,t,L/'narration-aligned.wav')
assert coverage['ratioAgainstFullNarrationAsr']>.94 and not coverage['materialMissingSpans'],coverage
qa={'probes':probes,'sameEncodedAudioBothMasters':True,'encodedAudioHash':audio[0],'captionSamples':len(pixel),'captionBoxAllCueCentersPassed':True,'minimumNarrationAlignment':min(r['ratio'] for r in align['paragraphs']),'finalMixSpeechCoverage':coverage,'humanFullReview':False,'physicalMobileQa':False,'webQa':'production/web-browser-qa.json'}
(Q/'caption-pixels.json').write_text(json.dumps(pixel,indent=2)+'\n','utf-8');(P/'production/full-video-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
def clock(s):return f'{int(s)//60:02}:{int(s)%60:02}'
chapters=''.join(f'<li><button data-t="{s["start"]}">{clock(s["start"])} · {html.escape(s["title"])}</button></li>' for s in t['scenes'])
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AI 3D LOFI 게이밍룸 · 전체 검수</title><style>body{{margin:0;background:#0c1513;color:#eeeedd;font:16px/1.7 system-ui,"Malgun Gothic",sans-serif}}main{{max-width:1200px;margin:30px auto;padding:22px}}a{{color:#91d5b9}}video{{width:100%;background:#000}}.links{{display:flex;gap:22px;flex-wrap:wrap}}button{{background:#1a3027;color:#e5eada;border:1px solid #496353;padding:9px 14px;cursor:pointer;font:inherit}}ol{{columns:2;list-style:none;padding:0}}li{{margin:7px 0}}h1{{font-size:29px}}small{{color:#bbc7bc}}@media(max-width:650px){{ol{{columns:1}}}}</style><main><small>얌얌코딩 · 로컬 전체 검수본 · 1080p / 60fps</small><h1>AI로 만드는 3D LOFI 게이밍룸</h1><p>이미지 입력·요청문·Tripo 설정·Codex와 Unity 연결부터 직접 조작되는 웹게임까지. {clock(t['duration'])} 분량의 전체 영상입니다.</p><video id="film" controls preload="metadata"><source src="{P.name}.captioned.mp4" type="video/mp4"><track src="captions.en.vtt" label="English" srclang="en" kind="subtitles"></video><p class="links"><a href="requests.html">따라 만들기 요청문 19개</a><a href="http://127.0.0.1:9324/" target="_blank">게임 직접 플레이</a><a href="{P.name}.clean.mp4">자막 없는 MP4</a><a href="{P.name}.ko.srt">한국어 SRT</a><a href="{P.name}.en.srt">English SRT</a><a href="https://app.notion.com/p/41b0b1ffa61e81f1a484f6c3e4b0555b">AI 게임 제작 위키</a></p><p>사용자의 전체 시청·발음·속도 검수는 대기 중입니다. YouTube 업로드·공개 웹 배포는 진행하지 않았습니다.</p><h2>바로 확인하기</h2><ol>{chapters}</ol></main><script>const v=document.querySelector('video');document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{{v.currentTime=+b.dataset.t;v.play()}});</script></html>'''
(F/'index.html').write_text(page,'utf-8');srt=(F/(P.name+'.en.srt')).read_text('utf-8');(F/'captions.en.vtt').write_text('WEBVTT\n\n'+re.sub(r'(\d\d:\d\d:\d\d),(\d{3})',r'\1.\2',srt),'utf-8')
d.update(stage='local-final-review-ready',technicalQa='projects/ai-3d-lofi-gaming-room/production/full-video-qa.json',reviewUrl='http://127.0.0.1:9329/',gameReviewUrl='http://127.0.0.1:9324/',humanReview=False,youtubeUploaded=False)
(P/'production/full-video-delivery.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');print('Verified',t['frames'],'frames,',len(pixel),'caption samples',flush=True)
