"""Prepare a separate natural-sentence voice version; preserve every v1 input."""
from pathlib import Path
import datetime, hashlib, json, re
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
EDITS={
 'shorts-oot-ninja-show-z-targeting':{
  'p001':'젤다에서 적을 주목해 보세요. 옆으로 움직여도 상대를 바라봅니다. 특정 상대를 계속 겨누는 조작, 락온입니다. 교토의 닌자 공연이 여기에 어떤 힌트를 줬을까요? 화면의 문제부터 살펴보겠습니다. 그다음은 공격 차례와 상대 중심 이동입니다.',
  'p003':'한 개발자는 검술 액션의 힌트를 찾으러 공연에 갔습니다. 닌자는 팽팽한 사슬을 사이에 두고 상대 주위를 돌았습니다. 개발자는 이 움직임을 눈여겨봤습니다.',
  'p004':'상대를 겨누기 쉽게 하자는 고민은 마리오 육십사 때부터 있었습니다. 다른 개발자가 공연에서 찾은 해법은 공격 차례였습니다. 한 명이 싸우는 동안 나머지는 기다렸습니다.',
  'p006':'사슬에서 얻은 힌트를 보이지 않는 연결로 생각해 보세요. 상대를 향한 방향이 기준입니다. 앞으로 움직이면 다가갑니다. 옆으로 움직이면 상대 주위를 돕니다. 빈틈을 찾으면 뛰어들어 공격합니다.'
 },
 'shorts-mario64-lakitu-camera':{
  'p001':'마리오 육십사에는 카메라를 든 캐릭터가 나옵니다. 이름은 쥬게무입니다. 마리오 조작과 카메라 조작은 서로 다릅니다. 가까이 살펴보고, 주위를 돌고, 멀리서 보는 순서로 살펴보겠습니다.',
  'p002':'카메라는 마리오를 따라가며 촬영합니다. 플레이어는 씨 버튼으로 촬영 위치와 방향을 조절합니다. 화면을 보는 자리가 바로 시점입니다. 이 시점도 직접 바꿀 수 있습니다.',
  'p003':'주변이나 위쪽을 둘러보세요. 길과 파워스타를 찾는 데 도움이 됩니다. 마리오가 서 있는 자리와 카메라가 향하는 방향을 나눠 생각하면 쉽습니다.',
  'p005':'씨 버튼의 왼쪽과 오른쪽을 눌러 보세요. 카메라가 마리오 주위를 돕니다. 같은 마리오를 다른 쪽에서 볼 수 있죠. 더 돌릴 수 없는 곳에서는 경고음이 한계를 알려 줍니다.',
  'p006':'씨 버튼의 아래쪽을 누르면 카메라가 뒤로 빠집니다. 마리오는 작게 보입니다. 주변 공간은 더 넓게 들어옵니다. 가까이 보기, 주위를 돌기, 멀리 보기. 마리오 육십사에서는 플레이어가 촬영자이기도 한 겁니다.'
 }
}
def main():
    batch=read(HERE/'batch.json');summary=[]
    for row in batch['projects']:
        slug=row['slug'];project=ROOT/'projects'/slug;origin=project/'planning/narration-locked-v1.json';old=read(origin)
        assert old['narrationLocked'] and old['approvedForTts']
        paragraphs=[];units=[]
        for paragraph in old['paragraphs']:
            text=EDITS.get(slug,{}).get(paragraph['id'],paragraph['ko'])
            sentences=re.split(r'(?<=[.!?])\s+',text.strip())
            ids=[]
            for sentence in sentences:
                assert sentence and sentence[-1]in'.!?'
                unit=dict(id=f'u{len(units)+1:03}',paragraph=paragraph['id'],ko=sentence)
                units.append(unit);ids.append(unit['id'])
            paragraphs.append(dict(id=paragraph['id'],ko=' '.join(sentences),previousEnglishMeaning=paragraph['en'],unitIds=ids,wordingRevised=paragraph['id']in EDITS.get(slug,{})))
        evidence=[]
        status=MEDIA/slug/'asr-v1/status.json'
        if status.exists():
            s=read(status)
            if s.get('modelCompleted'):
                review=Path(s['review']['path']);evidence.append(pin(review));level=review.parent/'levels.json'
                if level.exists():evidence.append(pin(level))
        new=dict(schemaVersion=1,slug=slug,origin=pin(origin),sourceInputs=[pin(origin)]+[old[k]for k in ['sourceDraft','sourceOrderMap','sourceActionReview']]+[old.get('nativeModelCpuReview',old.get('nativePilotReview'))],
            previousAsrEvidence=evidence,paragraphs=paragraphs,units=units,narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,
            decision='Generate natural sentences separately after sustained late-body decline in independently reviewed long-paragraph sources. First two lessons also clarify ambiguous heard phrases. Remaining lessons preserve exact original words and sentence order.',
            safeguards=['Same approved voice/reference/model/profile, one attempt per unit.','No gain, compression, fading, trimming, speed manipulation or lowered QA thresholds.','Review complete paragraphs as well as individual units and every join; short units do not waive paragraph trend checks.','Previous English is a meaning reference only; new clause timing/translation must match the final spoken version.'],
            sourceAndNarrationSemanticsReady=True,humanApproval=False,voiceAcceptedForFilm=False)
        locked=project/'planning/narration-sentence-v2.json';write(locked,new)
        script=project/'script/narration.sentence-v2.json';write(script,dict(title=old.get('workingTitle',slug),status='Separate sentence source, independent blind QA required',scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in units]))
        manifest=read(project/'production/tts-manifest-v1.json');manifest['revision']='natural-sentence-v2';manifest['paths']['script']=str(script.relative_to(ROOT)).replace('\\','/');manifest['tts']['outputDir']='shared/output/original-tech-twelve-20261115/'+slug+'/voice-sentence-v2';manifest['tts']['filenameStem']='sentence-voice-v2';manifest['srtRole']='Unreviewed unit timing; final captions use actual reviewed whole-word boundaries only.'
        manifest_path=project/'production/tts-manifest-sentence-v2.json';write(manifest_path,manifest)
        summary.append(dict(slug=slug,paragraphs=len(paragraphs),units=len(units),source=pin(locked),manifest=pin(manifest_path),script=pin(script)))
    write(HERE/'sentence-voice-input-review-v2.json',dict(timeUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exactProjects=summary,paragraphs=sum(x['paragraphs']for x in summary),units=sum(x['units']for x in summary),wordOrderPreservedForLastTen=True,firstTwoEdits=EDITS,actualVoiceGenerated=False,finalFilmsComplete=False))
    print(json.dumps(dict(projects=len(summary),units=sum(x['units']for x in summary))))
if __name__=='__main__':main()
