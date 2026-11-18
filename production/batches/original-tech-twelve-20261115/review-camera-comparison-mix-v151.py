"""Check changed music against exact approved speech, retaining raw ASR differences."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,statistics
import numpy as np,soundfile as sf
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 if p.exists():assert read(p)==d,p;return
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--record',action='store_true');a=ap.parse_args();slug=a.project
 assert slug in[x['slug']for x in read(H/'batch.json')['projects']]
 version=150 if slug=='shorts-mario64-lakitu-camera' else 144;base=M/slug/'camera-music-v139'/f'audio-mix-v{version}';mp=base/'audio-build.json';mix=read(mp)
 rp=Path(read(M/slug/'mixed-asr-v146/status.json')['review']['path']);r=read(rp);job=read(r['job']['path']);assert job['identity']['mixProof']==pin(mp)
 data,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);music,mr=sf.read(mix['musicStem']['path'],dtype='float32',always_2d=True);voice,vr=sf.read(mix['voice']['path'],dtype='float32',always_2d=True)
 assert rate==mr==vr==24000 and data.shape==music.shape==(mix['frames'],2)and len(voice)==len(data)
 assert pin(mix['mix']['path'])==mix['mix']and pin(mix['voice']['path'])==mix['voice']
 gain=mix['masterConstantGain']
 if slug=='shorts-mario64-lakitu-camera':
  prior=np.repeat(voice,2,axis=1);oldmusic=np.zeros_like(prior);word_reference=mix['sourceWordReference']
 else:
  old=read(mix['oldMix']['path']);prior,_=sf.read(old['mix']['path'],dtype='float32',always_2d=True);oldmusic,_=sf.read(old['musicStem']['path'],dtype='float32',always_2d=True);word_reference=mix['oldEncodedQa']
 retained=(prior-oldmusic)*gain;residual=float(np.max(np.abs(data-retained-music)));assert residual<3e-7,residual
 q=module('audible148_unchanged_level_math',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py');n=module('audible148_existing_spelling',H/'review-camera-comparison-voice-v147.py')
 paragraphs=[];joins=[];differences=[];flags=[];asr_window_diagnostics=[];source_words=[]
 for rec in r['results']:
  task=rec['task'];assert task['sha256']==mix['mix']['sha256']
  if task['kind']=='join':joins.append(dict(key=task['key'],recognized=rec['rawRecognition']['text'],rawRecord=pin(rp.parent/(task['key']+'.json'))));continue
  a0,b0=task['startSample'],task['endSample'];ws=[];invalid=[]
  for w in rec['rawRecognition']['chunks']:
   x,y=w['timestamp']
   if x is None or y is None or not 0<=x<y<=(b0-a0)/rate:invalid.append(w);continue
   lo,hi=q.sample_window(x,y,rate);lo+=a0;hi+=a0;vl=q.levels(voice[lo:hi]*gain,rate);ml=q.levels(music[lo:hi],rate);ratio=ml['rmsDbfs']-vl['rmsDbfs']
   ws.append(dict(text=w['text'],startSeconds=x,endSeconds=y,durationSeconds=y-x,levels=dict(voice=vl,mixed=q.levels(data[lo:hi],rate)),musicMinusVoiceDb=ratio))
   if ratio>q.POLICY['musicToVoiceRmsWarningDb']and y-x>=.08:asr_window_diagnostics.append(dict(kind='unadopted-new-ASR-window',paragraph=task['paragraph'],word=w,ratioDb=ratio))
  literal=n.norm(task['expected'],slug,task['paragraph'])==n.norm(rec['rawRecognition']['text'],slug,task['paragraph']);content=dict(paragraph=task['paragraph'],expected=task['expected'],recognized=rec['rawRecognition']['text'],literal=literal)
  if not literal:differences.append(content)
  paragraphs.append(dict(**content,words=ws,unusedInvalidAsrWords=invalid,voiceTrend=q.trend(ws,'voice'),mixedTrend=q.trend(ws,'mixed'),voiceWholeTake=q.levels(voice[a0:b0]*gain,rate)))
 # ASR timestamps from this louder mix do not replace the previously approved
 # captions. Report all text differences; never convert lexical differences
 # into aliases. Reused speech is proven separately by exact known-stem math.
 for w in read(word_reference['path'])['wordLevelWindows']:
  lo,hi=w['startSample'],w['endSample']
  if not 0<=lo<hi<=len(data):continue
  vl=q.levels(voice[lo:hi]*gain,rate);ml=q.levels(music[lo:hi],rate);ratio=ml['rmsDbfs']-vl['rmsDbfs'];source_words.append(dict(text=w['text'],startSample=lo,endSample=hi,musicMinusVoiceDb=ratio))
  if ratio>q.POLICY['musicToVoiceRmsWarningDb']and (hi-lo)/rate>=.08:flags.append(dict(kind='music-to-voice-approved-whole-word-ratio',word=w,ratioDb=ratio))
 assert source_words
 report=dict(mixProof=pin(mp),asrReview=pin(rp),knownStemMaximumResidual=residual,approvedVoicePcmPreserved=mix['voiceRawPcmUnchanged'],masterConstantGain=gain,narrationInternalEnvelopeChanged=False,paragraphs=paragraphs,asrTextDifferences=differences,joinTranscripts=joins,flags=flags,approvedSourceWordReference=word_reference,approvedSourceWordWindows=source_words,unadoptedNewAsrWindowDiagnostics=asr_window_diagnostics,wordBoundaryReuseReason='Speech PCM and timing are identical before one uniform master gain. Use previously approved whole-word extents rather than replacing them with different cropped ASR estimates from a new music mix.',newAsrWordsUsedAsCaptionAnchors=False,actualListening=False,humanApproval=False)
 save(base/'mixed-technical-review-v151.json',report)
 print(json.dumps(dict(project=slug,flags=flags,differences=differences,joins=joins,knownStemMaximumResidual=residual),ensure_ascii=False),flush=True)
 if a.record:
  peer=base/'mixed-peer-review-v151.json';p=read(peer);assert p['mixProof']==pin(mp)and p['asrReview']==pin(rp)and p['approvedForRemux']and not flags
  save(base/'mixed-content-review-v151.json',dict(approvedForRemux=True,mixProof=pin(mp),technicalReview=pin(base/'mixed-technical-review-v151.json'),peerReview=pin(peer),asrLiteralAll=not differences,asrDifferencesRetained=differences,speechContentEvidence='Exact accepted speech PCM retained; one constant master gain. New independent mixed ASR compared and its lexical differences retained, not aliased or used to alter captions.',actualListening=False,humanApproval=False))
if __name__=='__main__':main()
