"""Archive small verified source extracts for the on-screen editorial inserts."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import requests,json
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/newsroom-v3/sources'
def get(url):
 res=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=16);res.raise_for_status();return res
docs='https://raw.githubusercontent.com/godotengine/godot-docs/master/'
g='getting_started/step_by_step/img/nodes_and_scenes_05_editor_with_label.webp'
(L/'godot-editor.webp').write_bytes(get(docs+g).content)
print('Godot documentation screenshot:',Image.open(L/'godot-editor.webp').size)
urls={'mit':'https://raw.githubusercontent.com/godotengine/godot/master/LICENSE.txt','unity-terms':'https://unity.com/legal/editor-terms-of-service/software','unity-price':'https://unity.com/products/pricing-updates','unreal-license':'https://www.unrealengine.com/en-US/license'}
for key,url in urls.items():
 try:
  ret=get(url)
  plain=ret.text if key=='mit' else BeautifulSoup(ret.content,'html.parser').get_text(' ',strip=True)
  (L/(key+'.txt')).write_text(plain,encoding='utf-8');print(key,len(plain))
 except requests.RequestException as e:print(key,str(e))
