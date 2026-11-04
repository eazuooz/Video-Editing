"""Index exact Notion fetch results; downloading is not a completed content audit."""
from pathlib import Path
import json,hashlib,re
BASE=Path(__file__).parent
rows=[]
for path in sorted((BASE/'sources').glob('*.json')):
    if path.name=='index.json':continue
    wrapper=json.loads(path.read_text(encoding='utf-8-sig'))
    obj=json.loads(next(x['text'] for x in wrapper['content'] if x['type']=='text'))
    text=obj['text']
    target=path.with_suffix('.notion.txt')
    target.write_text(text,encoding='utf-8')
    rows.append({'id':obj['id'],'title':obj['title'],'url':obj['url'],'textFile':target.name,'characters':len(text),'sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),'pageLastEditedAt':obj.get('page_last_edited_at'),'fetchAsOf':re.search(r'as of ([^:]+T[^:]+:[^:]+:[^:]+):',text).group(1) if re.search(r'as of ([^:]+T[^:]+:[^:]+:[^:]+):',text) else None,'truncatedField':obj.get('truncated','not-reported'),'unknownBlockCount':obj.get('unknown_block_count','not-reported'),'hasClosingPage':text.rstrip().endswith('</page>'),'contentReview':'pending full paragraph audit by episode','headers':[line for line in text.splitlines() if re.match(r'^#{1,6} ',line)]})
(BASE/'sources/index.json').write_text(json.dumps({'provenance':'Connected Notion fetch snapshots. Fetch as-of and page edit times retained; no claim of a fresher live revision than tool returned.','sources':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} full fetch snapshots indexed; {sum(x["characters"] for x in rows)} characters. Content audit remains separate.')
