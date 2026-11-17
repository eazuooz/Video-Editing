"""Join independently written columns to reviewed media and existing stable navigation."""
import json,re,hashlib,argparse
from pathlib import Path

HERE=Path(__file__).resolve().parent
EVIDENCE=HERE.parent/'evidence/column-v2'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',default='first-four');args=parser.parse_args()
    before=json.loads((EVIDENCE/('before-'+args.batch+'.json')).read_text(encoding='utf8'))
    uploaded=json.loads((HERE/'media-uploaded.json').read_text(encoding='utf8'))
    result=[]
    for item in before:
        key=item['id'];page=item['data']
        old=re.search(r'<content>\n([\s\S]*?)\n</content>',page['text'])[1]
        baseline=(HERE.parent/'articles'/f'{key}.md').read_text(encoding='utf8').strip()
        assert old.strip()==baseline, (key,'Concurrent article edit: reconcile before replacing')
        prefix=re.sub(r'<image source="[^"]+">[\s\S]*?</image>','',old.split('\n## ',1)[0]).strip()
        navigation='## 이어서 읽기'+old.split('## 이어서 읽기',1)[1]
        original_images=re.findall(r'<image source="[^"]+">[\s\S]*?</image>',old)
        draft=(HERE/'articles'/f'{key}.md').read_text(encoding='utf8')
        assert not re.search(r'[ぁ-んァ-ヶ]',draft),(key,'unexpected Japanese prose in Korean column')
        for i,image in enumerate(original_images):
            placeholder='{{existing_image_'+str(i)+'}}'
            assert placeholder in draft,(key,'existing image must be preserved',i)
            draft=draft.replace(placeholder,image)
        for i,diagram in enumerate(re.findall(r'```mermaid[^\n]*\n[\s\S]*?```',old)):
            placeholder='{{existing_mermaid_'+str(i)+'}}'
            assert placeholder in draft,(key,'existing diagram must be preserved',i)
            draft=draft.replace(placeholder,diagram)
        for meta in uploaded:
            if meta['article']!=key:continue
            placeholder='{{'+meta['key']+'}}'
            assert placeholder in draft,(key,'unused new media',meta['key'])
            draft=draft.replace(placeholder,'<image source="'+meta['markdownSource']+'">\n'+meta['caption']+'\n</image>')
        draft=draft.replace('{{video_and_navigation}}',navigation)
        assert '{{' not in draft,(key,'unfilled marker')
        content=prefix+'\n\n'+draft
        assert content!=old and len(content)>2500,key
        (HERE/'articles'/f'{key}.prepared.md').write_text(content,encoding='utf8')
        result.append(dict(id=key,pageId=page['id'],title=page['title'],content=content,
            oldChars=len(old),newChars=len(content),oldSha256=hashlib.sha256(old.encode()).hexdigest(),
            newSha256=hashlib.sha256(content.encode()).hexdigest(),
            imageCount=len(re.findall(r'<image source=',content)),
            changes='Independent column; continuous concrete case; explained state/variables; process diagrams; troubleshooting; primary references; existing images/video/navigation retained.'))
    (HERE/('payload-'+args.batch+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{k:r[k] for k in ['id','oldChars','newChars','imageCount']} for r in result]))

if __name__=='__main__':main()
