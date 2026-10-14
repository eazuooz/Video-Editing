"""Corroborate current mixed ASR and original placement, without a listening claim."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,psutil
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('MKL_NUM_THREADS','2')
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
settings=read(P/'part1-final-mix-settings-v242.json');PP=P/'part1-final-input-plan-v240.json';plan=read(PP)
mix=ROOT/settings['wav'];assert sha(mix)==settings['wavSha256'] and sha(PP)==settings['planSha256']
states=[read(P/'part1-final-mixed-asr-execution-v243.json'),read(P/'part1-artifact-context-execution-v255.json')]
assert all(s['status']=='complete' and s['exitCode']==0 for s in states) and len(states[0]['results'])==30
for s in states:
 w=s['worker']
 if psutil.pid_exists(w['pid']):assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01,'Actual ASR worker still alive'
proofPath=P/'part1-final-pcm-preservation-v242.json';proof=read(proofPath)
assert sha(proofPath)==settings['pcmProofSha256'] and proof['planSha256']==sha(PP)
voicePath=ROOT/proof['path'];assert sha(voicePath)==proof['sha256']==settings['voiceSha256']
voice,sr=sf.read(voicePath,dtype='float32')
assert sr==24000 and voice.ndim==1 and len(voice)==proof['samples']==plan['finalFrames']*400
placements=[];hashes={};originalRanges=[]
originalSha='5b2464f1ade841fa1f3207fd8f80b06035c8d5602915f184a3c1fce15efe74dd'
for p in proof['placements']:
 source=ROOT/p['source']['path']
 if p['source']['path'] not in hashes:hashes[p['source']['path']]=sha(source)
 assert hashes[p['source']['path']]==p['source']['sha256']
 lo,hi=p['samples']
 with sf.SoundFile(source) as f:
  assert f.samplerate==24000 and f.channels==1;f.seek(lo);data=f.read(hi-lo,dtype='float32')
 begin=p['fromFrame']*400;end=begin+p['frames']*400
 assert len(data)==hi-lo and np.array_equal(voice[begin:begin+len(data)],data)
 assert end-begin-len(data)==p['paddingSamples'] and np.count_nonzero(voice[begin+len(data):end])==0
 placements.append({'id':p['id'],'sourceSha256':p['source']['sha256'],'sampleRange':p['samples'],'fromFrame':p['fromFrame'],'sourceValuesExact':True,'paddingOnlySilence':True})
 if p['source']['sha256']==originalSha:originalRanges.append(p['samples'])
assert originalRanges[0][0]==0 and originalRanges[-1][1]==13144320
assert all(a[1]==b[0] for a,b in zip(originalRanges,originalRanges[1:])) and sum(b-a for a,b in originalRanges)==13144320
assert np.count_nonzero(voice[:120*400])==np.count_nonzero(voice[-600*400:])==0
del voice
groups=[]
for s in states:
 windows=[]
 for done in s['results']:
  resultPath=ROOT/done['path'];assert sha(resultPath)==done['sha256'];r=read(resultPath);w=r['window']
  assert r['mixSha256']==settings['wavSha256'] and r['planSha256']==sha(PP) and not r['expectedTextUsedAsPrompt']
  wav=resultPath.with_suffix('.wav');assert sha(wav)==r['windowSha256']
  actual,sr=sf.read(wav,dtype='float32')
  with sf.SoundFile(mix) as f:
   assert f.samplerate==48000 and f.channels==2;f.seek(w['fromFrame']*800)
   expected=f.read((w['toFrame']-w['fromFrame'])*800,dtype='float32',always_2d=True).mean(axis=1)
  assert sr==48000 and len(actual)==r['sourceSamples'] and np.array_equal(actual,expected)
  reversals=[{'previous':r['words'][i-1],'current':q} for i,q in enumerate(r['words']) if i and q['timestamp'][0] is not None and r['words'][i-1]['timestamp'][0] is not None and q['timestamp'][0]<r['words'][i-1]['timestamp'][0]]
  windows.append({'label':done['label'],'resultSha256':done['sha256'],'windowSha256':r['windowSha256'],'fromFrame':w['fromFrame'],'toFrame':w['toFrame'],'allCurrentMixedSampleValuesExact':True,'timestampReversals':reversals})
 groups.append(windows)
record={'verifiedAt':datetime.now(timezone.utc).isoformat(),'currentMixSha256':settings['wavSha256'],'planSha256':sha(PP),
 'pcmPlacementProofSha256':sha(proofPath),'voiceSha256':proof['sha256'],'placements':placements,'sourceHashes':hashes,'originalSelectedSamples':13144320,
 'mainWindows':groups[0],'additionalWindows':groups[1],'additionalWindowCount':len(groups[1]),
 'allOriginalChapterSamplesPartitionedOnce':True,'allSelectedPcmValuesExact':True,'all30RecognitionWindowsCurrentMixExact':True,'allAdditionalArtifactContextsCurrentMixExact':True,
 'automaticContentApproval':False,'finalMixedAsrApproved':False,'allFinalPixelsReviewed':False,'humanWholeListening':'pending','humanPronunciation':'pending','newAudio':0,'newGitImages':0}
dest=P/'part1-final-mixed-pcm-corroboration-v254.json';assert not dest.exists(),'Preserve completed proof'
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'placements':len(placements),'mainWindows':len(groups[0]),'additionalWindows':len(groups[1]),'exactPcm':True,'languageApproved':False}))
