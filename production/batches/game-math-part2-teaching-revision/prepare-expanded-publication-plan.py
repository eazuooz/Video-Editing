"""Plans only: never reserve an unfinished ID or silently displace a baseline."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
q=read(B/'queue.json');policy=read(ROOT/'shared/publishing/daily-alternating-schedule.json')
start=datetime.date.fromisoformat(q['items'][0]['baseline']['date']);rows=[]
for item in q['items']:
    episodes=item['revision'].get('episodeSlugs') or [None]
    for number,slug in enumerate(episodes,1):
        date=start+datetime.timedelta(days=2*len(rows))
        assert (date-datetime.date(2026,10,11)).days%2==0
        current=next((x['baseline']['videoId'] for x in q['items'] if x['baseline']['date']==date.isoformat()),None)
        rows.append({'order':len(rows)+1,'baselineChapter':item['slug'],'episode':number,'episodeSlug':slug,'plannedDate':date.isoformat(),'time':'09:00','timezone':'Asia/Seoul','currentBaselineOccupant':current,'actualRevisionVideoId':(item['revision']['videoIds'][number-1] if len(item['revision']['videoIds'])>=number else None),'platformScheduleSaved':False,'status':'plan only; current schedules preserved','coverageNeedsMeasuredNarration':slug is None})
plan={'createdAt':datetime.datetime.now().astimezone().isoformat(),'policy':'shared/publishing/daily-alternating-schedule.json','anchor':'2026-10-11 game lecture; alternating09:00KST','minimumEpisodeCount':len(rows),'additionalConceptualSplitsMayExtendPlan':True,'episodes':rows,'transition':'Read current Studio before each assignment. Release an original baseline only after that chapter is fully covered by reviewed private revisions and Git delivery. Do not take a slot while its existing occupant still lacks a reviewed replacement. Execute ordered collision-free transitions; preserve original files/receipts and unrelated/published videos.','platformMutations':False,'fullBatchCompleted':False}
(B/'expanded-publication-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'plannedMinimumEpisodes':len(rows),'platformMutations':False}))
