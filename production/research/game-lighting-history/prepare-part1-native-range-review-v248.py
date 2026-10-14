"""Inspect the exact original interval proposed after an observed title-card defect."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/research/game-lighting-history'
path='production/research/game-lighting-history/local/episode04-native-v1/cyberpunk-ray-reconstruction.mp4'
rows=[{'id':'cyber-actual-action-range','path':path,'ranges':[[46.5,46.5+1085/60]],'ko':'원본 제목 카드 제외 제안. 인물·카메라가 움직이는 실제 게임과 DLSS Off/3.5, Full RT On 조건·FPS 숫자를 함께 확인. 원본 전체 좌표이며 아직 최종 픽셀 승인 아님.'}]
source=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','④-1 원본 실제 동작 범위 검수')
source=source.replace('입력의 움직임 확인 · 최종 자막 합성 픽셀 승인과 구별','제목 카드 제외 · 정상 속도 · 원본 비교 조건과 FPS 보존 확인')
html=R/'local/part1-native-range-review-v248.html';assert not html.exists();html.write_text(source,'utf-8')
print(json.dumps({'proposedRanges':rows[0]['ranges'],'sourceSha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'approved':False}))
