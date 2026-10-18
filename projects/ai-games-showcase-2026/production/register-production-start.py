"""Link actual GPU and newly inspected FHD evidence to the existing records."""
from pathlib import Path
import json,hashlib,datetime,subprocess
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
coord=read(P/'production/local/compact-edit/tts-gpu-coordination.json')
media=read(P/'sources/media.json')
for name,game,url,role,credit in [('nightshoal-week11.mp4','nightshoal','https://www.reddit.com/r/ClaudeAI/comments/1x3ttzl/week_11_of_making_my_fishing_game_with_the_help/','independent-creator-gameplay','Nightshoal / ProFactor'),('emberfall-editor-1080.png','emberfall','https://broad-grass-ea4b.supportinfo-593.workers.dev/editor','direct-browser-screenshot','Emberfall / Luminati')]:
 f=R/'production/preflight/ai-games-showcase-2026/local'/name
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(f)]))['streams'][0]
 assert info['width']>=1920 and info['height']>=1080
 path=f.relative_to(R).as_posix();media['assets']=[x for x in media['assets'] if x['path']!=path]
 media['assets'].append(dict(game=game,path=path,sourceUrl=url,role=role,credit=credit,width=info['width'],height=info['height'],fps=info['r_frame_rate'],durationSeconds=float(info.get('duration',0)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),audioUse='excluded mixed source music; no voice/music reuse',review={'frames':'directly inspected; whole selected motion review pending'},rights={'basis':'Limited attributed excerpts for original game-specific commentary; no reusable license or permission claimed','publicReuseReview':'pending exact cut selection'}))
save(P/'sources/media.json',media)
k=read(P/'production/checkpoint.json');k.update(updatedAt=now,runningJob={'kind':'Qwen3 GPU scene batch','pid':coord['coordinator']['pid'],'log':'production/local/tts-current.log','memoryEvidence':'production/local/compact-edit/tts-gpu-coordination.json'},stage='GPU-voice-running-and-cut-preparation');k['completed'].append('Additional FHD Nightshoal week11 gameplay and separate FHD Emberfall editor capture inspected');save(P/'production/checkpoint.json',k)
p=read(P/'planning/production-plan.json');p['status']='voice-generation-and-measured-edit-preparation';p['stages']['tts']='GPU-running';p['audio']['gpu']['firstObservedPeakAllocatedMiB']=coord['generations'][0]['peakAllocatedMiB'];p['audio']['gpu']['firstObservedPeakReservedMiB']=coord['generations'][0]['peakReservedMiB'];save(P/'planning/production-plan.json',p)
paths=['projects/ai-games-showcase-2026/'+x for x in ['project.json','planning/production-plan.json','sources/media.json','production/checkpoint.json','production/tts-manifest.json','production/render-voice.py','production/record-gpu-authorization.py','production/register-production-start.py']]+['shared/publishing/video-production-control.json']
save(P/'production/local/commit-voice-start.json',{'message':'Start bounded GPU voice production after user confirmation and add FHD gameplay evidence','paths':paths})
