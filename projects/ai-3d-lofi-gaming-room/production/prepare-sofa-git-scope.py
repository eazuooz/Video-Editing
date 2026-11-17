"""Create the selective v10/v4 commit scope with exact referenced texture exceptions."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];U=R/'unity/LofiGamingRoomWeb'
textures=['ThirdParty/VintageSofaV10/BaseColor.png','ThirdParty/VintageSofaV10/Normal.png','ThirdParty/VintageSofaV10/MetallicSmoothness.png','TripoSleepingCatV10/BaseColor.png','TripoSleepingCatV10/Normal.png']
for relative in textures:
 p=U/'Assets/LofiRoom'/relative
 sofa='VintageSofa' in relative
 record={'path':p.relative_to(R).as_posix(),'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'purpose':'Actual URP material texture referenced by the selected v10 sofa/cat prefab','provider':'RG Poly' if sofa else 'Tripo Studio H3.1','license':'CC0 1.0' if sofa else 'Paid Tripo output from a cleaned AI derivative of a CC0 Am9489 photograph','source':'https://rg-poly.itch.io/vintage-retro-stylized-pack' if sofa else 'https://studio.tripo3d.ai/ko/workspace/retopology/81839ca7-5d7f-4c7e-9da3-edb5316946fa','importRecord':'production/sofa-v10-source.json' if sofa else 'production/cat-v10-import.json','actuallyUsed':True}
 p.with_suffix('.png.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
g=U/'.gitignore';s=g.read_text('utf-8');marker='# Exact required textures for the selected sleeping-cat / reading-sofa scene'
if marker not in s:s+='\n'+marker+'\n'+'\n'.join('!Assets/LofiRoom/'+v for v in textures)+'\n';g.write_text(s,'utf-8')
s=(H/'scoped-tutorial-v3-commit.py').read_text('utf-8').replace('tutorial-v3','sofa-tutorial-v4').replace('living-room-v9','living-room-v10').replace('full-video-v3','full-video-v4').replace('len(images)==9','len(images)==14')
s=s.replace(" names=spec['ownedPaths'];images=", " names=spec['ownedPaths'];images=")
s=s.replace(" raw=subprocess.check_output",''' for relative in '''+repr(textures)+''':
  p=root/'unity/LofiGamingRoomWeb/Assets/LofiRoom'/relative
  images.append({'path':p.relative_to(root).as_posix(),'purpose':'required-scene-asset','reason':'Actually referenced v10 URP texture; source and license recorded beside the file.','sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'reviewedAt':now,'project':'ai-3d-lofi-gaming-room'})
 raw=subprocess.check_output''')
s=s.replace("names={n for n in raw if n and not any(v in n for v in excluded)}", "names={n for n in raw if n and not any(v in n for v in excluded) and PurePosixPath(n).suffix.lower() not in {'.mp4','.mp3','.wav','.ogg','.zip','.7z','.exe','.dll','.log','.fbx','.glb','.gltf','.bin','.jpg','.png','.webp'}}")
s=s.replace('v9는 삼색 무늬·매끈한 꼬리와 독서 시 책·손목·팔꿈치 접촉을 보완했다.','v10은 CC0 수면 사진의 파생 입력으로 생성한 실제 Tripo 삼색고양이와 기존 CC0 소파, 휴식 몸·독서 팔 클립 및 책 접촉을 사용한다.')
s=s.replace('v9 게임의 고양이·독서 접촉','v10 실제 Tripo 고양이·소파 독서').replace('natural cat, fitted reading contacts','actual Tripo calico, supported sofa reading')
(H/'scoped-sofa-v4-commit.py').write_text(s,'utf-8')
print('Prepared selective scope and 5 exact required-texture exceptions')
