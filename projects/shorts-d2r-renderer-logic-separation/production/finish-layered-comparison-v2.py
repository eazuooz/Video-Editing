"""Package the one requested visual revision, keeping the approved AAC and SRTs."""
from pathlib import Path
import argparse, datetime, hashlib, html, json, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

P=Path(__file__).resolve().parents[1];R=P.parents[1]
L=P/'production/local/layered-comparison-v2';A=P/'production/local/audio-v1'
F=L/'final-reviewed';Q=F/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(a):
 result=subprocess.run(a,cwd=R,capture_output=True)
 if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-6000:])
 return result.stdout
def guard():
 assert sha(A/'voice/narration.wav')=='9809f48b8a8dfbf0fc20c80e3f6c2acd4d7d8020ec1a3e69962e122f328d96be'
 assert read(P/'script/captions.json')['frames']==2620
def pair(visual):
 guard();F.mkdir(parents=True,exist_ok=True);visual=Path(visual).resolve()
 assert visual.name.startswith('d2layers-v2-') and visual.suffix=='.mp4'
 assert visual.is_relative_to(Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025').resolve())
 assert not (F/'clean.mp4').exists() and not (F/'captioned.mp4').exists(),'Preserve all earlier renders'
 run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(A/'final-mix.m4a'),'-i',str(P/'production/local/static-header-v1.png'),
      '-filter_complex','[0:v][2:v]overlay=0:0:format=auto[v]','-map','[v]','-map','1:a:0','-frames:v','2620','-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(F/'clean.mp4')])
 ass=(A/'captions.ko.ass').relative_to(R).as_posix()
 run(['ffmpeg','-v','error','-n','-i',str(F/'clean.mp4'),'-vf','ass='+ass,'-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(F/'captioned.mp4')])
 for lang in ['ko','en']:shutil.copy2(A/f'captions.{lang}.srt',F/f'captions.{lang}.srt')
 save(F/'build-receipt.json',{'revision':'layered-comparison-v2','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'visual':{'path':str(visual),'sha256':sha(visual)},'voicePcmSha256':sha(A/'voice/narration.wav'),'mixSha256':sha(A/'final-mix.m4a'),'assSha256':sha(A/'captions.ko.ass'),'renderer':'Motion Canvas CPU; libx264 CPU final encodes; no GPU production job','frames':2620,'speechSpeed':1,'oldPrivateYoutubeId':'rrbimJ4XwHk','platformMutation':False})
 print('Four files packaged',flush=True)
def integrity():
 guard();reports=[];aac=[]
 for name in ['clean','captioned']:
  p=F/(name+'.mp4')
  run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'])
  info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in info['streams'] if s['codec_type']=='video')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',2620)
  pts=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(p)]))['frames']
  assert len(pts)==2620 and all(abs(float(q['best_effort_timestamp_time'])-i/60)<2e-6 for i,q in enumerate(pts))
  raw=run(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','adts','pipe:1']);aac.append(hashlib.sha256(raw).hexdigest())
  reports.append({'name':p.name,'path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'durationSeconds':float(v['duration']),'frames':2620,'width':1080,'height':1920,'fps':60,'fullDecode':'pass','regularPts':'pass'})
 raw=run(['ffmpeg','-v','error','-i',str(A/'final-mix.m4a'),'-map','0:a:0','-c','copy','-f','adts','pipe:1'])
 assert aac[0]==aac[1]==hashlib.sha256(raw).hexdigest()
 captions=read(P/'script/captions.json');assert all(0<=c['start']<c['end']<=2620/60 for c in captions['cues'])
 for lang in ['ko','en']:
  p=F/f'captions.{lang}.srt';assert sha(p)==sha(A/p.name);reports.append({'name':p.name,'path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size})
 save(F/'integrity.json',{'status':'pass','revision':'layered-comparison-v2','outputs':reports,'sameAacPayloadAsApprovedMix':True,'aacAdtsSha256':aac[0],'unchangedPcm':sha(A/'voice/narration.wav'),'unchangedKoEnSubtitles':True,'allCaptionTimesInsideVideo':True,'actualListening':'pending; unchanged audio retained'})
 print('Integrity passed',flush=True)
def qa():
 Q.mkdir(exist_ok=True);captions=read(P/'script/captions.json')
 frames=sorted(set(list(range(0,2620,60))+[2619]+[round((q['start']+q['end'])/2*60) for q in captions['cues']]+[321,322,692,693,1248,1249,1284,1308,1332,1374,1807,1808,2167,2168,2244,2245,2409,2460]))
 expression='+'.join('eq(n\\,'+str(n)+')' for n in frames)
 run(['ffmpeg','-v','error','-n','-threads','3','-i',str(F/'captioned.mp4'),'-vf','select='+expression,'-fps_mode','vfr','-start_number','0','-threads','1','-q:v','2',str(Q/'frame-%03d.jpg')])
 rows=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for i,frame in enumerate(frames):
  p=Q/f'frame-{i:03d}.jpg'
  with Image.open(p) as image:
   image.load();assert image.size==(1080,1920)
   image.resize((375,667),Image.Resampling.LANCZOS).save(Q/f'frame-{i:03d}-375.jpg',quality=95)
  rows.append({'frame':frame,'seconds':frame/60,'native':p.name,'mobile':f'frame-{i:03d}-375.jpg','sha256':sha(p)})
 for batch,start in enumerate(range(0,len(rows),12)):
  selected=rows[start:start+12];canvas=Image.new('RGB',(1500,3*705),(18,18,18));draw=ImageDraw.Draw(canvas)
  for j,row in enumerate(selected):
   x=j%4*375;y=j//4*705
   draw.text((x+8,y+5),f"{row['seconds']:.2f}s | frame {row['frame']}",font=font,fill='white')
   with Image.open(Q/row['mobile']) as image:canvas.paste(image,(x,y+36))
  canvas.save(Q/f'contact-{batch+1:02d}.jpg',quality=94)
 save(Q/'index.json',{'masterSha256':sha(F/'captioned.mp4'),'sampledFrames':len(rows),'rows':rows,'reviewStatus':'generated, direct visual review to be recorded separately'})
 print('QA frames prepared',len(rows),flush=True)
def page():
 integrity=read(F/'integrity.json');master=next(x for x in integrity['outputs'] if x['name']=='captioned.mp4')
 body=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>디아블로 그래픽 · 상하 비교 수정본</title><style>body{{background:#080b09;color:white;font:17px sans-serif;max-width:900px;margin:auto;padding:24px}}video{{display:block;width:min(100%,420px);margin:24px auto}}a{{color:#92df9c}}code{{overflow-wrap:anywhere}}li{{margin:12px 0}}</style><h1>위 레저렉션 · 아래 클래식</h1><p>같은 시점의 실제 화면을 비교하고, 하나의 게임 상태가 두 표시 계층으로 연결되는 원리 설명입니다.</p><p>1080×1920 · 60fps · 43.67초 / 기존 음성·음악·한영 자막 유지</p><video controls playsinline preload="metadata" src="captioned.mp4"></video><ul><li><a href="captioned.mp4">전체 자막 MP4</a></li><li><a href="clean.mp4">자막 없는 MP4</a></li><li><a href="captions.ko.srt">한국어 SRT</a> · <a href="captions.en.srt">영어 SRT</a></li></ul><p>버전: layered-comparison-v2<br>SHA256: <code>{master['sha256']}</code></p><p>기술 검사 통과. 직접 확인한 시각 표본과 미완료 청취 범위는 검수 기록에 분리합니다. 사용자 최종 검수 전이며 이전 비공개 영상은 보존됩니다.</p></html>'''
 (F/'playback.html').write_text(body,encoding='utf8');print(F.resolve())
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['pair','integrity','qa','page','all']);parser.add_argument('--visual');parser.add_argument('--output',default='final-reviewed');a=parser.parse_args()
 assert a.output in ['final-reviewed','final-reviewed-b','final-reviewed-c'],'Use an owned immutable attempt'
 F=L/a.output;Q=F/'qa'
 if a.command in ['pair','all']:pair(a.visual)
 if a.command in ['integrity','all']:integrity()
 if a.command in ['qa','all']:qa()
 if a.command in ['page','all']:page()
