"""Reviewed clause boundaries and semantic motion anchors for the castle revisions."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save
from prepare_causal_edit import prepare
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')

def native(anchors,labels,phases,pilots,description):
    return dict(anchors=[dict(word=w,progress=t,**({'edge':'end'} if end else {})) for w,t,end in anchors],
                labels=labels,phaseAnchors=phases,pilotAnchors=pilots,description=description)

def main():
    base=read(HERE/'edit-config-07.json')
    configs={
      '09':dict(clauseEnds=[[4,7,10,12,16],[4,8,12,16,18,22,27],[4,6,11,15,18,23],[3,7,10,14,18,21,24,27]],
        spellingReviews={'2':[dict(wordIndex=22,recognized='잃게',caption='읽게',
          evidence=str(WORK/'voice/09/0267a3c8691d/independent-context/e3db01a22c48/review.json'),
          reason='Independent complete second sentence recognizes 읽게; exact retained PCM. Raw ASR remains unchanged.')]},
        native={
          '1':native([(0,0,False),(8,.20,True),(9,.28,False),(16,.67,True),(17,.78,False),(22,.97,True),(27,1,True)],
            ['넓은 뜰: 먼 길과 목적지','좁은 통로: 가려진 다음 공간','높은 발판: 아래 착지점'],[0,2,4],[1,3,5],
            '독립 원리 모형 · 이동에 따라 바뀌는 시야'),
          '3':native([(0,0,False),(10,.22,True),(11,.25,False),(13,.44,False),(15,.83,False),(18,.97,True),(27,1,True)],
            ['캐릭터와 함께 이동','모서리 너머를 확인','아래를 보고 다음 행동 판단'],[0,3,4],[1,3,5],
            '독립 원리 모형 · 정보가 달라지면 판단도 달라진다')},
        starts=[118,224],ends=[144,243],
        labels=['엘든 링 실제 영상 · 지붕에서 좁은 통로로','엘든 링 실제 영상 · 높은 난간에서 아래 확인'],
        observation='Actual roof-to-passage and high tower ledges. Menu at approximately145s excluded. Model follows the spatial transitions; not an exact replica or measured player emotion.'),
      '12':dict(clauseEnds=[[2,5,8,12,16],[4,7,11,14,20,25],[6,10,13,17,19,23],[4,8,13,17,21,25]],
        spellingReviews={
          '0':[dict(wordIndex=0,recognized='엘덴',caption='엘든',reason='Korean title spelling of Elden Ring; no different named entity or missing word. Human pronunciation review is separate.')],
          '1':[dict(wordIndex=22,recognized='사이에',caption='사이의',reason='Spoken Korean realization of 의 as 에; unchanged grammatical phrase, positive whole-word interval.'),
               dict(wordIndex=23,recognized='세',caption='새',reason='Same pronounced syllable; source and full sentence describe a new route, not three routes. Preserve raw recognition and review final mix context.')],
          '2':[dict(wordIndex=4,recognized='제한하고',caption='제안하고',
               evidence=str(WORK/'voice/12/6e481e351ff6/independent-context/37f73d280d8e/review.json'),
               reason='Independent complete sentence recognizes 제안하고 on exact retained PCM; no blanket substitution.')]},
        native={
          '1':native([(0,0,False),(2,.16,False),(5,.25,False),(8,.40,False),(12,.58,False),(14,.92,True),(25,1,True)],
            ['탑에 올라 옆 탑 확인','가고 싶은 곳으로 새 길 제안','연결한 길을 직접 걸어 확인'],[0,2,4],[1,3,5],
            '독립 원리 모형 · 플레이하며 길을 다듬기'),
          '3':native([(0,0,False),(5,.12,False),(7,.36,False),(9,.72,False),(13,.82,True),(25,1,True)],
            ['사람의 탐험 검토와 구분','반복 순회로 문제 위치 기록','기록한 위치를 다시 점검'],[0,1,3],[2,3,4],
            '독립 원리 모형 · 자동 점검이 재미를 판정하는 것은 아님')},
        starts=[208,230],ends=[225,248],
        labels=['엘든 링 실제 영상 · 탑에 올라 주변 보기','엘든 링 실제 영상 · 탑 주변의 길 탐험'],
        observation='Actual ladder ascent and tower ledge traversal illustrate finished playable spaces. Internal developer test tools are represented separately by a model, not inferred from gameplay.')}
    for number,extra in configs.items():
        config=dict(episode=number,lock=str(HERE/'locked'/f'{number}-r2.json'))
        for k in ['clauseEnds','spellingReviews','native']:config[k]=extra[k]
        config['gameplay']=[{**base['gameplay'][i], 'start':extra['starts'][i],
          'observedUntil':extra['ends'][i],'label':extra['labels'][i]} for i in range(2)]
        config['selectionReview']={**base['selectionReview'],'observation':extra['observation']}
        path=HERE/f'edit-config-{number}-r2.json';save(path,config);prepare(path)

if __name__=='__main__':main()
