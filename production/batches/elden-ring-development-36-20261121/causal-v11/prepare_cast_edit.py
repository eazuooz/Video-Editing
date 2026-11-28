"""Word-timed early/aligned release comparison, using two distinct observed casts."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save
from prepare_causal_edit import prepare
from prepare_castle_edits import native

def main():
    record=read(Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json'))['episodes']['10']['record']
    config=dict(episode='10',lock=str(HERE/'locked/10.json'),
      clauseEnds=[[3,6,8,12,14],[4,7,11,14,18,20],[3,5,10,14,18,21],[4,8,11,16,21,24]],
      native={
        '1':native([(0,0,False),(5,.20,False),(8,.40,False),(14,.51,True),(15,.52,False),(19,.765,False),(20,1,True)],
          ['발사만 먼저 켜면','몸의 준비와 효과가 따로 보임','이번에는 지팡이 동작과 맞추기'],[0,2,4],[1,2,5],
          '독립 원리 모형 · 같은 동작, 다른 발사 시점'),
        '3':native([(0,0,False),(4,.22,True),(9,.35,False),(11,.51,False),(16,.80,True),(24,1,True)],
          ['시간표의 발사 표시 이동','손·지팡이·발사가 이어짐','언제 나오는지도 동작의 일부'],[0,3,4],[1,3,4],
          '독립 원리 모형 · 효과 이벤트와 동작 연결')},
      gameplay=[dict(index=i,path=record['formatSources'][i]['source'],sha256=record['cuts'][i]['sha256'],
                     start=start,observedUntil=end,label='엘든 링 실제 영상 · 지팡이 시전과 회복 동작')
                for i,start,end in [(0,16,28),(2,29,42)]],
      selectionReview=dict(sampleReview=True,continuousPlayback=False,
        sheet='D:/YamyamProduction/elden-ring-development-36-causal-v11/sources/retained-causal-sources-1.jpg',
        observation='Two distinct contiguous source intervals within inspected 16–42s. Cast action is visible; original Time Act Editor keys are not. No duplicate source interval.'))
    path=HERE/'edit-config-10.json';save(path,config);prepare(path)

if __name__=='__main__':main()
