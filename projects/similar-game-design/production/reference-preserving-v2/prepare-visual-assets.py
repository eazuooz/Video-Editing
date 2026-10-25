"""Extract exact independently sourced stills and a planned caption-layout sample."""
from pathlib import Path
from storage_paths import local_output, relative, logical_path
import hashlib, importlib.util, json, subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/similar-game-design';HERE=Path(__file__).parent;LOCAL=P/'production/local/reference-preserving-v2';ASSETS=local_output(LOCAL/'edit/visual-assets');ASSETS.mkdir(parents=True,exist_ok=True)
sources=json.loads((P/'sources/footage-options-v2.json').read_text('utf-8-sig'))['sources'];byid={s['id']:s for s in sources};samples=[('drgs','drgs-scout',11.4),('mm2','maker2-world',18.5),('social','maker2-versus',7.1)];records=[];paths={}
for key,sid,t in samples:
 s=byid[sid];num,den=s['decoded']['fps'].split('/');fps=float(num)/float(den);n=round(t*fps);out=ASSETS/(key+'.png')
 if not out.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-i',str(R/s['localPath']),'-vf',f"select='eq(n,{n})'",'-frames:v','1','-fps_mode','vfr',str(out)],check=True)
 paths[key]='/@fs/'+str(logical_path(out)).replace('\\','/');records.append({'key':key,'path':relative(out),'source':sid,'sourceSha256':s['sha256'],'sourceFrame':n,'sourceTime':n/fps,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'use':'Independent gameplay screenshot inside explanation; explanation time, not actual moving gameplay.'})
(HERE/'visual-assets.json').write_bytes((json.dumps({'assets':records,'sourceMediaPreserved':True,'sourceLectureImagesUsed':False},ensure_ascii=False,indent=2)+'\n').encode('utf8'))
mc=R/'motion-canvas/src/projects/similar-game-design/revision-v2';f=mc/'preflight-scene.tsx';t=f.read_text('utf-8-sig')
if 'imagePaths:' not in t:t=t.replace('preflight: true}', 'preflight: true, imagePaths: '+json.dumps(paths,ensure_ascii=False)+'}');f.write_bytes(t.encode('utf8'))
f=mc/'production-project.ts'
if not f.exists():f.write_bytes(b"// Internal preflight placeholder. Replaced by the measured edit builder before production export.\nexport {default} from './preflight-project';\n")
spec=importlib.util.spec_from_file_location('d22_captions',HERE/'caption_pipeline.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
font=cap.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),500);bold=cap.measured_font(Path('C:/Windows/Fonts/NotoSansKR-VF.ttf'),700)
u=json.loads((HERE/'caption-units.json').read_text('utf-8-sig'));paragraphs=u['paragraphs'];ids=['01-p02','03-p02','04-p02','05-p03','06-p03','08-p03','07-p02','09-p03','10-p03'];content=cap.ass_header('Noto Sans KR');rows=[]
for i,pid in enumerate(ids):
 raw_unit=max(paragraphs[pid]['captionUnits'],key=lambda x:len(x['ko']));unit=cap.partition_pair(raw_unit['ko'],raw_unit['en'],font,[raw_unit])[0];emphasis=unit.get('emphasis',{'ko':None,'en':None});row={'cue':i+1,'start':i*4+.1,'end':i*4+3.95,'ko':unit['ko'],'en':unit['en'],'emphasis':emphasis};g=cap.geometry(row['ko'],font,bold,emphasis.get('ko'));content+=cap.ass_events(row,g);rows.append({'paragraph':pid,'plannedStart':row['start'],'plannedEnd':row['end'],'text':row['ko'],'geometry':g})
review=local_output(LOCAL/'edit/review');review.mkdir(exist_ok=True);(review/'preflight-captions.ass').write_bytes(content.encode('utf8'));(review/'preflight-captions.json').write_bytes((json.dumps({'status':'planned-layout-test-only-not-final-speech-alignment','rows':rows},ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'screenshots':len(records),'plannedCaptionSamples':len(rows),'productionProject':'preflight-placeholder-until-measured-edit'},ensure_ascii=False))
