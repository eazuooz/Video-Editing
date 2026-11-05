"""Read-only, seekable review of this Short's delivered files on this computer."""
import sys
from pathlib import Path
import json
from aiohttp import web
folder=Path(json.loads((Path(__file__).parent/'project.json').read_text(encoding='utf8'))['mediaRoot'])/'final-reviewed-v2'
files={'index.html','captioned.mp4','clean.mp4','captions.ko.srt','captions.en.srt','mobile.mp4','delivery.json','SHA256SUMS.txt','Freedoom-COPYING.txt'}
async def get_file(request):
    name=request.match_info['name'] or 'index.html'
    if name not in files or not (folder/name).is_file():raise web.HTTPNotFound()
    return web.FileResponse(folder/name,headers={'Cache-Control':'no-cache'})
if __name__=='__main__':
    app=web.Application()
    app.router.add_get('/{name:.*}',get_file);web.run_app(app,host='127.0.0.1',port=int(sys.argv[1]))
