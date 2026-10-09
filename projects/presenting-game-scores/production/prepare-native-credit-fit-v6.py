from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
raw=ROOT/'shared/assets/presenting-game-scores/raw'
old=raw/'balatro-native-action-playback-v4.html'
target=raw/'balatro-native-action-playback-v6.html'
assert not target.exists(), 'Preserve prepared helper; do not repeat'
s=old.read_text('utf-8-sig')
s=s.replace('video{position:absolute;width:1920px;height:1080px;left:0;top:0;object-fit:contain}', 'video{position:absolute;width:1600px;height:900px;left:160px;top:0;object-fit:contain}.credit{box-sizing:border-box}')
s=s.replace('right:32px;top:24px;max-width:340px;background:#000b;padding:8px 12px;font:24px/30px sans-serif;color:#fff;text-align:right;white-space:normal', 'left:12px;top:320px;width:136px;background:#000b;padding:8px 6px;font:22px/29px sans-serif;color:#fff;text-align:left;white-space:normal;overflow-wrap:normal')
s=s.replace('Footage: Squeaky Whale Gameplay Archive', 'Footage:<br>Squeaky Whale<br>Gameplay Archive')
s=s.replace('원본/상단 48px 이동 표본', '전체 UI 보존 1600×900 / 원본 비교')
s=s.replace("offset=offset?0:-48;v.style.top=offset+'px';status.textContent+=(offset?' | preview up48':' | original')", "offset=offset?0:1;v.style.width=offset?'1920px':'1600px';v.style.height=offset?'1080px':'900px';v.style.left=offset?'0':'160px';v.style.top='0px';status.textContent+=(offset?' | original':' | fit1600x900')")
s=s.replace('상단 48px 이동은 여백 검사 표본이며 하단 48px 검정은 임시 표시입니다. 실제 same-frame fill과 모든 cue 픽셀은 별도 검수합니다. 화면 크레딧도 준비 표본입니다.', '전체 원본 UI를 균일 축소하여 보존하고 크레딧은 왼쪽 여백에 표시합니다. 최종 화면은 같은 프레임의 흐린 배경으로 화면 전체를 채웁니다. 준비 자막과 실제 모든 최종 cue의 승인은 구별합니다.')
target.write_text(s,'utf-8')
print(json.dumps({'helper':target.relative_to(ROOT).as_posix(),'sourceCrop':False,'videoRect':[160,0,1600,900],'captionCenter':[960,970],'creditRect':[12,320,136,200],'mediaGenerated':0,'researchChanges':0}))
