from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[3]; U=R/'unity/VideoEditing'; H=Path(__file__).resolve().parent
c=json.loads((R/'shared/assets/unity-asset-library.json').read_text(encoding='utf-8-sig')); products={x['id']:x for x in c['products']}
items=[]
def add(key,pid,pattern):
 p=products[pid];candidates=sorted((U/p['actualAssetPath']).rglob(pattern));assert candidates,(key,pattern)
 asset=candidates[0];meta=asset.with_suffix(asset.suffix+'.meta');guid=re.search(r'^guid: (\S+)',meta.read_text(encoding='utf-8-sig'),re.M).group(1)
 items.append(dict(key=key,path=asset.relative_to(U).as_posix(),productId=pid,license='CC0-1.0' if pid!='023' else 'EmacEArt Asset License: commercial projects permitted; no standalone redistribution',url=p['publicProductUrl'],sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),guid=guid,creditRequired=False,sourceRedistribution=False))
add('hero','011','Character_2_2_1_*.prefab');add('heroAlt','011','Character_1_1_1_*.prefab')
for key,pat in [('chest','Chest_1.prefab'),('crystal','Crystal_2.prefab'),('potion','Potion_4_1.prefab'),('barrel','Barrel_1_1.prefab'),('door','Waals_Doors.prefab')]:add(key,'032',pat)
add('car','009','Taxi_3_MC_B.prefab')
add('chair','007','Chair_1_A_*.prefab');add('sofa','007','Armchair_1_A_*.prefab')
add('table','007','Table_1_A_*.prefab');add('cup','007','CoffyCup_P_*.prefab')
add('tree','023','EA04_Tree*Bowl*01a*.prefab')
add('blaster','076','SM_Blaster_1_A_SW_*.prefab')
data=dict(checkedOnKst='2026-10-28',rightsEvidence='Official publisher product pages checked on 2026-10-28; product032 included License.txt SHA a2267ca0048c3e42a808ab3dee662ff6ea713f9fdb15420a13789b798007dd19. Credit kept in description-bottom provenance; no vendor source files added to Git.',assets=items)
out=U/'Assets/VideoScenes/design-25-30-unity-v2/asset-map.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(H/'asset-provenance.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({x['key']:x['path'] for x in items},ensure_ascii=False,indent=2))
