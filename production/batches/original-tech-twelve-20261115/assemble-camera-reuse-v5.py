"""Reuse a clearly recognized original sentence after v4 says 나노 for 나눠."""
from pathlib import Path
import hashlib,json,wave
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-mario64-lakitu-camera';BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    source_path=P/'planning/narration-repair-v3.json';source=read(source_path);v4path=BASE/'voice-repair-v4/voice-generation-complete-proof.json';v4=read(v4path);v2path=BASE/'voice-sentence-v2/voice-generation-complete-proof.json';v2=read(v2path);asr4=Path(read(BASE/'asr-repair-v4/status.json')['review']['path']);asr2=Path(read(BASE/'asr-sentence-v2/status.json')['review']['path']);assert read(asr4.parent/'levels.json')['flags']==[]
    record=next(x for x in read(asr2)['results']if x['task']['key']=='unit-u011');assert '나눠'in record['rawRecognition']['text']
    old_unit=next(u for u in v2['identity']['unitGroups']if u['id']=='u011');old_raw=next(r for u,r in zip(v2['identity']['unitGroups'],v2['rawChunks'])if u['id']=='u011');current={u['id']:r for u,r in zip(v4['identity']['unitGroups'],v4['rawChunks'])};units=[];raw=[]
    for u in source['units']:
        if u['id']=='r0111':u=dict(old_unit);row=old_raw
        else:row=current[u['id']]
        assert pin(row['path'])['sha256']==row['sha256'];units.append(u);raw.append(row)
    for para in source['paragraphs']:
        selected=[u for u in units if u['paragraph']==para['id']];para.update(ko=' '.join(u['ko']for u in selected),unitIds=[u['id']for u in selected])
    source.update(units=units,newUnits=[],reuseUnits=units,origin=pin(source_path),sourceVoice=pin(v4path),sourceAsr=pin(asr4),earlierVoice=pin(v2path),earlierAsr=pin(asr2),reason='All v4 word-level and paragraph numeric checks pass. Replace its consistently recognized 나노 sentence with the byte-exact original clearly recognized 나눠 sentence. Retain every other v4 unit and source order.',newEngineRequired=False)
    locked=P/'planning/narration-camera-v5.json';write(locked,source)
    caption_path=P/'planning/caption-clauses-sentence-v2.json';caption=read(caption_path);caption['source']=pin(locked);caption['paragraphs'][0]['clauses']=[x for i,x in enumerate(caption['paragraphs'][0]['clauses'])if i!=2]
    caption['paragraphs'][1]['clauses']=[['카메라는 마리오를 따라갑니다.','The camera follows Mario.'],['씨 버튼으로 찍는 자리와 방향을 바꿉니다.','The C buttons change its position and direction.'],['이처럼 화면을 보는 자리를 시점이라고 합니다.','The viewpoint is where we see the scene from.']]
    caption['paragraphs'][2]['clauses']=[['시점을 돌려 주변과 위쪽을 살펴볼 수 있습니다.','Turn the viewpoint to look around and upward.'],['갈 길과 파워스타를 찾는 데 도움이 됩니다.','It helps you find routes and Power Stars.'],['마리오가 서 있는 자리와','Think about where Mario stands'],['카메라가 향하는 방향을 나눠 생각하면 쉽습니다.','separately from what the camera points toward.']]
    for p,c in zip(source['paragraphs'],caption['paragraphs']):assert ''.join(p['ko'].split())==''.join(''.join(x[0]for x in c['clauses']).split())
    write(P/'planning/caption-clauses-camera-v5.json',caption)
    out=BASE/'voice-edit-v5';pieces=[];entries=[];position=0;gap=6720
    for i,(u,row)in enumerate(zip(units,raw)):
        with wave.open(row['path'],'rb')as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000);data=w.readframes(w.getnframes())
        assert hashlib.sha256(data).hexdigest()==row['pcmSHA256'];pieces.append(data);entries.append(dict(index=i+1,scene_id=u['id'],text=u['ko'],start=position/24000,end=(position+row['frames'])/24000));position+=row['frames']
        if i<len(units)-1:pieces.append(bytes(gap*2));position+=gap
    pcm=b''.join(pieces);out.mkdir(parents=True,exist_ok=False);wav=out/'camera-edit-v5.wav'
    with wave.open(str(wav),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    unit_timing=out/'unit-timing.json';write(unit_timing,dict(entries=entries,sample_rate=24000,duration_seconds=position/24000));paragraphs=[]
    for p in source['paragraphs']:
        rows=[e for e,u in zip(entries,units)if u['paragraph']==p['id']];paragraphs.append(dict(id=p['id'],text=p['ko'],start=rows[0]['start'],end=rows[-1]['end'],startSample=round(rows[0]['start']*24000),endSample=round(rows[-1]['end']*24000)))
    para_timing=out/'paragraph-timing.json';write(para_timing,dict(entries=paragraphs,sampleRate=24000,rawBytesPreserved=True));identity=dict(slug=P.name,sourceInputs=[pin(x)for x in[locked,v4path,v2path,asr4,asr4.parent/'levels.json',asr2,Path(__file__)]],unitGroups=units,paragraphs=source['paragraphs'],spoken=[u['ko']for u in units],unitGapSeconds=.28,noGainSpeedTrimOrCompression=True)
    fp=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();proof=dict(fingerprint=fp,identity=identity,rawChunks=raw,canonical=dict(**pin(wav),frames=position,rate=24000,duration=position/24000,pcmSHA256=hashlib.sha256(pcm).hexdigest()),unitTiming=pin(unit_timing),paragraphTiming=pin(para_timing),modelCompleted=True,sourceModelGenerationReused=True,newModelStarted=False,sourceRawPcmAllExact=True,voiceAcceptedForFilm=False,actualListening=False,humanApproval=False)
    write(out/'voice-generation-complete-proof.json',proof);print(json.dumps(dict(proof=pin(out/'voice-generation-complete-proof.json'),duration=position/24000,newEngineUnits=0,rawChunks=len(raw))))
if __name__=='__main__':main()
