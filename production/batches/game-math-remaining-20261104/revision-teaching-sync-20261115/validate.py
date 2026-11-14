"""Check every authored operation before the selected finite production job."""
from inventory import HERE,read,save
from boards import Board,working
from workings import WORKINGS
import motion_panels
from render_revision import additions


def main():
    failures=[];count=0;rows=[]
    for e in read(HERE/'inventory.json')['episodes']:
        b=Board()
        for s in e['scenes']:
            recipe=WORKINGS.get(e['id'],{}).get(s['scene'])
            if recipe:
                try:working(b,s,recipe);count+=1
                except Exception as error:failures.append([e['id'],s['scene'],repr(error)])
        try:motion_panels.apply(b,e,additions(e))
        except Exception as error:failures.append([e['id'],'motion',repr(error)])
        rows.extend([dict(episode=e['id'],**r) for r in b.evidence])
    zero=[r for r in rows if r['end']<=r['start']]
    save(HERE/'operation-dwell-audit.json',dict(operationCount=len(rows),nonPositive=zero,
        shortStages=[r for r in rows if r['end']-r['start']<1.5],
        scope='Individual reveals; the parent and preceding useful operation remain visible. Actual audio speed and all approved narration preserved.',
        actualHumanPaceApproval=False))
    save(HERE/'authoring-validation.json',dict(preparedSceneCount=count,failures=failures,
        operationCount=len(rows),nonPositiveStageCount=len(zero),
        actualWordEvidence='operation-word-alignment.json',finalVideoRendered=False))
    assert not failures and not zero,(failures,zero)
    print(count,'scenes,',len(rows),'ordered operations; layout/cue checks passed')


if __name__=='__main__':main()
