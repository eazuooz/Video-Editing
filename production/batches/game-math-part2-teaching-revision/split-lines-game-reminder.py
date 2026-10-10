"""Split only at the generated line gap, retaining every PCM sample in order."""
from pathlib import Path
import json,hashlib,copy
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def split(combined,pending):
 if 'LG06' not in combined:return
 provenance=B/{'game-math-lines-unit-retake-v6':'lines-line-provenance-v6.json','game-math-lines-numeric-retakes-v5':'lines-line-provenance-v5.json','game-math-lines-opening-retake-v4':'lines-line-provenance-v4.json','game-math-lines-narration-retakes-v3':'lines-line-provenance-v3.json','game-math-lines-bounds-teaching-additions-v2':'lines-line-provenance.json'}[combined['LG06']['ttsProject']]
 if not provenance.exists():
  combined.pop('LG06');pending.extend(x for x in ['LG06','LB06'] if x not in pending);return
 old=combined.pop('LG06');records=read(provenance)['records'];row=next(r for r in records if r['scene']==old['ttsScene']);assert len(row['lines'])==4
 for x in row['lines']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
 wav=ROOT/old['voice'];a,sr=sf.read(wav,dtype='int16');assert sr==24000 and a.ndim==1
 assert hashlib.sha256(wav.read_bytes()).hexdigest()==row['currentSceneSha256']==old['voiceSha256']
 gap=round(.28*sr);cut=sum(sf.info(ROOT/x['path']).frames for x in row['lines'][:3])+2*gap+gap//2
 assert np.max(np.abs(a[cut-gap//2:cut+gap//2]))==0,'Use the actual generated silent line gap'
 pieces=[a[:cut],a[cut:]];assert np.array_equal(np.concatenate(pieces),a)
 raw=read(wav.parent.parent/'asr'/f"{old['ttsScene']}.json");assert raw['audio_sha256']==old['voiceSha256']
 out=ROOT/'shared/output/game-math-part2-teaching-revision/lines/split-additions';record=[]
 for ident,first,last,begin,end,piece in [('LG06',0,3,0,cut/sr,pieces[0]),('LB06',3,4,cut/sr,len(a)/sr,pieces[1])]:
  path=out/'chunks'/f'{ident}-scene.wav';path.parent.mkdir(parents=True,exist_ok=True);sf.write(path,piece,sr,subtype='PCM_16')
  check,_=sf.read(path,dtype='int16');assert np.array_equal(check,piece)
  digest=hashlib.sha256(path.read_bytes()).hexdigest();slot=copy.deepcopy(old)
  slot.update(id=ident,ttsScene=ident,voice=path.relative_to(ROOT).as_posix(),voiceSha256=digest,voiceSeconds=len(piece)/sr,seconds=len(piece)/sr+.6,sourceType='actual-footage' if ident=='LG06' else 'supplement')
  slot['lineStarts']=[max(0,t-begin) for t in old['lineStarts'][first:last]];slot['lineEnds']=[min(len(piece)/sr,t-begin) for t in old['lineEnds'][first:last]]
  slot['captions']={lang:[{**c,'start':max(0,c['start']-begin),'end':min(len(piece)/sr,c['end']-begin),'line':c['line']-first} for c in old['captions'][lang] if first<=c['line']<last] for lang in ['ko','en']}
  slot['sentenceCues']=[{**s,'start':max(0,s['start']-begin),'end':min(len(piece)/sr,s['end']-begin)} for s in old['sentenceCues'] if begin-.02<=s['start']<end-.02]
  slot['pcmPreservation']={'sourceVoice':old['voice'],'sourceVoiceSha256':old['voiceSha256'],'sampleRange':[0,cut] if first==0 else [cut,len(a)],'sampleRate':sr,'allSamplesRetainedAcrossSplit':True,'splitAtActualSilentLineGap':True}
  words=[{**w,'timestamp':[max(0,w['timestamp'][0]-begin),min(len(piece)/sr,w['timestamp'][1]-begin) if w['timestamp'][1] is not None else None]} for w in raw['words'] if w['timestamp'][0] is not None and begin-.02<=w['timestamp'][0]<end-.02]
  assert all(c['end']>c['start'] for lang in slot['captions'].values() for c in lang)
  cache={'scene':ident,'audio_sha256':digest,'text':''.join(w['text'] for w in words),'words':words,'derivedFromUnchangedPcm':slot['pcmPreservation'],'recognizer':'existing current-hash raw words shifted by exact sample offset; no supplied words added'}
  write(out/'asr'/f'{ident}.json',cache);combined[ident]=slot;record.append({'id':ident,**slot['pcmPreservation'],'voice':slot['voice'],'voiceSha256':digest,'lineCount':last-first})
 write(B/'lines-game-reminder-pcm-split.json',{'records':record,'entireSourcePcmReconstructsExactly':True,'engineAngleMeasured':False,'humanListening':'pending'})
