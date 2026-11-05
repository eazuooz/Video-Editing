"""Loopback-only review for these exact edits; newly verified local files become playable without restarting."""
from build import *
from aiohttp import web
from urllib.parse import quote
from pathlib import PurePosixPath
import importlib.util,sys
spec=importlib.util.spec_from_file_location('overview',HERE.parent/'build-review-overview.py');overview=importlib.util.module_from_spec(spec);spec.loader.exec_module(overview)
DIR='final-reviewed-feedback-nov05-r2'
def getrows():
    rows=[]
    for r,e in zip(BASE,ED):
        p=Path(r['finalDirectory']).parent/DIR;exists=(p/'delivery.json').is_file() and (p/'feedback-check.json').is_file()
        row=dict(order=r['order'],slug=r['slug'],title=e['title'],description=r['description'],generated=exists)
        if exists:
            d=read(p/'delivery.json');row.update(seconds=d['durationSeconds'],revision=d['revision'],visualVersion=d['revision'],finalDirectory=str(p),review=str(p/'index.html'),masterSha256=d['files'][1]['sha256'],description=d['description'],files=d['files'])
        rows.append(row)
    return dict(completeCount=sum(r['generated'] for r in rows),projects=rows)
allowed={('/'+r['slug']+'/local/'+DIR+'/'+k):(Path(r['finalDirectory']).parent/DIR/k) for r in BASE for k in [*FILES,'index.html','mobile-review.mp4','delivery.json','metadata.json','SHA256SUMS.txt']}
async def access(req):
    if req.path=='/':raise web.HTTPFound('/delivery/review-ten.html')
    if req.path in ['/delivery/review-ten.html','/delivery/review-ten.json']:
        rows=getrows()
        if req.path.endswith('.json'):return web.json_response(rows)
        return web.Response(text=overview.render(rows,MEDIA/'delivery'),content_type='text/html',headers={'Cache-Control':'no-store'})
    p=allowed.get(req.path)
    if not p or not p.is_file() or not (p.parent/'feedback-check.json').exists():raise web.HTTPNotFound()
    return web.FileResponse(p,headers={'Cache-Control':'no-cache'})
if __name__=='__main__':
    app=web.Application();app.router.add_get('/{path:.*}',access);web.run_app(app,host='127.0.0.1',port=int(sys.argv[1]) if len(sys.argv)>1 else 9359)
