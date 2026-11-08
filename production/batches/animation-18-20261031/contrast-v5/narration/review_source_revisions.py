"""Print changed passages with unchanged neighbors for model semantic review.
Does not modify baseline scripts, PCM, revisions.json or source ledgers.
"""
from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[5]
B=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text('utf8'))
M={x['id']:x for x in read(B/'script-migration-plan.json')['records']}
P={}
for file,team in [(B/'footage/passage-proposals.json','a'),(B/'footage/team-b/passage-proposals.json','b')]:
 for ep in read(file)['episodes']:
  eid=ep.get('episode',ep.get('id'));x=P.setdefault(eid,{'changes':{},'sourceProposals':[]})
  x['sourceProposals'].append({'file':str(file.relative_to(ROOT)),'episode':ep})
  for c in ep['changes']:
   sid=c.get('baselineSentenceId',c.get('id'));x['changes'][sid]={**c,'id':sid,'team':team}
for ep in read(B/'narration/revisions.json')['episodes']:
 for c in ep['changes']:P[ep['id']]['changes'][c['id']]={**c,'team':'existing-root','existingApproved':True}
def baseline(eid,lang):
 path=ROOT/M[eid]['baselineKo'].replace('.ko.','.'+lang+'.')
 return read(path)['scenes']
if __name__=='__main__':
 for eid in sys.argv[1:]:
  e=P[eid];ko=baseline(eid,'ko');en={x['id']:x for x in baseline(eid,'en')}
  print('\n##',eid,M[eid]['slug'])
  wanted={i+j for i,x in enumerate(ko) if x['id'] in e['changes'] for j in [-1,0,1]}
  for i,s in enumerate(ko):
   if i not in wanted:continue
   c=e['changes'].get(s['id']);en0=' '.join(en[s['id']]['lines'])
   if c:
    print(s['id'],'OLD',' '.join(s['lines']));print('NEW',c['ko']);print('EN0',en0);print('EN+',c['en'])
   else:print(s['id'],' '.join(s['lines']),' | ',en0)
  if not e['changes']:print('No proposed spoken changes; current baseline preserved.')
