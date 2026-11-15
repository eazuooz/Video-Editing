"""New words only for actual held or incomplete units; preserve all other takes."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
REPLACEMENTS={
 'shorts-mario64-lakitu-camera':{
  'u002':[],
  'u005':['카메라는 마리오를 따라갑니다.'],
  'u006':['씨 버튼으로 찍는 자리와 방향을 바꿉니다.'],
  'u007':['이처럼 화면을 보는 자리를 시점이라고 합니다.'],
  'u008':[],
  'u009':['시점을 돌려 주변과 위쪽을 살펴볼 수 있습니다.'],
  'u010':['갈 길과 파워스타를 찾는 데 도움이 됩니다.'],
  'u011':['마리오의 위치와 카메라의 방향은 나눠 생각하면 쉽습니다.']},
 'shorts-journey-sand-sparkle':{
  'u001':['이 게임의 사막은 움직일 때마다 반짝입니다.'],
  'u007':['개발진은 작은 텍스처에서도 결이 남게 방향의 분포를 다듬었습니다.'],
  'u011':['좋은 반짝임과 불안정한 깜빡임은 다릅니다.'],
  'u012':['개발진은 반짝임을 계산하는 방법을 바꿨습니다.','빛과 시선의 중간 방향 대신 다른 관계를 썼습니다.','표면과 시선 사이의 관계입니다.'],
  'u018':['마지막은 모래 언덕 위에 넓게 흐르는 반사광입니다.','이 빛이 언덕의 큰 형태를 살립니다.'],
  'u020':['모래알의 개수보다 빛을 나눠 표현하는 방법이 중요합니다.']}
}
def main():
    summaries=[]
    for slug,replacements in REPLACEMENTS.items():
        p=ROOT/'projects'/slug;old_source=p/'planning/narration-sentence-v2.json';old=read(old_source);old_proof=MEDIA/slug/'voice-sentence-v2/voice-generation-complete-proof.json';proof=read(old_proof);review=Path(read(MEDIA/slug/'asr-sentence-v2/status.json')['review']['path']);levels=review.parent/'levels.json';assert levels.exists()
        units=[];new=[];reuse=[]
        for i,u in enumerate(old['units']):
            if u['id']in replacements:
                for n,text in enumerate(replacements[u['id']]):
                    unit=dict(id='r'+u['id'][1:]+str(n+1),paragraph=u['paragraph'],ko=text,originUnit=u['id']);units.append(unit);new.append(unit)
            else:
                row=proof['rawChunks'][i];assert pin(row['path'])['sha256']==row['sha256'];unit=dict(u,sourceRaw=row);units.append(unit);reuse.append(unit)
        paragraphs=[]
        for para in old['paragraphs']:
            selected=[u for u in units if u['paragraph']==para['id']];paragraphs.append(dict(id=para['id'],ko=' '.join(u['ko']for u in selected),unitIds=[u['id']for u in selected],previousEnglishMeaning=para['previousEnglishMeaning']))
        locked=p/'planning/narration-repair-v3.json';d=dict(schemaVersion=1,slug=slug,origin=pin(old_source),sourceVoice=pin(old_proof),sourceAsr=pin(review),sourceLevels=pin(levels),sourceInputs=old['sourceInputs'],units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,
            reason=('Clarify camera terminology and replace the two held paragraphs while retaining manual order. Lakitu remains visible and is named in source notes; omit its ambiguous spoken-name unit.'if 'mario64'in slug else'Replace the incomplete sparkle-versus-flicker utterance, split the internally declining14-word sentence into three natural statements, and express ambiguous proper/technical names plainly. Preserve every optical distinction and caution.'),
            qualityPolicy='Same approved reference/model/profile and unchanged9-word/6-second and word-body level thresholds. Also check the combined camera p002+p003 sequence. No gain, compression, trimming, fades or speed changes.',humanApproval=False,voiceAcceptedForFilm=False)
        write(locked,d);script=p/'script/narration.repair-v3.json';write(script,dict(title=slug,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
        manifest=read(p/'production/tts-manifest-sentence-v2.json');manifest['revision']='targeted-semantic-repair-v3';manifest['paths']['script']=str(script.relative_to(ROOT)).replace('\\','/');manifest['tts']['outputDir']='shared/output/original-tech-twelve-20261115/'+slug+'/voice-repair-v3';manifest['tts']['filenameStem']='targeted-voice-repair-v3';write(p/'production/tts-manifest-repair-v3.json',manifest)
        summaries.append(dict(slug=slug,newUnits=len(new),reusedUnits=len(reuse),physicalUnits=len(units),source=pin(locked),partialVoiceGenerated=False))
    write(HERE/'targeted-voice-repair-source-review-v3.json',dict(projects=summaries,sourceWordsMeaningReviewed=True,independentSourceEvidence=True,actualNewVoiceGenerated=False,finalFilmsComplete=False));print(json.dumps(summaries))
if __name__=='__main__':main()
