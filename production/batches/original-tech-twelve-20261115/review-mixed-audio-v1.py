"""Read actual per-paragraph stereo sample ranges; no model or audio changes."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,re
import numpy as np,soundfile as sf
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CONFIG={'shorts-oot-ninja-show-z-targeting':('audio-mix-v3','mixed-asr-v3','voice-edit-v3'),'shorts-mario64-lakitu-camera':('audio-mix-v5','mixed-asr-v5','voice-edit-v5'),'shorts-mariokart8-spin-boost':('audio-mix-v2','mixed-asr-v2','voice-sentence-v2')}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def norm(s):
 for x,y in [('육십사','64'),('에이트','8'),('씨','c'),('에이','a'),('비','b')]:s=s.lower().replace(x,y)
 return re.sub(r'[^0-9a-z가-힣]','',s.lower())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=CONFIG,required=True);p.add_argument('--record-content',action='store_true');a=p.parse_args();mixver,asrver,voicever=CONFIG[a.project];base=MEDIA/a.project;mp=base/mixver/'audio-build.json';mix=read(mp);rp=Path(read(base/asrver/'status.json')['review']['path']);review=read(rp);data,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);assert rate==24000 and data.shape==(mix['frames'],2)and np.max(np.abs(data))<1;spec=importlib.util.spec_from_file_location('unchanged_mixed_level_primitive',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);rows=[];flags=[];content=[]
 for r in review['results']:
  t=r['task']
  if t['kind']!='take':continue
  samples=data[t['startSample']:t['endSample']];words=[]
  for w in r['rawRecognition']['chunks']:
   x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=len(samples)/24000,(t['key'],w);i,j=q.sample_window(x,y,24000);words.append(dict(text=w['text'],startSeconds=x,endSeconds=y,durationSeconds=y-x,levels=dict(mixed=q.levels(samples[i:j],24000))))
  trend=q.trend(words,'mixed');rows.append(dict(paragraph=t['paragraph'],sourceSampleRange=[t['startSample'],t['endSample']],words=words,trend=trend,wholeTake=q.levels(samples,24000)));content.append(dict(paragraph=t['paragraph'],expected=t['expected'],recognized=r['rawRecognition']['text'],literalAfterOrthographicEquivalence=norm(t['expected'])==norm(r['rawRecognition']['text'])))
  if trend['suspect']:flags.append(dict(paragraph=t['paragraph'],trend=trend))
 assert not flags,flags
 report=base/mixver/'mixed-level-review-v1.json';save(report,dict(mixProof=pin(mp),asrReview=pin(rp),primitive=pin(ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py'),policy=q.POLICY,actualStereoMixSampleRanges=True,paragraphs=rows,flags=flags,actualListening=False,humanApproval=False))
 if a.record_content:
  assert all(x['literalAfterOrthographicEquivalence']for x in content),content
  target=base/mixver/'mixed-content-review.json';save(target,dict(approvedForPilot=True,mixProof=pin(mp),blindAsrReview=pin(rp),technicalVoiceReview=pin(base/voicever/'technical-voice-review.json'),mixedLevelReview=pin(report),reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewScope='Compared every complete mixed paragraph and every independent join with the approved source order. Full paragraphs match literally after punctuation/spacing and64/8/C/A/B spelling equivalence. No learning sentence omitted, inserted or reordered.',recognitionVariations=['Cropped join endpoints may end in a partial phrase; they are never used as new caption anchors.','The kart join at p003/p004 has 이말은 at the crop end, while the full p004 literally recognizes 이말이. The accepted voice and complete mixed paragraph agree.']if'kart'in a.project else['All new joins retain complete words around the actual paragraph boundary.'],musicToVoiceMaximumDb=max(x['musicMinusVoiceDb']for x in mix['wordWindows']),knownStemResidual=mix['knownStemResidual'],voiceGain=1,voiceInternalDsp=False,bodyOnly=True,actualListening=False,humanApproval=False,finalFilmComplete=False))
 print(json.dumps(dict(project=a.project,levelReview=pin(report),flags=[],content=content),ensure_ascii=False))
if __name__=='__main__':main()
