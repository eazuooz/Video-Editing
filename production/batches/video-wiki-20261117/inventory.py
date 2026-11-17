"""Inventory existing authored lessons without starting production or changing YouTube."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Github/VideoEditing')
HERE = Path(__file__).resolve().parent


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def paths_in(d, suffix):
    if isinstance(d, str) and d.lower().endswith(suffix):
        yield d
    elif isinstance(d, dict):
        for v in d.values():
            yield from paths_in(v, suffix)
    elif isinstance(d, list):
        for v in d:
            yield from paths_in(v, suffix)


def evidence(slug):
    p = ROOT / 'projects' / slug
    project = read(p / 'project.json') if (p / 'project.json').exists() else {}
    all_paths = list(paths_in(project, '.mp4')) + list(paths_in(project, '.srt'))
    candidates = []
    for value in dict.fromkeys(all_paths):
        q = Path(value)
        if not q.is_absolute():
            q = ROOT / q
        if not q.exists():
            q = p / value
        candidates.append(dict(path=value, exists=q.is_file(), resolved=str(q) if q.is_file() else None))
    scripts = sorted(p.glob('script/**/narration*.json'))
    return dict(project=str(p / 'project.json'), currentMediaCandidates=candidates,
        scriptCandidates=[str(x) for x in scripts],
        captionCandidates=[str(x) for x in p.glob('production/**/*.ko.srt')][:60])


def main():
    ledger = read(ROOT / 'shared/publishing/video-worklist.json')
    shorts = read(ROOT / 'shared/publishing/shorts-worklist.json')
    studio = read(HERE / 'studio-shorts-inventory.json')
    existing = read(ROOT / 'docs/wiki/game-design-basics/notion-publication.json')
    known = {x.get('youtube', '').split('v=')[-1]:x for x in existing['pages'] if x.get('youtube')}
    known['5W5f6T8Hho8'] = existing['additionalPages'][0]
    rows = []
    for r in ledger['rows']:
        if r.get('series') not in ('D', 'A'):
            continue
        row = {k:r.get(k) for k in ('id','slug','title','videoId','platformStatus')}
        row.update(series='game-design' if r['series']=='D' else 'game-animation',
            status='source-review-pending', existingPage=known.get(r.get('videoId')),
            sourceEvidence=evidence(r['slug']))
        rows.append(row)
    for ident, slug, vid in [
        ('DL01','let-them-play','bSPwEfdU_JI'),
        ('DL02','jump-physics','_j3H7lg4p1s')]:
        rows.append(dict(id=ident,slug=slug,title=known[vid]['properties']['title'],videoId=vid,
            series='game-design',status='existing-article-review-pending',existingPage=known[vid],sourceEvidence=evidence(slug)))
    modern = {}
    for r in shorts['rows']:
        auth=r.get('authorization')
        vid = r.get('youtubeId') or r.get('videoId') or (auth.get('youtubeId') if isinstance(auth,dict) else None)
        if vid:
            modern[vid] = r
    # Match older ledgers' IDs only against an actual recorded publishing receipt.
    for r in shorts['rows']:
        p = ROOT/'projects'/r['slug']/'publishing'
        for q in p.glob('*.json'):
            try:
                d=read(q)
            except (ValueError,OSError):
                continue
            for k in ('videoId','youtubeId','actualVideoId'):
                if d.get(k) in {x['videoId'] for x in studio}:
                    modern[d[k]]=r
    non_learning = {'cGxb7mmUVOM','m-NIAFKwz7Q','CH3wip7CYZw','TZsXDiVJazQ','0Ovl9MhcvAY',
        'R2ljQmoj3NQ','pm3yfmCj__E','WRtX5UldcyI','3z_ZqroumYc','XZTZyoU3w-Y',
        'U742rI3wpbI','BS6RTsw_tII','-Y5BLRRILOE','Vqi87w4BjyQ','pQgf73xjOdQ'}
    excluded=[]
    for i,s in enumerate(studio):
        if s['videoId'] in non_learning:
            excluded.append(dict(videoId=s['videoId'],title=s['text'].splitlines()[1],reason='Personal pet, music/concert or reaction meme; no teaching article inferred from it.'))
            continue
        r=modern.get(s['videoId'])
        rows.append(dict(id=f'S{i+1:02}',slug=r['slug'] if r else 'legacy-short-'+s['videoId'],
            series='shorts',title=s['text'].splitlines()[1],videoId=s['videoId'],
            status='source-review-pending',studioText=s['text'],
            sourceEvidence=evidence(r['slug']) if r else {'originalVideoRequired':True}))
    write(HERE/'inventory.json',dict(status='source-and-article-review-in-progress',
        scope='existing game-design, game-animation and educational Shorts',
        wikiRoot='https://app.notion.com/p/0d2adf455d1a43bea37c61c94b1ae2c8',
        existingDesignHub='https://app.notion.com/p/3de0b1ffa61e80f4b411f7f227d52b43',
        rows=rows,excluded=excluded,studioShortsCount=79))
    control=read(ROOT/'shared/publishing/video-production-control.json')
    control['videoCompanionWikiPolicy20261117']=dict(id='video-companion-wiki-v1',
        userEvidence='앞으로 항상 영상제작되면 위키 상세 글까지 완료. 영상 이미지 활용 우선. 비디오에이전트(영상) 대화에도 추가.',
        requiredForVideoCompletion=True,onePagePerLogicalVideo=True,
        existingPagesPreserved=True,videoFramesPreferred=True,
        document='docs/VIDEO_WIKI_WORKFLOW.md',youtubeChangesAuthorized=False)
    control.setdefault('scopedDocumentationAuthorizations',{})['videoWiki20261117']=dict(
        status='in-progress',scope='Existing game-design, game-animation and educational Shorts; detailed Notion articles, frames and series navigation.',
        inventory=str(HERE/'inventory.json'),videoProduction=False,youtubeActions=False,
        userRequestedAgentNotification='Video Agent1 (영상)',preserveUnrelatedWork=True)
    write(ROOT/'shared/publishing/video-production-control.json',control)
    print('Inventoried',len(rows),'learning items;',len(excluded),'non-learning Shorts retained in exclusion ledger.')


if __name__=='__main__':
    main()
