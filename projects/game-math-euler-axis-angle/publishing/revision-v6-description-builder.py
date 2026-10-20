"""Local V6 descriptions only; never reads/uploads a video or mutates Studio receipts.

Default: wait for a measured current41-scene timeline and create final local text.
--draft: omit chapters until measured timing exists; mark the receipt incomplete.
Canonical footer content is read from the same inputs as the shared assembler.
"""
from pathlib import Path
import argparse, hashlib, json, math, re

R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-math-euler-axis-angle'
PUB = P / 'publishing'
PLAN = PUB / 'revision-v6-plan.json'
SHARED = R / 'scripts/prepare-youtube-upload.cjs'
DEFAULTS = R / 'shared/publishing/youtube-defaults.json'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.resolve().relative_to(R).as_posix()
def utf16_length(text): return len(text.encode('utf-16-le')) // 2

def footers(defaults):
    ko = (R / defaults['description']['channelDefaultSnapshot']).read_text(encoding='utf-8-sig').split('📚 수업 노트')[0].strip()
    shared = SHARED.read_text(encoding='utf-8-sig')
    match = re.search(r'const footerEn = `([\s\S]*?)`;', shared)
    assert match, 'Shared EN footer changed; review its current contract before building'
    en = match.group(1).replace('${defaults.coaching.url}', defaults['coaching']['url']).replace('${defaults.membershipUrl}', defaults['membershipUrl'])
    assert '${' not in en, 'Unrecognized shared footer interpolation; do not invent a replacement'
    assert 'ノーション' not in ko and '여기에-GitHub' not in ko
    return {'ko':ko.replace('\r\n','\n'), 'en':en.replace('\r\n','\n')}

def time_text(frame, fps):
    seconds = frame // fps
    hours, seconds = divmod(seconds,3600)
    minutes, seconds = divmod(seconds,60)
    return f'{hours}:{minutes:02d}:{seconds:02d}' if hours else f'{minutes:02d}:{seconds:02d}'

