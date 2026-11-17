"""Recheck every actual saved column and original navigation/media before handoff."""
from pathlib import Path
import json,re,hashlib
from collections import Counter
from PIL import Image

B=Path(__file__).resolve().parent
IMG=r'<image source="[^"]+"\s*/>(?:\s*<i>[\s\S]*?</i>)?|<image source="[^"]+">[\s\S]*?</image>'

def main():
    p=json.loads((B/'progress.json').read_text(encoding='utf8'))
    media=json.loads((B/'media-uploaded.json').read_text(encoding='utf8'))
    assert len(p['rows'])==len({x['id'] for x in p['rows']})==113
    mismatches=[];rows=[]
    for r in p['rows']:
        k=r['id'];assert r['status']=='column-saved-and-readback-verified',k
        saved=(B/r['columnArticle']).read_text(encoding='utf8').strip()
        old=(B.parent/'articles'/f'{k}.md').read_text(encoding='utf8').strip()
        assert saved!=old and '{{' not in saved,k
        assert not re.search(r'[ぁ-んァ-ヶ]',saved),k
        assert saved.count('<image ')==r['imageCount'],k
        for block in re.findall(IMG,old):assert block in saved,(k,'original image/caption lost')
        for block in re.findall(r'<video source="[^"]+"[^>]*>',old):assert block in saved,(k,'video changed')
        nav='## 이어서 읽기'+old.split('## 이어서 읽기',1)[1]
        assert nav in saved,(k,'navigation changed')
        for block in re.findall(r'```mermaid[^\n]*\n[\s\S]*?```',old):assert block in saved,(k,'original diagram lost')
        rows.append(dict(id=k,series=r['series'],pageId=r['pageId'],images=r['imageCount'],originalMediaAndNavigationPreserved=True,savedReadbackEvidence=r['verification'],userReview='pending'))
    for m in media:
        path=Path(m['path']);assert path.is_file(),m['key']
        with Image.open(path) as im:
            if m.get('kind')=='authored-explanatory-model':assert im.size==(1200,1000),m['key']
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if m.get('sha256') and actual!=m['sha256']:mismatches.append(m['key'])
    result=dict(status='all-notion-columns-saved-internally-reviewed-user-review-pending',checkedOn='2026-11-18',pages=len(rows),series=dict(Counter(r['series'] for r in rows)),imageBlocks=sum(r['images'] for r in rows),newAuthoredFigures=sum(m.get('kind')=='authored-explanatory-model' for m in media),licensedExternalFigures=sum(bool(m.get('license')) for m in media),allOriginalMediaAndNavigationPreserved=True,notionReadbacksChecked=True,publicWebsite='Separate browser check; one late-updated sample still showed cached baseline, so full public-site revision rollout is not claimed.',screenshotCapture='IAB screenshot capture unavailable; native Notion accessibility view showed new DL02 heading and content.',localMediaHashDifferences=mismatches,rows=rows)
    (B/'final-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False))

if __name__=='__main__':main()
