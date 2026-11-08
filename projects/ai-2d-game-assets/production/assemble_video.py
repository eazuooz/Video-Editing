from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';F=L/'final';F.mkdir(exist_ok=True)
def run(args):subprocess.run([str(x) for x in args],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def read(p):return json.loads(p.read_text('utf-8-sig'))
control=read(R/'shared/publishing/video-production-control.json');assert control['scopedProductionAuthorizations'][P.name]['fullProductionAuthorized']
timing=read(L/'timeline.json');files=[P/'assets/local/intro.mp4']+[L/'visual'/f"scene-{r['id']}.mp4" for r in timing['scenes']]+[P/'assets/local/outro.mp4']
assert len(files)==32 and all(p.exists() for p in files)
for row in timing['scenes']:
 rec=read(L/'visual'/f"scene-{row['id']}.mp4.json");assert rec['frames']==row['frames']
concat=L/'concat.txt';concat.write_text('\n'.join("file '"+p.as_posix().replace("'","'\\''")+"'" for p in files)+'\n','utf-8')
clean=F/(P.name+'.clean.mp4');captioned=F/(P.name+'.captioned.mp4')
if not clean.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',concat,'-i',L/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-shortest',clean])
if not captioned.exists():
 # Workdir-relative filter path avoids Windows drive-colon parsing in libass.
 ass=(L/'captions.ko.ass').relative_to(R).as_posix()
 run(['ffmpeg','-hide_banner','-loglevel','error','-i',clean,'-vf',f"ass='{ass}'",'-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-c:a','copy','-movflags','+faststart',captioned])
manifest=read(P/'project.json')
manifest['paths'].update(videoClean=clean.relative_to(R).as_posix(),videoBurnedCaptions=captioned.relative_to(R).as_posix(),captionsKo=(L/'captions.ko.srt').relative_to(R).as_posix(),captionsEn=(L/'captions.en.srt').relative_to(R).as_posix(),audioMix=(L/'final-mix.m4a').relative_to(R).as_posix())
for unused in ('motionCanvasProject','manimProject','publishingKo','publishingEn'):manifest['paths'].pop(unused,None)
manifest['paths'].update(sceneRenderer=(P/'production/render-scenes.cjs').relative_to(R).as_posix(),audioReport=(P/'production/audio-qa.json').relative_to(R).as_posix())
manifest['membershipOutro']['appliedToFinal']=True
manifest['publishReady']=False
manifest['finalRender']={'knownIssues':[],'openItems':['사용자의 전체 영상·발음·속도 최종 검수 대기']}
manifest['delivery']={'localStorageRoot':(L/'delivery').relative_to(R).as_posix()};manifest['video']['durationSeconds']=timing['duration'];manifest['status']='internal-qa'
(P/'project.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Assembled',timing['duration'],'seconds',flush=True)