def chapter_rows(plan, timeline):
    assert timeline['revision'] == 'article-flow-v6'
    assert timeline['slug'] == 'game-math-euler-axis-angle'
    assert timeline['timing'] == 'measured-and-asr-aligned'
    assert timeline['fps'] == 60 and timeline['introFrames'] == 120 and timeline['outroFrames'] == 600
    script = P / 'script/revision-v6-article-flow/narration.ko.json'
    assert timeline['inputs']['koSha256'] == sha(script), 'Stale timeline/script correspondence'
    scenes = {x['id']:x for x in timeline['scenes']}
    assert len(scenes) == 41 and timeline['sceneCount'] == 41
    rows=[]
    for entry in plan['chapterPlan']:
        frame = (timeline['temporalContract']['outroStartFrame'] if entry.get('membershipOutro') else 0 if entry.get('startsAtBranding') else scenes[entry['scene']]['startFrame'])
        assert isinstance(frame,int) and frame >= 0
        rows.append({**entry,'globalFrame':frame,'display':time_text(frame,60),'seconds':frame//60})
    assert rows[0]['globalFrame'] == 0 and len(rows) >= 3
    for before,after in zip(rows,rows[1:]):
        assert after['seconds']-before['seconds'] >= 10, 'Chapter is too short; group related scenes rather than inventing timestamps'
    assert timeline['totalFrames']-rows[-1]['globalFrame'] >= 600
    return rows

def assemble(plan, defaults, rows):
    footer=footers(defaults)
    result={}
    for language,heading in [('ko','출처·자료 및 제작 도구'),('en','Sources, assets and production tools')]:
        body=plan['descriptionBody'][language].strip()
        if rows:
            body += '\n\n' + ('챕터' if language=='ko' else 'Chapters') + '\n' + '\n'.join(f"{c['display']} {c[language]}" for c in rows)
        credits=plan['sourceCredits'][language].strip()
        description='\n\n'.join([body,footer[language],heading+'\n'+credits])
        assert description.endswith(credits), 'Nothing may follow source credits'
        for url in plan['requiredCanonicalLinks'].values():
            assert description.count(url)==1, (language,'Missing/duplicate canonical footer link',url)
        assert 'source-video' not in body and '원영상' not in body and '사쿠라이' not in body
        assert 'actual40' not in description and '게임40%' not in description and 'placeholder' not in description.lower()
        assert len(description)<=5000 and utf16_length(description)<=5000, (language,len(description),utf16_length(description),'Do not truncate attribution; edit explicitly')
        result[language]={'body':body,'sourceCredits':credits,'description':description,'characters':len(description),'utf16CodeUnits':utf16_length(description)}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',type=Path,default=P/'production/revision-v6/timeline.json');ap.add_argument('--draft',action='store_true');args=ap.parse_args()
    plan=read(PLAN);defaults=read(DEFAULTS)
    chosen=next(x for x in plan['titleCandidates'] if x['id']==plan['selectedTitleCandidate'])
    assert len(plan['titleCandidates'])==3
    for candidate in plan['titleCandidates']:
        assert all(utf16_length(candidate[k])<=100 for k in ['ko','en'])
    assert defaults['coaching']['url']==plan['requiredCanonicalLinks']['coaching']
    assert defaults['membershipUrl']==plan['requiredCanonicalLinks']['membership']
    rows=[] if args.draft else chapter_rows(plan,read(args.timeline))
    built=assemble(plan,defaults,rows)
    # Capacity check only: no invented timestamp is ever written to a description.
    worst_case_rows=[{**x,'display':'00:00:00'} for x in plan['chapterPlan']]
    assemble(plan,defaults,worst_case_rows)
    suffix='.draft' if args.draft else ''
    outputs={}
    for language,row in built.items():
        path=PUB/f'revision-v6-description{suffix}.{language}.txt'
        path.write_text(row['description']+'\n',encoding='utf-8')
        outputs[language]={'file':rel(path),'sha256':sha(path),'characters':row['characters'],'utf16CodeUnits':row['utf16CodeUnits']}
    evidence=[{'file':path,'sha256':sha(R/path)} for path in plan['sourceEvidence']]
    receipt={
        'revision':'article-flow-v6','status':'draft without chapter timestamps' if args.draft else 'local descriptions built from measured timeline; final delivery/human review still pending',
        'platformMutationPerformed':False,'uploadAuthorizedByThisBuild':False,'finalMasterSha256':None,'humanReview':'pending',
        'inputs':{'plan':{'file':rel(PLAN),'sha256':sha(PLAN)},'builder':{'file':rel(Path(__file__)),'sha256':sha(Path(__file__))},'sharedAssembler':{'file':rel(SHARED),'sha256':sha(SHARED)},'defaults':{'file':rel(DEFAULTS),'sha256':sha(DEFAULTS)},'canonicalKoFooter':{'file':defaults['description']['channelDefaultSnapshot'],'sha256':sha(R/defaults['description']['channelDefaultSnapshot'])},'timeline':None if args.draft else {'file':rel(args.timeline),'sha256':sha(args.timeline)}},
        'metadata':{'title':chosen['ko'],'description':built['ko']['description'],'privacyStatus':'private','language':'ko'},
        'englishMetadata':{'title':chosen['en'],'description':built['en']['description']},
        'descriptionBody':{k:v['body'] for k,v in built.items()},'sourceCredits':{k:v['sourceCredits'] for k,v in built.items()},
        'sourceEvidence':evidence,'sourceCreditsPolicy':'description-sources-last-v1','chapterRows':rows,'chapterTimingStatus':'pending actual measured timeline' if args.draft else 'measured current V6 frame mapping',
        'outputs':outputs,'checks':{'canonicalLinksOnce':True,'sourcesAtAbsoluteBottomBothLanguages':True,'noUnfilledNotesOrGithub':True,'allTitlesWithin100Utf16Units':True,'bothDescriptionsWithin5000Utf16Units':True,'capacityWithActualChapterCountAndLongTimeFormat':True},
        'sharedAssemblerHandoff':'descriptionBody/sourceCredits/title fields are ready for a future revision-specific receipt; preserve same reviewed captioned SHA and run shared preparation only after actual user review. No existing upload receipt was changed.'}
    out=PUB/f'revision-v6-description{suffix}-build.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'receipt':rel(out),'sha256':sha(out),'outputs':outputs,'chapters':len(rows),'externalUploadPerformed':False},indent=2))

if __name__=='__main__':main()
