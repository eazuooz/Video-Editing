from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];site=R/'sites/yamyam-cartographers-room/dist'
tools=json.loads((site/'tool-records.json').read_text('utf8'));sources=json.loads((P/'planning/sources.json').read_text('utf8'))
url='https://yamyam-cartographers-room.eazuooz.chatgpt.site'
intro='AI로 만든 한 장의 그림을 실제로 클릭하며 노는 작은 방으로 확장했습니다. 캐릭터 일관성, 픽셀 규격, 걷기와 행동 전환, 실제 도구 명령·요청문·설정을 한 흐름에서 살펴봅니다.\n\n직접 플레이: '+url+'\n의자에 앉기 · 지도 읽기 · 책 꺼내 읽기 · 창밖 보기 · 깃털펜으로 기록하기\n날씨4종과 HoliznaCC0의 CC0 로파이20곡 라디오도 사용할 수 있습니다.\n\n실제 실행: 2dimg2motion, sprite-gen, pixelfx, PixelOE, Agent Sprite Forge, Codixel, Pixelbolt, ComfyUI 및 이미지 생성. Sprite-Sheet-Diffusion은 실제 설치를 시도했으나 공식 필수 가중치 누락으로 추론 재현을 완료하지 못했습니다. 캐릭터 전용 LoRA를 학습한 결과로 소개하지 않습니다.\n'
intro_en='We extend one AI-assisted character and workshop into a small playable room, showing the actual prompts, settings, tool outputs, pixel cleanup, measured walking cycle, and action transitions.\n\nPlay: '+url+'\nSit, read a map, take out a book, look through the window, or write with a quill. The room includes four weather states and a twenty-track CC0 lo-fi radio by HoliznaCC0.\n\nSeven open-source tools, ComfyUI, and image generation were actually used. Sprite-Sheet-Diffusion setup was attempted, but official required weights were missing, so no inference output from it is used. No new character LoRA training is claimed.\n'
credits=['자료·도구 출처 / Sources and tools']
for tool in tools:
 if tool.get('url'):credits.append(tool['name']+': '+tool['url'])
 if tool.get('evidenceUrl'):credits.append('재현 문제 기록: '+tool['evidenceUrl'])
credits += ['음악 / Music: HoliznaCC0 — Lo-Fi and Chill Collection, CC0','https://opengameart.org/content/lo-fi-and-chill-collection','https://creativecommons.org/publicdomain/zero/1.0/','pixelfx includes third-party notices; retained in the supplied source/license records.','실습 캐릭터·방·시트: 이번 제작의 이미지 생성 및 직접 편집 결과. 실제 웹 게임 화면과 도구 출력은 자체 제작·실행 캡처.']
for lang,body in [('ko',intro),('en',intro_en)]:
 (H/f'description.{lang}.txt').write_text(body+'\n'+ '\n'.join(credits)+'\n','utf8')
records=[]
from PIL import Image
for folder,pattern in [(P/'production/local/room-v3/pixel-clean/96x132/writing','write-*.png'),(P/'production/local/room-v3/codixel-writing','write-loop-*.png')]:
 for f in sorted(folder.glob(pattern)):
  im=Image.open(f).convert('RGBA');colors=set(im.getdata());alpha={v[3] for v in colors};assert im.size==(96,132);assert alpha <= {0,255};assert len({v[:3] for v in colors if v[3]})<=32
  records.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':list(im.size),'opaqueColors':len({v[:3] for v in colors if v[3]}),'alpha':sorted(alpha)})
(H/'writer-pixel-qa.json').write_text(json.dumps({'frames':len(records),'allNative96x132':True,'sharedPaletteMaximum':32,'binaryAlpha':True,'records':records,'visualReview':'entry contact sheet, Codixel owner map and 24-frame preview directly inspected; root actual-game contact review separate'},ensure_ascii=False,indent=2),'utf8')
print('Prepared publication drafts; no platform mutations. Writer QA',len(records))
