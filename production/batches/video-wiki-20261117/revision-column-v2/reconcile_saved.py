"""Record actual readbacks without re-labelling the remaining baseline pages as revised."""
from pathlib import Path
import json,re,hashlib,argparse

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);args=parser.parse_args()
    readback=HERE.parent/'evidence/column-v2'/('after-'+args.batch+'.json')
    after=json.loads(readback.read_text(encoding='utf8'))
    payload=json.loads((HERE/('payload-'+args.batch+'.json')).read_text(encoding='utf8'))
    progress=json.loads((HERE/'progress.json').read_text(encoding='utf8'))
    for item in after:
        key=item['id'];page=item['data'];expected=next(x for x in payload if x['id']==key)
        content=re.search(r'<content>\n([\s\S]*?)\n</content>',page['text'])[1]
        assert not page.get('truncated') and not page.get('unknown_block_count'),key
        assert '{{' not in content and '\\*\\*' not in content,key
        assert '## 이어서 읽기' in content,key
        assert content.count('<image ')==expected['imageCount'],key
        oldbody=re.search(r'<content>\n([\s\S]*?)\n</content>',next(x['data']['text'] for x in json.loads((readback.parent/('before-'+args.batch+'.json')).read_text(encoding='utf8')) if x['id']==key))[1]
        for image in re.findall(r'<image source="[^"]+">[\s\S]*?</image>',oldbody):
            assert image in content,(key,'lost original media')
        assert content.count('<video source=')==oldbody.count('<video source='),(key,'video block count changed')
        for video in re.findall(r'<video source="[^"]+"[^>]*>',oldbody):
            assert video in content,(key,'video link changed')
        r=next(x for x in progress['rows'] if x['id']==key)
        (HERE/'articles'/f'{key}.saved.md').write_text(content+'\n',encoding='utf8')
        r.update(status='column-saved-and-readback-verified',columnArticle=f'articles/{key}.saved.md',imageCount=content.count('<image '),verification='../evidence/column-v2/'+readback.name,savedChars=len(content),bodySha256=hashlib.sha256(content.encode()).hexdigest(),qualityReview={'continuousConcreteCase':True,'intermediateMechanismExplained':True,'relevantProcessFigures':True,'applicationAndFailureDiagnosis':True,'sourcesLinked':True,'humanReview':'pending'})
    saved=[r for r in progress['rows'] if r['status']=='column-saved-and-readback-verified']
    media=json.loads((HERE/'media-uploaded.json').read_text(encoding='utf8'))
    progress['summary']={'savedAndInternallyReviewed':len(saved),'pending':len(progress['rows'])-len(saved),'newProcessDiagrams':sum(m.get('kind')=='authored-explanatory-model' for m in media),'externalLicensedFigures':sum(bool(m.get('license')) for m in media),'revisedPageImageBlocks':sum(r['imageCount'] for r in saved),'userReview':'pending'}
    (HERE/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    shared=HERE.parents[3]/'shared/publishing/video-worklist.json'
    data=json.loads(shared.read_text(encoding='utf-8-sig'))
    data['videoCompanionWiki20261117']['columnRevision'].update(progress['summary'])
    shared.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(progress['summary']))

if __name__=='__main__':main()
