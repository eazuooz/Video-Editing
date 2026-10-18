"""Extract only source-linked stills for the selected explanation package."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/player-customization';L=P/'production/local/reference-preserving-v2';H=P/'production/reference-preserving-v2'
FF=os.environ.get('FFMPEG','C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
O=L/'assets';O.mkdir(parents=True,exist_ok=True)
rows=[
 ('jets-preview','jets2-shop',100,'The equipment layout and the adjacent Test Range are visible together.'),
 ('jets-weapons','jets2-shop',140,'Weapon list, selected weapon detail and the Test Range; do not attribute both ships to one weapon.'),
 ('acvi-assembly','acvi-shop-tradeoffs',156,'Actual booster comparison: Boost Speed306→320 and QB EN Consumption480→560.'),
 ('botw-armor','nintendo-botw-opening',205.5,'Armor category and clothing choices; no sorting execution or temperature resistance inferred.'),
 ('mh-menu','mh-iceborne-armour-328-474',18,'Forge Armor: set rows and distinct body-part columns, selected details and character preview.'),
 ('terratech-build','terratech-edit-test',160,'Changed construction returning to ground-level operation in the same world.'),
 ('acnh-before','nintendo-acnh-character-creation',150.5,'Hairstyle selection and the matching avatar preview, before the next choice.'),
 ('acnh-after','nintendo-acnh-character-creation',151.5,'Different hairstyle on the same avatar; appearance, not measured performance.'),
]
records=[]
for name,key,t,purpose in rows:
 source=L/'media'/(key+'.mp4');receipt=json.loads(source.with_suffix('.source.json').read_text(encoding='utf-8'))
 digest=hashlib.sha256(source.read_bytes()).hexdigest();assert receipt['sha256']==digest
 image=O/(name+'.png');signature={'sourceSha256':digest,'localSeconds':t,'crop':'none'}
 cache=O/(name+'.json')
 if cache.exists():
  old=json.loads(cache.read_text(encoding='utf-8'));assert old['extraction']==signature and image.exists(),name
 else:
  assert not image.exists(),image
  subprocess.run([FF,'-nostdin','-n','-v','error','-threads','2','-ss',str(t),'-i',str(source),'-frames:v','1',str(image)],check=True)
 record=dict(id=name,sourceFile=source.relative_to(R).as_posix(),sourceSha256=digest,sourceUrl=receipt['url'],uploader=receipt['uploader'],image=image.relative_to(R).as_posix(),sha256=hashlib.sha256(image.read_bytes()).hexdigest(),extraction=signature,purpose=purpose,classification='explanation-still-from-independent-gameplay',referenceLessonUsed=False,aspectRatio='16:9',rootFinalLayoutInspection='pending')
 cache.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(record)
(O/'provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest=R/'output/player-customization/preproduction-assets';dest.mkdir(parents=True,exist_ok=True)
for row in records:shutil.copy2(R/row['image'],dest/Path(row['image']).name)
shutil.copy2(O/'provenance.json',dest/'provenance.json')
print('Prepared',len(records),'source-linked independent explanation stills; no media added to Git.')
