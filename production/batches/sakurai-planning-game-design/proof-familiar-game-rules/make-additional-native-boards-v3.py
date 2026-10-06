import json,pathlib,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=pathlib.Path(__file__).resolve().parent
state=json.loads((BASE/'additional-source-execution-v3.json').read_text(encoding='utf-8'))
assert state['status']=='additional-native-extracted-awaiting-direct-review'
assert all(c['exitCode']==0 for c in state['children'])
out=ROOT/'shared/output/familiar-game-rules/research/additional-native-v3/boards'
assert not out.exists(),'Inspect existing boards instead of repeating'
out.mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
records=[]
for source in state['results']:
    assert source['fullDecodeExitCode']==0
    for offset in range(0,len(source['nativeFrames']),6):
        board=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(board);tiles=[]
        for local,f in enumerate(source['nativeFrames'][offset:offset+6]):
            p=ROOT/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
            im=Image.open(p);assert im.size==(960,540)
            x=(local%2)*960;y=(local//2)*570;board.paste(im,(x,y+30))
            draw.text((x+8,y+3),f'{source["videoId"]} n={f["sourceFrame"]} t={f["seconds"]:.6f}s',font=font,fill='black');tiles.append(f)
        target=out/f'{source["videoId"]}-{offset//6+1:02}.jpg';board.save(target,quality=95)
        records.append({'sourceId':source['videoId'],'board':str(target.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'tiles':tiles,'directlyRead':False})
result={'schemaVersion':1,'slug':'familiar-game-rules','boards':records,'boardCount':len(records),'frameCount':sum(len(b['tiles']) for b in records),'allDirectlyRead':False,'exactCutApproval':False,'imagesGitPolicy':'local-only','sourceFrameStep':30,'timing':'rational source-frame index; Each time is derived from actual rational source fps; precise edges require separate review; precise edges require separate review'}
(BASE/'additional-native-boards-v3.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'boards':result['boardCount'],'frames':result['frameCount']}))
