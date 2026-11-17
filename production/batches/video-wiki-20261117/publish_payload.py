"""Emit reviewed page payloads only; called by the connected Notion tool orchestrator."""
import argparse,json,re
from pathlib import Path
ROOT=Path('D:/Github/VideoEditing');HERE=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main(ids):
    pub=rd(HERE/'publication.json');sources={r['id']:r for r in rd(HERE/'sources.json')['rows']};inventory={r['id']:r for r in rd(HERE/'inventory.json')['rows']}
    daily=rd(HERE.parent/'longform-daily-schedule-20261117/summary.json');dates={r['videoId']:r['newKst'] for r in daily['rows']};out=[]
    for ident in ids:
        if ident in pub['pages']:continue
        d=rd(HERE/'drafts'/f'{ident}.json');assert d['status']=='editorially-reviewed-body-images-pending',ident
        src=sources[ident];hub=pub['hubs'][d['series']];notice='';vid=d['videoId']
        if vid in dates:notice='공개 예약: '+dates[vid][:10]+' 오후 7시 (한국 시간). 공개 전에는 영상 재생이 제한될 수 있습니다. 아래 내용은 글과 그림으로 읽을 수 있습니다.\n\n'
        elif '예약됨' in inventory[ident].get('studioText',''):
            m=re.search(r'20\d\d\. \d{1,2}\. \d{1,2}\.',inventory[ident]['studioText']);notice='공개 예약: '+(m.group() if m else '현재 예약 중')+' 공개 전에는 영상 재생이 제한될 수 있습니다.\n\n'
        label={'game-design':'게임 디자인 기초','game-animation':'게임 애니메이션','shorts':'게임 개발 기술 쇼츠'}[d['series']]
        footer='### 영상과 자료\n\n위 얌얌코딩 영상의 학습 내용을 읽기용으로 구성하고, 개념 설명과 적용 연습을 보충했습니다. 실제 게임에서 관찰한 장면과 원리를 보여 주는 자체 설명 모형은 구분합니다. 설명용 수치·표시는 특정 게임의 내부 실측값을 뜻하지 않습니다.'
        plan=ROOT/'projects'/src['slug']/'planning/production-plan.json'
        if plan.exists():
            pp=rd(plan);links=[]
            for item in pp.get('primarySources',[]):
                if isinstance(item,dict) and item.get('url'):links.append('- ['+(item.get('title') or item.get('author') or item.get('publisher') or '기술 자료')+']('+item['url']+')')
            if links:footer+='\n\n'+'\n'.join(links)
        content='<video source="https://www.youtube.com/watch?v='+vid+'" />\n\n<mention url="https://app.notion.com/p/'+hub.replace('-','')+'">'+label+'</mention>\n\n'+notice+d['body']+'\n\n'+footer
        out.append({'id':ident,'parent':hub,'properties':{'title':d['title']},'content':content})
    print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');main(p.parse_args().ids)
