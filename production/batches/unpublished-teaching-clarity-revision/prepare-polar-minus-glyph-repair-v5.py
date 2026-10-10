"""Prepare a narrowly scoped glyph repair for scene11/16, preserving v4.

Malgun has no U+2212 in its cmap. Use its supported ASCII subtraction sign
only in editorial labels. The mathematical claims, PCM and cue timing stay.
"""
from pathlib import Path
import importlib.util, json
from datetime import datetime, timezone
from PIL import Image
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/minus-glyph-repair-prepared-v5'
spec=importlib.util.spec_from_file_location('minus_repair_v4',Path(__file__).with_name('prepare-polar-remaining-annotations-v4.py'))
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
sha,rel=previous.sha,previous.rel
original_label=previous.label
def label(d,xy,text,color='white',size=30):
    return original_label(d,xy,text.replace('\u2212','-'),color,size)
for m in [previous,previous.previous,previous.v2,previous.v1,previous.base,previous.base.base]:
    m.label=label
annotate=previous.annotate
def main():
    cmap=TTFont('C:/Windows/Fonts/malgun.ttf').getBestCmap()
    assert 0x2212 not in cmap and ord('-') in cmap
    proofpath=OUT/'minus-glyph-repair-preparation-v5.json';assert not proofpath.exists()
    state=json.loads((OUT/'six-moving-pilots-execution-v4.json').read_text(encoding='utf-8'))
    assert state['status']=='completed' and state['exitCode']==0
    prepared=json.loads((OUT/'remaining-editorial-annotation-preparation-v4.json').read_text(encoding='utf-8'))
    LOCAL.mkdir(parents=True,exist_ok=False);jobs=[]
    for sid,frame in [('11',1500),('16',1200)]:
        old=next(j for j in prepared['jobs'] if j['scene']==sid)
        oldplan=ROOT/old['plan'];assert sha(oldplan)==old['planSha256']
        plan=json.loads(oldplan.read_text(encoding='utf-8'))
        plan.update(previousPlan=rel(oldplan),previousPlanSha256=sha(oldplan),
                    glyphRepair={'from':'U+2212 unsupported by Malgun','to':'ASCII hyphen-minus subtraction','claimsChanged':False},
                    sampledLayoutApproved=False,movingTrackApproved=False)
        p=OUT/f'scene{sid}-editorial-annotations-v5.json';assert not p.exists()
        p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # Existing coarse source pixels are reused, no frame extraction.
        oldsource=json.loads((OUT/'action-clarity-execution-v3.json').read_text(encoding='utf-8'))
        row=min(next(j for j in oldsource['jobs'] if str(j['scene'])==sid)['records'],key=lambda r:abs(r['frame']-frame))
        assert sha(ROOT/row['path'])==row['sha256']
        with Image.open(ROOT/row['path']) as im:res=annotate(im,row['frame'],plan)
        sample=LOCAL/f'scene{sid}-minus-fixed.png';res.save(sample)
        jobs.append({'scene':sid,'plan':rel(p),'planSha256':sha(p),
                     'sample':{'frame':row['frame'],'path':rel(sample),'sha256':sha(sample)},
                     'preparedOnly':True,'currentMovingPixelsApproved':False})
    proofpath.write_text(json.dumps({'preparedAt':datetime.now(timezone.utc).isoformat(),'jobs':jobs,
       'fontCmapEvidence':{'U+2212':None,'ASCII-minus':cmap[ord('-')]},'historyPreserved':True,
       'narrationChanged':False,'allFinalPixelsApproved':False,'imageGitAdded':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preparedScenes':['11','16'],'movingApproved':False}))
if __name__=='__main__':main()
