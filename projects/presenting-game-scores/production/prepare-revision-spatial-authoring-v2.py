"""Preserve completed v8 geometry; author a separate selective revision module."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2';M=ROOT/'motion-canvas/src/projects/presenting-game-scores'
source=M/'measured-score-explanation-frame-exact-v8.tsx';target=M/'revision-spatial-score-explanation-v2.tsx';proof=BASE/'spatial-authoring-preparation-v2.json'
assert not target.exists() and not proof.exists();original=source.read_text('utf-8-sig');txt=original
replacements=[('scoreExplanationMeasuredV8','scoreExplanationBalatroRevisionV2'),("'양과 평가 → 비교 기준 → 계산 표현'","'양과 평가 → 카드의 기여 → 기준과 표현'"),("['양 / 평가','상대 기준','계산 표현']","['양 / 평가','카드 → 점수','기준 / 표현']"),("note('높이와 행동 기호는 설계 설명용 · Tetris 실제 배점표가 아닙니다');","note('높이와 행동 기호는 설계 설명용 · 실제 게임의 배점표가 아닙니다');"),("tag('계속 읽는 총점',-370,280);tag('계속 읽는 수량',360,280);","tag('누적 라운드 점수',-370,280);tag('넘어야 할 목표',360,280);")]
for old,new in replacements:assert old in txt,old;txt=txt.replace(old,new)
target.write_text(txt,'utf-8');assert source.read_text('utf-8-sig')==original
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof.write_text(json.dumps(dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),baselineModule=dict(path=source.relative_to(ROOT).as_posix(),sha256=sha(source)),revisionModule=dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target)),reviewedCodeChanges=[dict(old=a,new=b) for a,b in replacements],projectedFacesOcclusionCameraAndMotionPreserved=True,originalGoodExplanationContentPreserved=True,style='research-black-v1',measuredVoiceTimingAssigned=False,rendered=False,actualAnimatedPixelApproval=False,finalCaptionApproval=False,baselineMediaRegenerated=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Separate spatial revision module prepared. Baseline/code/media preserved; measured timing and final animated pixels pending.')
