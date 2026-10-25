"""Align provisional openings with actual inspected release / legacy footage."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
DATA={
 'shorts-d2r-ultrawide-ai-range':{
 0:[('디아블로 투 레저렉션,','Diablo II: Resurrected.'),('화면을 더 넓히면 무조건 좋을까요?','Is a wider screen always better?')],
 1:[('이천이십일 년 테스트에서는 화면을 스물하나 대 아홉까지 넓혔습니다.','In the 2021 test, the view extended to twenty-one by nine.'),('캐릭터와 몬스터는 그대로 두고,','Keep the player and monster in place.'),('화면만 옆으로 넓히면 더 먼 적이 보이죠.','Widening only the view reveals a more distant enemy.')]
 },
 'shorts-d2-modular-sprite-equipment':{
 0:[('디아블로 투 원작의 캐릭터,','The original Diablo II character:'),('갑옷마다 통째로 다시 그렸을까요?','did they redraw the whole character for every armor combination?')]
 }
}
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug,changes in DATA.items():
 p=ROOT/'projects'/slug
 old=read(p/'script/clauses.json')
 paragraphs=[]
 for i in range(6):paragraphs.append(changes.get(i,[(c['spoken'],c['en']) for c in old['clauses'] if c['lineIndex']==i]))
 clauses=[dict(id=f'p{i+1}-{j+1}',lineIndex=i,spoken=ko,ko=ko.replace('디아블로 투 레저렉션','디아블로 II: 레저렉션').replace('디아블로 투','디아블로 II'),en=en) for i,para in enumerate(paragraphs) for j,(ko,en) in enumerate(para)]
 lines=[' '.join(c[0] for c in para) for para in paragraphs]
 eng=[' '.join(c[1] for c in para) for para in paragraphs]
 write(p/'script/clauses.json',dict(clauses=clauses,pronunciationAliases={'디아블로 II':'디아블로 투','21:9':'스물하나 대 아홉','19:9':'십구 대 구'}))
 narration=read(p/'script/narration.spoken.ko.json');narration['scenes'][0]['lines']=lines;write(p/'script/narration.spoken.ko.json',narration)
 for lang,paras in [('ko',lines),('en',eng)]: (p/f'script/narration.{lang}.txt').write_text('\n\n'.join(paras)+'\n',encoding='utf8')
 plan=read(p/'planning/production-plan.json')
 for i,row in enumerate(plan['scenePlan']):row['speech']=lines[i]
 plan['scriptRevisionReason']='Opening now uses inspected ordinary release/legacy gameplay only as the setting. The historical alpha defect or equipment composition is taught in explicitly authored diagrams, never mislabeled as observed gameplay.'
 plan['headingFreeScriptReadthrough']={'ko':True,'en':True,'preserved':'Primary-source mechanism and limits; opening wording corrected to match observed source','audioListening':False}
 write(p/'planning/production-plan.json',plan)
 timing=read(p/'production/visual-timing.json')
 if timing['status']!='provisional-not-audio-aligned':raise RuntimeError('PCM timing exists: do not replace it.')
 cursor=0
 for i,row in enumerate(timing['sections']):
  end=round((cursor+max(5,len(lines[i])/11+1))*60)/60
  row.update(start=cursor,end=end,startFrame=round(cursor*60),endFrame=round(end*60));cursor=end
 timing.update(durationSeconds=cursor,frames=round(cursor*60),reactions=[{'start':timing['sections'][2]['start'],'end':timing['sections'][2]['start']+1.8,'kind':'realize'},{'start':timing['sections'][-1]['start'],'end':timing['sections'][-1]['start']+2,'kind':'relief'}])
 write(p/'production/visual-timing.json',timing)
 title=read(p/'project.json')['title']
 (p/'planning/outline.md').write_text('# '+title+'\n\n소스 대응 수정본 · 음성 제작 전\n\n'+'\n\n'.join(f'{i+1}. {row["id"]}\n\n{lines[i]}' for i,row in enumerate(timing['sections']))+'\n',encoding='utf8')
print(json.dumps({'updated':list(DATA),'ttsStarted':False}))
