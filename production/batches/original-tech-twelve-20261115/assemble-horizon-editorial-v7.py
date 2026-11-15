"""Remove redundant transition/contrast sentences; retain all retained PCM exactly."""
from pathlib import Path
import hashlib,json,wave
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/shorts-horizon-gpu-placement';BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 np=P/'planning/narration-repair-v6.json';n=read(np);vp=BASE/'voice-repair-v6/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(BASE/'asr-repair-v6/status.json')['review']['path']);lp=rp.parent/'levels.json';assert [x['taskKey']for x in read(lp)['flags']]==['paragraph-p004'];drop=['s6u0111','s6u0132'];units=[];raw=[]
 for u,r in zip(n['units'],v['rawChunks']):
  if u['id']in drop:continue
  assert pin(r['path'])['sha256']==r['sha256'];units.append(dict(u,sourceRaw=r));raw.append(r)
 for para in n['paragraphs']:
  selected=[u for u in units if u['paragraph']==para['id']];para.update(ko=' '.join(u['ko']for u in selected),unitIds=[u['id']for u in selected])
 n.update(origin=pin(np),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=[],reuseUnits=units,removedRedundantUnits=drop,reason='Remove the redundant announcement of map comparison and closing arbitrary-placement contrast. The previous paragraph already establishes the density map; p004 retains candidate testing, passing-point selection, spacing and patterns. Every learning operation remains in source order. Retained PCM is byte-exact, with no DSP.');locked=P/'planning/narration-horizon-v7.json';save(locked,n)
 cap=read(P/'planning/caption-clauses-repair-v6.json');cap['source']=pin(locked);p4=next(p for p in cap['paragraphs']if p['id']=='p004');p4['clauses']=p4['clauses'][1:-1]
 for a,b in zip(n['paragraphs'],cap['paragraphs']):assert ''.join(a['ko'].split())==''.join(''.join(x[0]for x in b['clauses']).split())
 save(P/'planning/caption-clauses-horizon-v7.json',cap);out=BASE/'voice-edit-v7';pieces=[];entries=[];position=0
 for i,(u,r)in enumerate(zip(units,raw)):
  with wave.open(r['path'],'rb')as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000);data=w.readframes(w.getnframes())
  assert hashlib.sha256(data).hexdigest()==r['pcmSHA256'];pieces.append(data);entries.append(dict(index=i+1,scene_id=u['id'],text=u['ko'],start=position/24000,end=(position+r['frames'])/24000));position+=r['frames']
  if i+1<len(units):pieces.append(bytes(6720*2));position+=6720
 out.mkdir(parents=True,exist_ok=False);wav=out/'horizon-edit-v7.wav';pcm=b''.join(pieces)
 with wave.open(str(wav),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
 ut=out/'unit-timing.json';save(ut,dict(entries=entries,sample_rate=24000,duration_seconds=position/24000));pt=out/'paragraph-timing.json';paragraphs=[]
 for p in n['paragraphs']:
  es=[e for e,u in zip(entries,units)if u['paragraph']==p['id']];paragraphs.append(dict(id=p['id'],text=p['ko'],start=es[0]['start'],end=es[-1]['end'],startSample=round(es[0]['start']*24000),endSample=round(es[-1]['end']*24000)))
 save(pt,dict(entries=paragraphs,sampleRate=24000,rawBytesPreserved=True));identity=dict(slug=P.name,sourceInputs=[pin(p)for p in [locked,vp,rp,lp,Path(__file__)]],unitGroups=units,paragraphs=n['paragraphs'],spoken=[u['ko']for u in units],unitGapSeconds=.28,noGainSpeedTrimOrCompression=True);fp=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();proof=dict(fingerprint=fp,identity=identity,rawChunks=raw,canonical=dict(**pin(wav),frames=position,rate=24000,duration=position/24000,pcmSHA256=hashlib.sha256(pcm).hexdigest()),unitTiming=pin(ut),paragraphTiming=pin(pt),modelCompleted=True,sourceModelGenerationReused=True,newModelStarted=False,sourceRawPcmAllExact=True,voiceAcceptedForFilm=False,actualListening=False,humanApproval=False);save(out/'voice-generation-complete-proof.json',proof);print(json.dumps(dict(proof=pin(out/'voice-generation-complete-proof.json'),duration=position/24000,newEngineUnits=0)))
if __name__=='__main__':main()
