"""Measure actual final screen categories; never label still analysis as motion."""
from pathlib import Path
from collections import Counter
import argparse,json,os
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def key(p):return os.path.normcase(str((R/Path(p)).resolve()))
def measure(ep):
 edl=read(H/'local/explanation-assembly'/ep/'edl.json')
 mask=next(e for e in read(H/'renderer/game-baseline-ranges.json')['episodes']if e['id']==ep)
 manifest=H/'game-plates-caption-safe.json'
 if not manifest.exists():manifest=H/'game-plates-manifest.json'
 plates=next(e for e in read(manifest)['episodes']if e['id']==ep)['pictureEdits']
 corrections=H/'visual-corrections'/(ep+'.json')
 if corrections.exists():plates+=read(corrections)['pictureEdits']
 registry={key(q['picture']):q for q in plates+edl['pictureEdits']if'mediaSegments'in q or'mediaComposition'in q}
 def classify(file,start,count):
  out=Counter();q=registry.get(key(file))
  if key(file)==key(edl['baselinePicture']):
   remaining=count
   for m in mask['rows']:
    n=max(0,min(start+count,m['relationEnd'])-max(start,m['relationStart']))
    if n:out['retainedGameplayNative'if m.get('playbackSpeed',1)==1 else'retainedGameplaySlowAnalysis']+=n;remaining-=n
   out['diagramOrOtherExplanation']+=remaining;assert remaining>=0
  elif q and'mediaComposition'in q:
   c=q['mediaComposition'];cursor=0;limit=c['originalUnscaledFrames']
   for clip in c['clips']:
    n=min(clip['frames'],max(0,limit-cursor));a,b=max(start,cursor),min(start+count,cursor+n)
    if a<b:out.update(classify(clip['source'],clip['sourceStartFrame']+a-cursor,b-a))
    cursor+=n
    if cursor>=limit:break
   suffix=max(0,min(start+count,q['newFrames'])-max(start,limit));out['explicitStillAnalysis']+=suffix
  elif q and'mediaSegments'in q:
   occupied=0
   for s in q['mediaSegments']:
    n=max(0,min(start+count,s['offsetFrame']+s['frames'])-max(start,s['offsetFrame']));occupied+=n
    cat={'native-gameplay':'verifiedGameplayNative','still-analysis':'actualGameStillAnalysis'}.get(s['kind'],'authoredExplanation');out[cat]+=n
   out['authoredExplanation']+=count-occupied
  else:out['authoredExplanation']+=count
  assert sum(out.values())==count,(file,start,count,out);return out
 counts=Counter();bodyStart=120;bodyEnd=edl['frames']-600
 for r in edl['pictureEdl']:
  a,b=max(bodyStart,r['outputStartFrame']),min(bodyEnd,r['outputEndFrame'])
  if a<b:counts.update(classify(r['source'],r['sourceStartFrame']+a-r['outputStartFrame'],b-a))
 total=bodyEnd-bodyStart;assert sum(counts.values())==total
 moving=sum(counts[k]for k in ['verifiedGameplayNative','retainedGameplayNative','retainedGameplaySlowAnalysis'])
 report={'episode':ep,'basis':'Actual final EDL; branding2s/member10s excluded. Source-derived stills and self-authored UE/math are explanation. Retained explicitly requested slow-motion gameplay is reported separately.','bodyFrames':total,'framesByCategory':dict(counts),'secondsByCategory':{k:round(v/60,3)for k,v in counts.items()},'gameMotionSharePct':round(100*moving/total,3),'baselineGameMotionSharePct':round(100*mask['gameFrames']/(mask['relationTimelineFrames']-720),3),'default60ContractClaimed':False,'comparisonPriority':'Preserve the requested native observations, full teaching speech and simultaneous phase analysis; no unrelated footage or extra loops to fill a quota.','humanReviewed':False}
 folder=H/'picture-metrics';folder.mkdir(exist_ok=True);(folder/(ep+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--episode',required=True);a=ap.parse_args();print(json.dumps(measure(a.episode),ensure_ascii=False))
