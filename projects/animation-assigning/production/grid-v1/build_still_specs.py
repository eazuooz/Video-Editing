"""Bind inspected still frames/crops to exact narration-derived lengths."""
from pathlib import Path
import audio_pipeline as ap
H=Path(__file__).resolve().parent
TITLES={2:'몸의 방향 · 발 · 상대와의 거리',11:'상대가 대응할 시간',19:'두 캐릭터가 맞닿는 동작',21:'손과 상대 몸의 위치',22:'잉클링 · 잉크를 쓰는 캐릭터',24:'몸과 무기를 함께 보기',26:'무기가 지나갈 공간',27:'무엇을 피하는가',29:'대기 자세에 담긴 성격',31:'인사로 드러나는 성격',35:'사람과 다른 몸의 구조',38:'부리와 물건이 만나는 곳',47:'움직임이 읽히는가'}

def main():
 p=ap.read(H/'measured-edit-plan.proposal.json');cuts={c['id']:c for c in p['cuts']}
 out=H/'still-specs';out.mkdir(exist_ok=True)
 for row in p['stillCompositionQueue']:
  c=cuts[row['id']];n=int(row['id'][5:]);crop=None
  if n==35:crop=[680,360,790,530]
  if n==38:crop=[700,520,680,450]
  s={'id':row['id'],'frames':row['frames'],'sourceFile':c['sourceFile'],'sourceSha256':c['sourceSha256'],
     'frameTimeSeconds':row['sourceStillTimestamp'],'crop':crop,'viewport':[320,180,1280,720],
     'title':TITLES[n],'contextLabel':'2017년 개발 중 공개 영상' if 'goose-prealpha'==row['source'] else '',
     'outputDir':'projects/animation-assigning/production/local/grid-v1/stills-v1/'+row['id'],
     'cropReview':'root inspected exact full source still; crop retains goose/beak/radio and relevant body parts' if crop else 'root inspected source-stills-v1 contact; entire original frame retained',
     'sourceFrameEvidence':'projects/animation-assigning/production/local/grid-v1/preflight/source-stills-v1/'+row['id']+'.png'}
  ap.save(out/(row['id']+'.json'),s)
 print('13 measured still specs prepared')

if __name__=='__main__':main()
