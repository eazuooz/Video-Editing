"""Technical resize only of the individually reviewed ImageGen originals."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
generated=Path('C:/Users/eazuo/.codex/generated_images/01a10594-7278-7761-b482-62c0269a3a18')
rows=[('game-math-interpolation-paths-v2','exec-5fc585b4-a276-4173-b415-3eedc741be06.png','두 자세 사이를 / 자연스럽게!','Physical toy planes show two orientations and the in-between path.'),('game-math-rotation-conversions-v2','exec-37970ca2-3ce1-4e55-929b-71bf033065a5.png','숫자는 달라도 / 같은 자세!','One unchanged toy plane with angle, quaternion and matrix tags.')]
for slug,file,title,concept in rows:
 src=generated/file;P=ROOT/'projects'/slug/'publishing';P.mkdir(parents=True,exist_ok=True)
 target=P/'thumbnail-v2.png';im=Image.open(src).convert('RGB');im.resize((1280,720),Image.Resampling.LANCZOS).save(target)
 mobile=ROOT/'shared/output'/slug/'thumbnail-mobile-v2.png';mobile.parent.mkdir(parents=True,exist_ok=True)
 im.resize((480,270),Image.Resampling.LANCZOS).save(mobile)
 record={'tool':'built-in image_gen','source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'target':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'technicalResize':[1280,720],'artEditsOutsideImageGen':False,'headline':title,'concept':concept,'originalPixelReview':True,'mobilePixelReview':False,'noGameInsetOrPPT':True,'style':'yellow header, white ground, large black/red Korean headline, integrated calico cat illustration'}
 (P/'thumbnail-v2.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(record,ensure_ascii=False))
