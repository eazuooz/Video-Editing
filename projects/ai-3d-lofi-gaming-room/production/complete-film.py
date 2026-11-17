"""Finish the selected film after resumable TTS, without advancing other projects."""
from pathlib import Path
import json,subprocess,time,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v4';PY=R/'qwen3-tts/.venv/Scripts/python.exe';F=L/'final';F.mkdir(parents=True,exist_ok=True)
def run(a):
 print('Running',Path(str(a[0])).name,Path(str(a[1])).name if len(a)>1 else '',flush=True)
 if Path(str(a[0]))==PY:a=[a[0],'-X','utf8','-u',*a[1:]]
 subprocess.run(list(map(str,a)),cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
while not (L/'narration/ai-3d-lofi-gaming-room.timing.json').exists():time.sleep(8)
audioReport=P/'production/full-video-audio-qa.json'
reuseAudio=False
if audioReport.exists() and (L/'timeline.json').exists():
 aq=json.loads(audioReport.read_text('utf-8'));tt=json.loads((L/'timeline.json').read_text('utf-8'))
 reuseAudio=(aq.get('narrationSha256')==sha(L/'narration-aligned.wav') and aq.get('mixSha256')==sha(L/'final-mix.wav') and abs(float(aq['measuredEncoded']['input_i'])+16)<=.3 and tt['scenes'][-1]['frames']>=600 and all(sha(Path(r['source']))==r['sourceSha256'] for r in tt['scenes']))
if reuseAudio:print('Reusing current validated audio and its ASR cache',flush=True)
else:run([PY,P/'production/build-film-audio.py'])
Q=L/'qa';Q.mkdir(exist_ok=True)
for name,source in [('narration',L/'narration-aligned.wav'),('mix',L/'final-mix.m4a')]:
 out=Q/(name+'.txt');rec=out.with_suffix('.timestamps.json')
 if not rec.exists() or json.loads(rec.read_text('utf-8'))['audio_sha256']!=sha(source):run([PY,R/'qwen3-tts/transcribe_reference.py',source,'--output',out,'--device','cuda','--timestamps','word'])
run([PY,P/'production/build-film-captions.py'])
run([PY,P/'production/render-film.py'])
t=json.loads((L/'timeline.json').read_text('utf-8'));files=[R/'projects/ai-2d-game-assets/assets/local/intro.mp4']+[L/'visual'/('scene-'+r['id']+'.mp4') for r in t['scenes']]+[R/'projects/ai-2d-game-assets/assets/local/outro.mp4']
for r in t['scenes']:
 rec=json.loads((L/'visual'/('scene-'+r['id']+'.json')).read_text('utf-8'));assert rec['frames']==r['frames'] and rec['inputs']['narration']==r['sourceSha256']
concat=L/'concat.txt';concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in files)+'\n','utf-8')
clean=F/(P.name+'.clean.mp4');captioned=F/(P.name+'.captioned.mp4')
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-i',L/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean])
ass=(L/'captions.ko.ass').relative_to(R).as_posix()
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-reinit_filter','0','-i',clean,'-vf',f"setsar=1,ass='{ass}'",'-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',captioned])
import shutil
for lang in ('ko','en'):shutil.copy2(L/f'captions.{lang}.srt',F/(P.name+f'.{lang}.srt'))
report={'stage':'rendered-internal-QA-pending','duration':t['duration'],'frames':t['frames'],'outputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [clean,captioned,*sorted(F.glob('*.srt'))]],'branding':[{'path':str(p),'sha256':sha(p),'preservedOriginalPixelsAndFrameTiming':True} for p in (files[0],files[-1])],'youtubeUploaded':False,'humanReview':False}
(P/'production/full-video-delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print('FULL FILM RENDERED',t['duration'],flush=True)
