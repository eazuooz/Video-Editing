"""Reuse existing independent context anchors; raw whole-source ASR untouched."""
from pathlib import Path
import importlib.util
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_context_timing',H/'voice-review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
def main():
 c.validate(preserve_pcm=True);current=c.read(c.O/'tts-current.json');pcm=c.read(c.O/'current-pcm.json');folder=c.O/'alignment-inputs';folder.mkdir(exist_ok=True);proof=[]
 for sid,name in [('v7-a05','a05-repetition'),('v7-a20','a20-repetition')]:
  row=next(x for x in current['scenes']if x['id']==sid);raw_file=c.O/'asr'/(sid+'.json');raw=c.read(raw_file);context_file=c.O/'contexts'/(name+'.json');context=c.read(context_file)
  assert raw['audio_sha256']==context['sourceSha256']==row['sha256']and c.sha(c.R/row['file'])==row['sha256']
  lo,hi=context['sourceRangeSeconds'];pad=context['recognitionOnlyLeadingTrailingPadSamples']/context['sourceSampleRate']
  words=[]
  for w in context['words']:
   begin,end=w['timestamp'];assert begin is not None and end is not None
   words.append(dict(text=w['text'],timestamp=[max(lo,begin-pad+lo),min(hi,end-pad+lo)]))
  # Whisper includes the leading recognition-only zero pad in its first-word
  # start. Reuse the same lexical word's original valid whole-source start.
  matches=[w for w in raw['words']if w['timestamp'][0]is not None and lo<=w['timestamp'][0]<lo+2 and r.normalized(w['text'])==r.normalized(words[0]['text'])]
  assert matches and words[0]['timestamp'][1]>matches[0]['timestamp'][0]
  words[0]['timestamp'][0]=matches[0]['timestamp'][0]
  prefix=[w for w in raw['words']if w['timestamp'][1]is not None and w['timestamp'][1]<=lo]
  suffix=[w for w in raw['words']if w['timestamp'][0]is not None and w['timestamp'][0]>=hi]
  joined=prefix+words+suffix;starts=[w['timestamp'][0]for w in joined]
  assert all(x<=y for x,y in zip(starts,starts[1:]))
  assert all(w['timestamp'][0]<=w['timestamp'][1]for w in joined)
  file=folder/(sid+'-context-word-anchors.json')
  c.save(file,dict(scene=sid,audio_sha256=row['sha256'],kind='Derived alignment-only word anchors; no model rerun or raw-ASR edit',text=' '.join(w['text'].strip()for w in joined),words=joined,wholeSourceAsrFile=c.rel(raw_file),wholeSourceAsrSha256=c.sha(raw_file),contextAsrFile=c.rel(context_file),contextAsrSha256=c.sha(context_file),contextRangeSeconds=[lo,hi],recognitionOnlyPadSubtractedSeconds=pad,firstWordStartEvidence=matches[0],sourcePcmChanged=False))
  row.update(alignmentAsrFile=c.rel(file),alignmentAsrSha256=c.sha(file));next(x for x in pcm['scenes']if x['id']==sid).update(alignmentAsrFile=c.rel(file),alignmentAsrSha256=c.sha(file))
  proof.append(dict(scene=sid,file=c.rel(file),sha256=c.sha(file),originalAsrFile=c.rel(raw_file),originalAsrSha256=c.sha(raw_file),contextFile=c.rel(context_file),contextSha256=c.sha(context_file),range=[lo,hi],sourcePcmSha256=row['sha256']))
 c.save(c.O/'tts-current.json',current);c.save(c.O/'current-pcm.json',pcm)
 c.save(folder/'context-anchor-review.json',dict(part=1,currentSourcesUnchanged=True,rawWholeAsrUnchanged=True,additionalInferenceCount=0,scenes=proof,reason='Existing independently decoded complete context replaces backward duplicate recognition spans only for character alignment.'))
 print('Existing independent context anchors bound for a05/a20; no ASR or PCM edits')
if __name__=='__main__':main()
