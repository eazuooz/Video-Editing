"""Bind paired, editor-reviewed translations and explicit source/study choices to the inherited lesson."""
from pathlib import Path
import json,sys,re
B=Path(__file__).resolve().parent;R=B.parents[2];ep=sys.argv[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
row=next(x for x in read(R/'shared/publishing/video-worklist.json')['rows'] if x['id']==ep)
P=R/'projects'/row['slug'];H=P/'production/series-v1';cfg=read(H/'lesson.json')
draft=read(B/'scripts'/ep/'narration.ko.json');catalog=read(B/'footage-catalog.json')
english=[p.splitlines() for p in (H/'translation.en.txt').read_text('utf-8-sig').strip().split('\n\n')]
assert len(english)==len(draft['scenes'])==len(cfg['chapters'])
allgroups=[];shots=[];seen=set();original_number=0;bound_number=0;cue_map={}
for i,(s,en,design) in enumerate(zip(draft['scenes'],english,cfg['chapters']),1):
 ko=[t.strip() for l in s['lines'] for t in re.split(r'(?<=[.!?])\s+',l) if t.strip()]
 assert len(ko)==len(en),(ep,i,len(ko),len(en))
 for j,text in enumerate(ko):
  code=f'{i}.{j+1}';ko[j]=cfg.get('revisedKo',{}).get(code,text)
 mapping=design['visuals'].split()
 assert len(mapping)==len(ko),(ep,i,len(mapping),len(ko))
 cards=[];pairs=[]
 for j,base in enumerate(mapping):
  original_number+=1;bound_number+=1;cue_map[original_number]=bound_number
  items=[(ko[j],en[j],base,design['focus'])]
  additions=cfg.get('insertions',{}).get(f'{i}.{j+1}',[])
  items.extend((z['ko'],z['en'],z['visual'],z['focus']) for z in additions)
  bound_number+=len(additions)
  for ko_text,en_text,token,focus in items:
   pairs.append(ko_text+' | '+en_text)
   if token.startswith('@'):
    key=token[1:];assert key in cfg['studies'];args=[key,0,focus]
   else:
    key,at=token.split(':');assert key in catalog;seen.add(key);args=[key,float(at),focus]
   cards.append(args)
 allgroups.append('\n'.join(pairs))
 shots.append(cards)
(H/'narration-pairs.txt').write_text('\n\n'.join(allgroups)+'\n',encoding='utf-8')
selection={'episode':ep,'reference':draft['sourceMap'],'referenceRole':'research only','teachingOrder':[s['title'] for s in draft['scenes']], 'editorialNotes':cfg['editorialNotes'],'examples':{k:catalog[k] for k in sorted(seen)},'renderer':cfg['renderer'],'nintendoExamples':cfg['nintendo'],'previousEpisode':cfg['previousEpisode'],'platform':'local review only'}
(H/'source-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan={'rigs':list(cfg['studies']),'gameFiles':{key:catalog[key]['file'] for key in sorted(seen)},'gameTitles':{key:catalog[key]['title'] for key in sorted(seen)},'shots':shots,'studyLabels':cfg['studies'],'studyObservationFrames':cfg['observationFrames'],'sources':[catalog[k]['credit'] for k in sorted(seen)]+cfg['sourceCredits']+['Nimbus — Eveningland · YouTube Audio Library — https://www.youtube.com/audiolibrary']}
for key in ['flexibleCuts','pronunciationAliases','studyBasePlayback','gameCallouts','originalAspect1440p','rendererLabel']:
 if key in cfg:plan[key]=cfg[key]
if 'flexibleCuts' in plan:
 plan['flexibleCuts']=[dict(x,cue=cue_map[x['cue']]) for x in plan['flexibleCuts']]
(H/'visual-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from prepare_selected_episode import prepare
prepare(ep)
