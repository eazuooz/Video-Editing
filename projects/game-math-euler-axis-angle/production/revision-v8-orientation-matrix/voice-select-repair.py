"""Explicit audio-agent selection of one reviewed m07L02 QA take, no script edit."""
from pathlib import Path
import argparse,copy,importlib.util,json,shutil
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_select_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_select_measure',H/'voice-render.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--review-reason',required=True);args=p.parse_args();plan=c.validate()
 lease=c.read(c.LEASE);assert lease['project']==c.P.name and lease['revision']=='orientation-matrix-v8'and lease['state']=='awaiting-manual-candidate-selection-models-unloaded'
 assert not(c.O/'repair-selection.json').exists();before=c.sha(c.O/'tts-current.json');source=c.read(c.O/'tts-current.json');selection=c.read(H/'voice-retake-input.json');assert selection['sourceReceiptSha256']==before
 candidates=c.read(c.O/'retake-candidates.json');candidate=next(x for x in candidates['candidates']if x['id']==args.candidate);assert candidate['scene']=='m07'and candidate['line']==2
 asrfile=c.O/'repair-asr'/(args.candidate+'.json');asr=c.read(asrfile);assert asr['audio_sha256']==candidate['sha256']and c.sha(c.R/candidate['file'])==candidate['sha256']
 old=next(x for x in source['scenes']if x['id']=='m07');assert old['lines'][1]['takeSha256']==candidate['originalTakeSha256'];new=copy.deepcopy(old)
 history=c.O/'history/before-m07-L02-repair';assert not history.exists();history.mkdir(parents=True);archives=[]
 for name in ['tts-current.json','line-levels.json','source-asr-review.json','source-alignment.json','source-level-review.json','voice-handoff.json','source-content-review.json','source-headroom.json']:
  path=c.O/name
  if path.exists():shutil.copy2(path,history/name);archives.append(dict(file=c.rel(path),preservedFile=c.rel(history/name),sha256=c.sha(path)))
 blocks=[];cursor=0;rate=24000;new_lines=[]
 for row in old['lines']:
  item=copy.deepcopy(row);gap=6720 if row['line']>1 else 0
  if gap:blocks.append(np.zeros(gap,np.float32));cursor+=gap
  if row['line']==2:
   item.update(takeFile=candidate['file'],takeSha256=candidate['sha256'],gainDb=candidate['gainDb'],before=candidate['before'],after=candidate['after'],
    processedFloatPeak=candidate['normalizedFloatPeak'],gainLimited=abs((-22-candidate['before']['speechFrameMedianDbfs'])-candidate['gainDb'])>1e-7,
    qaSelection=dict(candidate=candidate['id'],originalTakeFile=candidate['originalTake'],originalTakeSha256=candidate['originalTakeSha256'],seed=candidate['seed']))
   if candidate.get('pronunciationAlias'):item['qaSelection']['pronunciationAlias']=candidate['pronunciationAlias']
  raw,sr=sf.read(c.R/item['takeFile'],dtype='float32');assert sr==rate and c.sha(c.R/item['takeFile'])==item['takeSha256']
  processed=raw*np.float32(10**(item['gainDb']/20));item.update(startSample=cursor,endSample=cursor+len(processed),gapBeforeSamples=gap);new_lines.append(item);blocks.append(processed);cursor+=len(processed)
 x=np.concatenate(blocks);out=c.O/'repairs/m07.L02'/(candidate['id']+'.scene.wav');assert not out.exists();sf.write(out,x,rate,subtype='FLOAT');check,_=sf.read(out,dtype='float32');assert np.array_equal(x,check)
 new.update(file=c.rel(out),sha256=c.sha(out),samples=len(x),seconds=len(x)/rate,lines=new_lines,asrFile=c.rel(c.O/'repair-asr/m07.json'))
 source['scenes']=[new if s['id']=='m07'else s for s in source['scenes']];source['status']='source-complete-with-selected-m07-repair; changed-scene-ASR-pending'
 source['selectedRepair']=dict(scene='m07',line=2,candidate=candidate['id'],originalSourceReceiptSha256=before,originalSceneFile=old['file'],originalSceneSha256=old['sha256'],humanListening='pending')
 level=c.read(c.O/'line-levels.json');replace={r['line']:r for r in new_lines};current=[]
 for row in level['lines']:
  if row['scene']=='m07':
   r=replace[row['line']];row=dict(row,**{k:r[k]for k in ['takeFile','takeSha256','startSample','endSample','gapBeforeSamples','gainDb','before','after','processedFloatPeak','gainLimited']})
  current.append(row)
 level['lines']=current;level['maximumProcessedFloatPeak']=max(r['processedFloatPeak']for r in current);level['selectedRepair']=source['selectedRepair']
 c.save(c.O/'line-levels.json',level);c.save(c.O/'tts-current.json',source)
 record=dict(revision='orientation-matrix-v8',token=lease['token'],selectedCandidate=candidate['id'],sourceReceiptBeforeSha256=before,sourceReceiptSha256=c.sha(c.O/'tts-current.json'),
  sourceSceneBefore=dict(file=old['file'],sha256=old['sha256'],samples=old['samples']),sourceSceneAfter=dict(file=new['file'],sha256=new['sha256'],samples=new['samples']),
  sourceTextSha256=candidate['textSha256'],approvedScriptSha256=c.APPROVED,rawCandidatesFile=c.rel(c.O/'retake-candidates.json'),rawCandidatesSha256=c.sha(c.O/'retake-candidates.json'),
  candidateAsrFile=c.rel(asrfile),candidateAsrSha256=c.sha(asrfile),reviewReason=args.review_reason,selectedBy='Audio agent scoped QA decision; not human listening approval',
  archives=archives,originalRawTakesAndSceneAndAsrPreserved=True,unchangedSceneHashes=[dict(id=s['id'],sha256=s['sha256'])for s in source['scenes']if s['id']!='m07'],
  newSourceSpeed=1,completeParagraphConstantGainOnly=True,addedObservationSilenceSamples=0,humanListening='pending')
 c.save(c.O/'repair-selection.json',record);print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
