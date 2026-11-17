"""Assemble the article with exact final-master attachments, never local image URLs."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent
article=(H/'companion-article.md').read_text('utf-8')
article=article.replace('마지막 수정에서는 약 0.8초','아이맥 의자에 앉는 동작은 약 0.8초')
article=article.replace('CC0 1.0. 앉기·일어나기 모션.','CC0 1.0. 앉기·일어나기와 눕기·누운 상태·기립 모션.')
article=article.replace('프로젝트 사용 라이선스. 독서 모션의 렌더 결과를 사용하며 원본 파일을 재배포하지 않습니다.','프로젝트 사용 라이선스. 초기 의자 독서에 사용한 기존 모션의 출처이며, 현재 빈백 동작은 KayKit으로 연결했습니다. 원본 파일은 재배포하지 않습니다.')
article=article.replace('- 음악: Morning Coffee / HoliznaCC0, CC0 1.0. 환경음:', '- 음악: [Lo-Fi and Chill Collection / HoliznaCC0](https://opengameart.org/content/lo-fi-and-chill-collection), CC0 1.0. 게임에는 본문에 적은 열 곡을 사용했습니다. 환경음:')
(H/'companion-article.md').write_text(article,'utf-8')
body=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',article)
body='<mention url="https://app.notion.com/p/41b0b1ffa61e81f1a484f6c3e4b0555b">AI 게임 제작</mention>\n\n[이전 2D 픽셀 작업실 제작 문서](https://www.yamyamcoding.com/41b0b1ff-a61e-8139-8fbc-fe769adf5bff)\n\n'+body
frames=json.loads((H/'companion-frames.json').read_text('utf-8'))
for f in frames:
 s=f['timestampSeconds'];time=f'{int(s)//60:02d}:{s%60:05.2f}'
 assert f['notionAttachmentId'] and '{{frame:'+f['name']+'}}' in body
 body=body.replace('{{frame:'+f['name']+'}}','<image source="file-upload://'+f['notionAttachmentId']+'">'+f['caption']+' — 영상 '+time+'</image>')
assert '{{frame:' not in body and body.count('<image ')==len(frames)
(H/'companion-article.notion.md').write_text(body,'utf-8')
print('Prepared',len(frames),'exact-frame article images')
