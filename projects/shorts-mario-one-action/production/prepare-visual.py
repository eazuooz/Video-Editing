"""Build the current voice-led edit and finite native-speed source frame caches."""
from pathlib import Path
import json,hashlib,subprocess,argparse
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local'
FF='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=['plan','frames','gameframes','traces']);args=a.parse_args()
 control=read(R/'shared/publishing/video-production-control.json');assert control.get('selectedShortVideo')==P.name and control.get('shortsDirectSelection',{}).get('selectedRevision')=='one-action-v1'
 c=read(P/'script/captions.json');cue={x['id']:x for x in c['cues']};at=lambda x:cue[x]['start'];end=c['durationSeconds']
 sources={'coin':dict(path='shared/output/play-first/media-cache/archive64-odyssey-p1-250-282.mp4',originalOffsetSeconds=0),'chain':dict(path='shared/output/play-first/media-cache/archive64-odyssey-p2-110-135.mp4',originalOffsetSeconds=0),'dino':dict(path='shared/output/play-first/media-cache/archive64-odyssey-p2-715-762.mp4',originalOffsetSeconds=0)}
 game=lambda id,start,end,key,source,label:dict(id=id,kind='game',start=start,end=end,source=key,sourceStart=source,sourceEnd=source+end-start,rate=1,label=label)
 demo=lambda id,start,end,state,label:dict(id=id,kind='explanation',start=start,end=end,state=state,sourceStart=0,sourceEnd=end-start,rate=1,label=label)
 sections=[game('hook',0,at('c03'),'dino',24,'모자로 공룡을 조종한다?'),demo('familiar-input',at('c03'),at('c05'),'reward','처음에는 익숙한 던지기'),game('coin-result',at('c05'),at('c08'),'coin',11.7,'던진 모자에 주변이 반응'),game('chain-first',at('c08'),at('c11'),'chain',0,'같은 던지기 → 다른 몸'),game('chain-definition',at('c11'),at('c13'),'chain',9,'캡처 (Capture) · 몸과 능력 빌리기'),demo('same-input',at('c13'),at('c15'),'reward','버튼도 던지기도 그대로'),demo('new-target',at('c15'),at('c18'),'capture','달라진 것은 맞는 대상'),game('new-controls',at('c18'),at('c22'),'dino',30,'캡처 뒤의 조작은 따로 익힌다'),dict(id='closing',kind='explanation',start=at('c22'),end=37.4,state='closing',sourceStart=0,sourceEnd=2,rate=1,label='익숙한 행동 → 새로운 능력'),game('final-result',37.4,end,'dino',43.5,'새 능력도 익숙한 행동에서 출발')]
 assert abs(sections[0]['start'])<1e-8 and abs(sections[-1]['end']-end)<1e-8
 for x,y in zip(sections,sections[1:]):assert abs(x['end']-y['start'])<1e-8
 for s in sections:assert s['end']>s['start'] and (s['kind']=='game' or s['end']-s['start']<=6.5)
 reactions=[dict(start=1.85,end=3.25,kind='puzzled'),dict(start=26.6,end=28.2,kind='realize'),dict(start=38.15,end=39.65,kind='understood')]
 # Wide short-lived region around the directly inspected coin emergence.
 annotations=[dict(section='coin-result',start=14.0-11.7,end=15.2-11.7,width=250,height=185,label='초록 원: 코인이 나오는 곳',anchors=[[14.0-11.7,940,500],[15.2-11.7,940,500]],meaning='Editorial coin emergence region; no count,hitbox or detector measurement')]
 result=dict(schemaVersion=1,revision='one-action-v1',fps=60,frames=c['frames'],durationSeconds=end,captionSha256=sha(P/'script/captions.json'),voiceOffsetSeconds=.2,sourceTimeBasis='clip-relative',sources=sources,sections=sections,reactions=reactions,annotations=annotations,traces={},controlPromptCue=dict(start=at('c20'),end=at('c22'),sourceRegion=[570,860,780,180],text='이동·돌진 / 공격'),implementation=dict(project='unity/VideoEditing',engine='6000.6.0f1',pipeline='built-in custom unlit surface',capture='1080x1080/60fps',analogy='Own implementation, not Mario engine code',inputSequence='Space pulse at frame50; same Horizontal=1 frames180..299,0otherwise; controlled transform routes input',query='Physics.SphereCastAll matching selected collider',variablesHeld='caster,input,launch point,projectile speed/radius/path,camera,stage',changedVariable='target type and its response'),actualFrames=sum(round((s['end']-s['start'])*60) for s in sections if s['kind']=='game'))
 canonical=P/'production/visual-timing.json'
 if canonical.exists():
  old=read(canonical);result['traces']=old.get('traces',{})
  assert [{k:v for k,v in s.items()} for s in old['sections']]==sections,'Preserve previous timing before revision'
 if args.command=='traces':
  result['traces']={kind:read(L/'capture-full-v2'/f'{kind}-trace.json') for kind in ['reward','capture']}
 save(canonical,result);save(L/'visual-timing.json',result)
 if args.command in ['frames','gameframes']:
  for s in sections:
   if s.get('state')=='closing' or (args.command=='gameframes' and s['kind']!='game'):continue
   dest=L/'frames'/s['id'];dest.mkdir(parents=True,exist_ok=True);count=round((s['end']-s['start'])*60)
   existing=list(dest.glob('frame-*.jpg'))
   if len(existing)==count:continue
   assert not existing,'Inspect partial cache '+s['id']
   source=(R/sources[s['source']]['path']) if s['kind']=='game' else L/'capture-full-v2'/(s['state']+'.mp4')
   subprocess.run([FF,'-v','error','-n','-ss',str(s['sourceStart']),'-i',str(source),'-an','-vf','fps=60','-frames:v',str(count),'-q:v','3','-start_number','0',str(dest/'frame-%04d.jpg')],check=True)
   assert len(list(dest.glob('frame-*.jpg')))==count
   print(s['id'],count,flush=True)
  # Closing uses two persistent results from the same camera rather than rerendering a staged scene.
  for kind in ([] if args.command=='gameframes' else ['reward','capture']):
   dest=L/'frames'/f'closing-{kind}.jpg'
   if not dest.exists():subprocess.run([FF,'-v','error','-n','-ss','4.9','-i',str(L/'capture-full-v2'/(kind+'.mp4')),'-frames:v','1','-q:v','2',str(dest)],check=True)
 print(json.dumps(dict(command=args.command,frames=c['frames'],actualFrames=result['actualFrames'],explanationFrames=c['frames']-result['actualFrames'],sections=[{k:s[k] for k in ['id','kind','start','end']} for s in sections]),ensure_ascii=False))
if __name__=='__main__':main()
