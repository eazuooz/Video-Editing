"""Review real stereo paragraph ranges and preserve unprompted join transcripts."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,statistics
import numpy as np,soundfile as sf
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--record-content',action='store_true');a=p.parse_args();assert a.project in[x['slug']for x in read(HERE/'batch.json')['projects']];P=ROOT/'projects'/a.project;new=(P/'production/accepted-voice-selection-v27.json').exists();selected=read(P/('production/accepted-voice-selection-v27.json'if new else'production/accepted-voice-selection-v10.json'));mp=ROOT/'shared/output/original-tech-twelve-20261115'/P.name/('audio-mix-v27/audio-build.json'if new else'audio-mix-v13/audio-build.json'if'inside'in P.name else'audio-mix-v10/audio-build.json');mix=read(mp);status=MEDIA/P.name/('mixed-asr-v27/status.json'if new else'mixed-asr-v13/status.json'if'inside'in P.name else'mixed-asr-v10/status.json');rp=Path(read(status)['review']['path']);r=read(rp);assert read(read(r['job']['path'])['identity']['mixProof']['path'])==mix
 assert pin(mix['mix']['path'])==mix['mix'];data,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);assert rate==24000 and data.shape==(mix['frames'],2)and np.max(np.abs(data))<1
 primitive=ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py';q=load('unchanged_stereo_level_math',primitive);n=load('scoped_source_spelling',HERE/'review-corrected-voice-captions-v29.py');rows=[];flags=[];content=[];joins=[]
 for rec in r['results']:
  t=rec['task'];assert t['sha256']==mix['mix']['sha256']
  if t['kind']=='join':joins.append(dict(key=t['key'],boundarySample=t['boundarySample'],recognized=rec['rawRecognition']['text'],rawRecord=pin(rp.parent/(t['key']+'.json'))));continue
  assert t['kind']=='take';samples=data[t['startSample']:t['endSample']];words=[]
  for w in rec['rawRecognition']['chunks']:
   x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=len(samples)/rate,(t['key'],w);lo,hi=q.sample_window(x,y,rate);words.append(dict(text=w['text'],startSeconds=x,endSeconds=y,durationSeconds=y-x,levels=dict(mixed=q.levels(samples[lo:hi],rate))))
  trend=q.trend(words,'mixed');rows.append(dict(paragraph=t['paragraph'],sourceSampleRange=[t['startSample'],t['endSample']],words=words,trend=trend,wholeTake=q.levels(samples,rate)));content.append(dict(paragraph=t['paragraph'],expected=t['expected'],recognized=rec['rawRecognition']['text'],literal=n.norm(t['expected'],P.name,t['paragraph'])==n.norm(rec['rawRecognition']['text'],P.name,t['paragraph'])))
  if trend['suspect']:flags.append(dict(kind='sustained-word-body-decline',paragraph=t['paragraph'],trend=trend))
 center=statistics.median(x['wholeTake']['bodyDbfs']for x in rows)
 for x in rows:
  x['relativeBodyDb']=x['wholeTake']['bodyDbfs']-center
  if x['relativeBodyDb']<=q.POLICY['paragraphBelowMedianWarningDb']:flags.append(dict(kind='paragraph-below-median',paragraph=x['paragraph'],relativeBodyDb=x['relativeBodyDb']))
 assert len(joins)==len(rows)-1
 report=mp.parent/'mixed-level-review-v1.json';body=dict(mixProof=pin(mp),asrReview=pin(rp),primitive=pin(primitive),policy=q.POLICY,actualStereoMixSampleRanges=True,paragraphs=rows,flags=flags,actualListening=False,humanApproval=False)
 print(json.dumps(dict(project=P.name,flags=flags,content=content,joins=joins),ensure_ascii=False),flush=True)
 if not a.record_content:return
 assert not flags and all(x['literal']for x in content),'Retain a hold; do not change source wording, thresholds or recognition evidence to pass'
 if not report.exists():save(report,body)
 else:assert read(report)==body
 save(mp.parent/'mixed-content-review.json',dict(approvedForPilot=True,mixProof=pin(mp),blindAsrReview=pin(rp),technicalVoiceReview=selected['technicalVoiceReview'],mixedLevelReview=pin(report),reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewScope='All complete mixed paragraphs match the selected narration after scoped orthographic equivalence. Actual raw join transcripts were separately inspected in this conversation and remain unchanged; they supply no new caption interpolation.',recognitionReviewNotes=(pin(mp.parent/'mixed-peer-review-v29.json')if(mp.parent/'mixed-peer-review-v29.json').exists()else None),joinTranscripts=joins,musicToVoiceMaximumDb=max(x['musicMinusVoiceDb']for x in mix['wordWindows']),knownStemResidual=mix['knownStemResidual'],voiceGain=1,voiceInternalDsp=False,bodyOnly=True,actualListening=False,humanApproval=False,finalFilmComplete=False))
if __name__=='__main__':main()
