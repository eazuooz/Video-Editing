"""Serve the current nine review masters on the original review URL."""
import importlib.util
import sys
from aiohttp import web
from render import MEDIA, DIRECTORY, EDITS, SOURCES, SPEC, HERE, editor
from pathlib import Path

loader=importlib.util.spec_from_file_location('overview',HERE.parent/'build-review-overview.py')
overview=importlib.util.module_from_spec(loader)
loader.loader.exec_module(overview)
names=set(overview.FILES)|{'index.html','mobile-review.mp4','metadata.json','delivery.json','SHA256SUMS.txt'}
prefixes={r['slug']:Path(r['finalDirectory']).parent/DIRECTORY for n,r in SOURCES.items() if n in EDITS}
def records():
    rows=[]
    for n,e in EDITS.items():
        src=SOURCES[n]
        folder=prefixes[src['slug']]
        complete=(folder/'feedback-check.json').is_file() and (folder/'delivery.json').is_file()
        row=dict(order=n,slug=src['slug'],description=src['description'],title=e['title'],generated=complete)
        if complete:
            item=editor.read(folder/'delivery.json')
            row.update(description=item['description'],seconds=item['durationSeconds'],revision=item['revision'],
                       visualVersion=item['revision'],finalDirectory=str(folder),review=str(folder/'index.html'),
                       masterSha256=item['files'][1]['sha256'],files=item['files'])
        rows.append(row)
    return dict(total=len(rows),completeCount=sum(row['generated'] for row in rows),projects=rows)
async def handle(request):
    if request.path=='/':raise web.HTTPFound('/delivery/review-ten.html')
    if request.path in ['/delivery/review-ten.html','/delivery/review-ten.json']:
        data=records()
        if request.path.endswith('.html'):
            return web.Response(text=overview.render(data,MEDIA/'delivery'),content_type='text/html',headers={'Cache-Control':'no-store'})
        current=MEDIA/'delivery/review-ten.json'
        if current.exists() and data['completeCount']==data['total']:
            saved=editor.read(current)
            if [r.get('masterSha256') for r in saved['projects']]==[r.get('masterSha256') for r in data['projects']]:
                return web.FileResponse(current,headers={'Cache-Control':'no-cache'})
        return web.json_response(data,headers={'Cache-Control':'no-store'})
    pieces=request.path.strip('/').split('/')
    if pieces[0]==SOURCES[8]['slug']:raise web.HTTPGone()
    if len(pieces)!=4:raise web.HTTPNotFound()
    slug,local,version,name=pieces
    folder=prefixes.get(slug)
    if local!='local' or not folder or name not in names:raise web.HTTPNotFound()
    if version!=DIRECTORY:raise web.HTTPFound(f'/{slug}/local/{DIRECTORY}/{name}')
    if not (folder/'feedback-check.json').exists() or not (folder/name).is_file():raise web.HTTPNotFound()
    return web.FileResponse(folder/name,headers={'Cache-Control':'no-cache'})
if __name__=='__main__':
    app=web.Application()
    app.router.add_get('/{tail:.*}',handle)
    web.run_app(app,host='127.0.0.1',port=int(sys.argv[1]))
