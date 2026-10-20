"""Select the directly compared a09 first-sentence repair; archive selectors."""
from pathlib import Path
import difflib,hashlib,importlib.util,json,shutil
import soundfile as sf
import numpy as np
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_select_review',H/'voice-review.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);c=v.c
def main():
 c.validate(preserve_pcm=True);folder=c.O/'repair-a09-attempt3';proof=c.read(folder/'repair-proof.json')
 pcm=c.R/proof['composedFile'];asr_file=folder/'composed-asr.json';asr=c.read(asr_file)
 assert c.sha(pcm)==proof['composedSha256']==asr['audio_sha256']
 assert v.normalized(asr['text']).startswith('지금까지쓴오일러각은')
 assert proof['unchangedTailByteEquivalent']and proof['warmupExcluded']and proof['productionSilenceAddedSamples']==0
 source=c.read(c.O/'tts-current.json');assert source['scenes'][8]['id']=='v7-a09'
 assert source['scenes'][8]['sha256']==proof['sourceSha256'],'Preserve an already selected/different repair'
 oldrow=source['scenes'][8];current=c.read(c.O/'current-pcm.json');review=c.read(c.O/'source-asr-review.json')
 archive=c.O/'history/pre-a09-repair';archive.mkdir(parents=True,exist_ok=True);archived=[]
 for name in ['tts-current.json','current-pcm.json','source-asr-review.json']:
  src=c.O/name;dst=archive/name;assert not dst.exists();shutil.copy2(src,dst);assert c.sha(src)==c.sha(dst)
  archived.append(dict(file=c.rel(dst),sha256=c.sha(dst)))
 x,rate=sf.read(pcm,dtype='float32');row=dict(oldrow)
 for k in ['rawFloatPeak','rawOutOfPcm16RangeCount','peakAllocatedMiB','peakReservedMiB','elapsedSeconds','generatedAt']:row.pop(k,None)
 row.update(file=c.rel(pcm),sha256=c.sha(pcm),samples=len(x),seconds=len(x)/rate,sampleRate=rate,
  asrFile=c.rel(asr_file),asrSha256=c.sha(asr_file),encodedHardClipSampleCount=int(np.sum(abs(x)>=32766/32768)),
  currentPcmPeak=float(np.max(abs(x))),currentDerivation='Only approved first sentence repaired; original second sentence through ending is sample-exact.',
  repairProofFile=c.rel(folder/'repair-proof.json'),repairProofSha256=c.sha(folder/'repair-proof.json'),
  originalSynthesisRecord=oldrow,contentReview='Direct complete current text compared; human listening pending',humanListening='pending')
 source['scenes'][8]=row;current['scenes'][8]=row
 for obj in [source,current]:
  obj['selectedOpeningRepair']=dict(scene='v7-a09',proof=row['repairProofFile'],proofSha256=row['repairProofSha256'],originalSelectors=archived,wholeSceneRerendered=False,unchangedSourceFilesPreserved=True)
 expected=' '.join(c.read(H/'voice-input.json')['scenes'][8]['lines']);a,b=v.normalized(expected),v.normalized(asr['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
 review['scenes'][8]=dict(scene='v7-a09',audioFile=row['file'],audioSha256=row['sha256'],asrFile=c.rel(asr_file),asrSha256=c.sha(asr_file),expected=expected,recognized=asr['text'],similarity=m.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l])for t,i,j,k,l in m.get_opcodes()if t!='equal'],directFullTextReview='Directly compared all five approved paragraphs; repaired opening present; complete content and numbers retained.',humanListening='pending')
 review['selectedOpeningRepair']=source['selectedOpeningRepair']
 c.save(c.O/'tts-current.json',source);c.save(c.O/'current-pcm.json',current);c.save(c.O/'source-asr-review.json',review)
 c.save(folder/'selection.json',dict(selected=True,scopedPart=1,source=c.rel(pcm),sha256=c.sha(pcm),asrFile=c.rel(asr_file),asrSha256=c.sha(asr_file),originalSourcePcmUntouched=True,history=archived,allFiveCurrentParagraphsDirectlyCompared=True,voiceReferenceUnchanged=True,addedSilenceSamples=0,humanListening='pending'))
 print(json.dumps(dict(scene='v7-a09',seconds=row['seconds'],unchangedTailSamples=proof['unchangedTailSamples'],newSourceRawTotalSeconds=sum(s['seconds']for s in source['scenes']))))
if __name__=='__main__':main()
