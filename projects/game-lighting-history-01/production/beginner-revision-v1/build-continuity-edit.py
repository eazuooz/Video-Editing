"""Preserve the measured visual cut; fit new speech at natural adjacent pauses."""
import copy,datetime,hashlib,json,math,pathlib,runpy
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;B=P/'production/local/beginner-revision-v1';O=P/'production/local/continuity-v2'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 runpy.run_path(str(H/'production-authority.py'))['require_selected_production']()
 d=rd(H/'current-policy-changes.json');a=rd(O/'alignment-proposal.json');assert not a['issues']
 base=rd(B/'plan.json');plan=copy.deepcopy(base);replacements={r['key']:r for r in a['rows']};old={v['key']:v for v in base['voice']};by={v['key']:v for v in plan['voice']}
 assert all(sum(v['key']==k for v in base['voice'])==1 for k in replacements)
 for key,r in replacements.items():
  v=by[key];v.update(kind='continuity-replacement',path=r['audioPath'],audioSha256=r['audioSha256'],sourceStartSample=0,utteranceStartSample=0,samples=r['samples'],frames=math.ceil(r['samples']/400))
 moves=[];gap=6
 for pair in d['pairs']:
  k1,k2=[r['key'] for r in pair['rows']];v1,v2=by[k1],by[k2];idx=plan['voice'].index(v1);idx2=plan['voice'].index(v2)
  assert idx2==idx+1
  prev=plan['voice'][idx-1];nxt=plan['voice'][idx2+1];prev_end=math.ceil((prev['targetStartSample']+prev['samples'])/400)
  s2=min(old[k2]['startFrame'],nxt['startFrame']-gap-v2['frames']);s1=min(old[k1]['startFrame'],s2-gap-v1['frames'])
  if s1<prev_end+gap:
   s1=max(old[k1]['startFrame'],prev_end+gap);s2=max(old[k2]['startFrame'],s1+v1['frames']+gap)
  v1['startFrame']=s1;v2['startFrame']=s2
  v1['targetStartSample']=s1*400;v2['targetStartSample']=s2*400
  end=s2+v2['frames']+gap
  j=idx2+1
  while end>plan['voice'][j]['startFrame']:
   v=plan['voice'][j];shift=end-v['startFrame'];assert shift<=120 and v['key'] not in replacements,(v['key'],shift)
   v['startFrame']+=shift;v['targetStartSample']+=shift*400
   moves.append(dict(key=v['key'],shiftFrames=shift,reason='Preserved PCM moved within its existing relevant demonstration, after complete new speech.'))
   end=math.ceil((v['targetStartSample']+v['samples'])/400)+gap;j+=1
  pair['realizedBoundary']=dict(firstKey=k1,secondKey=k2,firstStartFrame=s1,secondStartFrame=s2,firstShiftFrames=s1-old[k1]['startFrame'],secondShiftFrames=s2-old[k2]['startFrame'],visualBoundaryFrame=old[k2]['startFrame'],audioOverlap=False,speedChanged=False,carry=pair['carryVisual'])
 assert all(v['targetStartSample']+v['samples']<=w['targetStartSample'] for v,w in zip(plan['voice'],plan['voice'][1:])), 'No voice overlap.'
 render=rd(O/'scenes/execution.json');assets={x['key']:x for x in render['completed']};assert set(assets)=={'02-p4','09-p9','09a-p5'}
 timing=rd(O/'scenes-timing-fix/execution.json');assert [x['key'] for x in timing['completed']]==['02-p4'];assets['02-p4']=timing['completed'][0]
 for n in plan['nodes']:
  if n.get('anchor') in assets and n['role']=='explanation':
   asset=assets[n['anchor']];assert asset['frames']==n['frames'];n.update(path=asset['path'],framedPath=asset['path'],sourceStartFrame=0,framedStartFrame=0,sha256=asset['sha256'],policyUiRevision=True)
 plan.update(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),revision='continuity-v2',baselinePlan=(B/'plan.json').relative_to(R).as_posix(),baselinePlanSha256=sha(B/'plan.json'),retainedVoiceKeys=sorted(set(old)-set(replacements)),replacedVoiceKeys=sorted(replacements),finalTimingApproved=False,allFinalPixelsApproved=False,finalMixAsrApproved=False,finalPairComplete=False,continuity=dict(timeStretch=False,visualTimingChanged=False,pairedBoundaries=[p['realizedBoundary'] for p in d['pairs']],retainedPcmMoves=moves,sourcePcmPreserved=True))
 assert plan['frames']==145768 and abs(plan['actualFrames']-.6*plan['bodyFrames'])<=1
 wr(O/'plan-proposal.json',plan);wr(H/'current-policy-changes.json',d)
 print(json.dumps(dict(frames=plan['frames'],seconds=plan['seconds'],changedVoices=14,retainedVoiceKeys=len(plan['retainedVoiceKeys']),moves=moves,boundaries=plan['continuity']['pairedBoundaries']),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
