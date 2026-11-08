"""Build frame-exact explanation-only replacements in both timeline coordinates.

Never modifies the batch, worklist, project, captions or review manifest. Parent
integrates these silent replacements with its separately secured gameplay.
"""
from pathlib import Path
import json,ast
from sources import *
from config import EPISODES
from compose import contract
OUT=H/'replacement-plan.json'

def literal_assignments(path,names):
    result={}
    for n in ast.parse(path.read_text('utf8')).body:
        if isinstance(n,ast.Assign):
            for target in n.targets:
                if isinstance(target,ast.Name) and target.id in names:result[target.id]=ast.literal_eval(n.value)
    return result

def cuts(ep):
    p=project(ep);rev=ROWS[ep]['baselineRevision'];h=p/'production'/rev
    if ep=='A01':
        mapping=literal_assignments(h/'render_picture.py',{'SOURCES','specific'})
        plan=read(h/'edit-plan-final.json');result=[]
        for i,c in enumerate(plan['segments']):
            if c['kind'] not in ('kit','added'):continue
            key=c.get('stage')
            if not key:
                key=mapping['specific'].get(int(str(c.get('cut','E000')).split('E')[-1]),mapping['SOURCES'].get(c.get('mode'),'walk'))
            result.append({**c,'index':i,'key':key,'baselineStart':c['start'],'baselineFrames':c['frames']})
        return result,h/'edit-plan-final.json'
    path=h/('edit-plan.json'if ep=='A02'else'edit-plan-final.json');plan=read(path);result=[]
    for i,c in enumerate(plan['cuts']):
        if ep=='A02':
            if c['id'] not in ('A02-E004','A02-E011'):continue
            result.append({**c,'index':i,'key':'combat','baselineStart':c['startFrame'],'baselineFrames':c['frames'],'sizeIntroFrames':324 if c['id']=='A02-E011' else 0})
            continue
        key=c['key']
        if key not in EPISODES[ep][2]:continue
        # Preserve existing useful non-motion diagrams and the explicit 3x3 matrix.
        if (ep,key) in {('A09','bounce'),('A09','volume'),('A09','morph'),('A13','letters'),('A17','curve'),('A15','count')}:continue
        if ep=='A10' and key=='height'and c['cue']in (38,39,40,42):continue
        if ep=='A10' and key=='height'and c['cue']==41:key='recoil'
        if ep=='A08' and str(c['chapter']).zfill(2) in ('01','02','07','08'):key='overview'
        if ep=='A08' and str(c['chapter']).zfill(2)=='04':key='edge'
        result.append({**c,'index':i,'key':key,'baselineStart':c['start'],'baselineFrames':c['frames']})
    return result,path

def prepare():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert control['fullLocalProductionAuthorized'] and control['renderAuthorized']
    result={'schemaVersion':1,'scope':'Only 17 selected episodes; immutable A03 omitted. Silent explanation plates, no commercial footage/TTS/platform changes.',
            'fps':60,'resolution':[1920,1080],'captionSafeY':920,'baselineCoordinate':'The original real-clips-v2/unreal-kit-v2 full-master frame clock; matching original authoring cut order.',
            'relationCoordinate':'Current relations-v4 full-master frame clock after pacing-v3 music-only observation insertions and relation/opening edit; map and existing body repair rows are protected.',
            'integration':'Parent may rebase final relation ranges after changed gameplay or speech. Original frameStart/frameEnd and cue/chapter identify anchors. All ends exclusive.',
            'audio':'No audio emitted. Preserve approved PCM and useful complete narration; final mixing/captions are parent-owned.',
            'status':'source-and-range-plan-ready; sampled-layout-review-in-progress','episodes':[]}
    for ep in EPISODES:
        p=project(ep);basecuts,cutfile=cuts(ep);pacing=read(p/'production/pacing-v3/edit-plan.json');edl=read(p/'production/local/relations-v4/opening-edl.json');events=pacing['events'];rows=[];pending=[]
        keys=sorted({c['key']for c in basecuts});inputs={}
        for key in keys:
            inputs[key]=input_receipt(ep,key)
        def mapped(start,n,detail):
            for part in edl['pictureEdl']:
                if part['kind']!='baseline':continue
                a=max(start,part['sourceStartFrame']);z=min(start+n,part['sourceStartFrame']+part['frames'])
                if z>a:rows.append({**detail,'relationFrameStart':part['outputStartFrame']+a-part['sourceStartFrame'],
                                   'relationFrameEnd':part['outputStartFrame']+z-part['sourceStartFrame'],
                                   'frames':z-a,'cutOffset':detail.get('cutOffset',0)+a-start,'pacingFrameStart':a,'pacingFrameEnd':z})
        seen=set();staged=set()
        for c in basecuts:
            start=c['baselineStart'];n=c['baselineFrames']
            detail={'id':f'{ep}-cut-{c["index"]:03d}','key':c['key'],'mode':'analysis','frameStart':start,'frameEnd':start+n,'originalCutFrames':n,
                    'baselineCut':c.get('id',c.get('cut')),'cue':c.get('cue'),'chapter':c.get('chapter',c.get('scene')),'focus':c.get('focus',c.get('teachingPurpose')),
                    'showLegend':c['key']not in seen,'phaseModeAtTail':c['key']not in staged and n>=240,'sizeIntroFrames':c.get('sizeIntroFrames',0)}
            if detail['phaseModeAtTail']:staged.add(c['key'])
            seen.add(c['key'])
            boundaries=sorted({start,start+n,*[e['pictureAt']for e in events if start<e['pictureAt']<start+n]})
            for a,z in zip(boundaries,boundaries[1:]):
                paced=a+sum(e['frames']for e in events if e['pictureAt']<=a)
                mapped(paced,z-a,{**detail,'cutOffset':a-start})
        inserted=0
        for e in events:
            key=e['key'].removeprefix('demo-');sourcekey=key
            if ep=='A02'and key in ('screen-size','amplitude'):sourcekey='combat'
            if e['kind']=='explanation'and sourcekey in keys:
                n=e['sourceEndFrame']-e['sourceStartFrame'];start=e['pictureAt']+inserted
                for k in range(e['repeatCount']):mapped(start+k*n,n,{'id':f'{ep}-{key}-pass-{k+1}','key':sourcekey,'mode':'native','passIndex':k+1,
                    'frameStart':e['pictureAt'],'frameEnd':e['pictureAt'],'insertionAtBaselineFrame':e['pictureAt'],'originalCutFrames':n,
                    'sourceStartFrame':e['sourceStartFrame'],'sourceEndFrame':e['sourceEndFrame'],'nativeSource':e['source'],
                    'screenSize':ep=='A02'and key=='screen-size','phaseModeAtTail':False,'showLegend':False})
            inserted+=e['frames']
        for part in edl['pictureEdl']:
            if part['kind']!='native-pass':continue
            key=part['key'].removeprefix('demo-')
            if key not in keys:continue
            rows.append({'id':f'{ep}-relocated-{key}-{part["passIndex"]}','key':key,'mode':'native','passIndex':part['passIndex'],
                         'frameStart':None,'frameEnd':None,'baselineNativeEvent':part['key'],'relationFrameStart':part['outputStartFrame'],
                         'relationFrameEnd':part['outputEndFrame'],'frames':part['frames'],'originalCutFrames':part['frames'],'cutOffset':0,
                         'sourceStartFrame':part['sourceStartFrame'],'nativeSource':part['source'],'phaseModeAtTail':False,'showLegend':False})
        rows.sort(key=lambda r:r['relationFrameStart']);assert all(a['relationFrameEnd']<=b['relationFrameStart']for a,b in zip(rows,rows[1:])),ep
        counts={r['id']:sum(v['id']==r['id']for v in rows)for r in rows};seq={}
        for r in rows:
            rid=r['id'];seq[rid]=seq.get(rid,0)+1
            if counts[rid]>1:r['id']+=f'-part-{seq[rid]}'
            r['output']=str((B/'local/contrast-v5/explanation-plates'/ep/(r['id']+'.mp4')).relative_to(R)).replace('\\','/')
            r['readyForRender']=True
        # The existing pacing pass count is two when the first body clip supplies
        # pass three. Preserve that 1x portion once, then analyze later cuts.
        # A full three-pass relocated opening needs no extra normal replay.
        for key in keys:
            native=[r for r in rows if r['key']==key and r['mode']=='native']
            analyses=[r for r in rows if r['key']==key and r['mode']=='analysis']
            # Series cuts do not necessarily carry an id. The original start
            # frame is the unique stable cut identity, also shared by splits.
            first=analyses[0]['frameStart'] if analyses else None
            lead=max((r['originalCutFrames']for r in native),default=0) if len(native)==2 else 0
            for r in analyses:r['nativeLeadFrames']=min(lead,r['originalCutFrames']) if r['frameStart']==first else 0
            assert len({r['frameStart']for r in analyses if r['nativeLeadFrames']})<=1
        result['episodes'].append({'id':ep,'slug':p.name,'originalRevision':ROWS[ep]['baselineRevision'],'cutPlan':str(cutfile.relative_to(R)).replace('\\','/'),
            'cutPlanSHA256':sha(cutfile),'pacingPlanSHA256':sha(p/'production/pacing-v3/edit-plan.json'),'relationEdlSHA256':sha(p/'production/local/relations-v4/opening-edl.json'),
            'contracts':{k:contract(ep,k)for k in keys},'sourceInputs':inputs,'rows':rows,'pending':pending,
            'preservedRelationRegions':[{k:v for k,v in q.items() if k in ('kind','outputStartFrame','outputEndFrame')}for q in edl['pictureEdl']if q['kind']in('map','repair')]})
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared',len(result['episodes']),'episodes',sum(len(e['rows'])for e in result['episodes']),'silent replacement ranges')
    return result
if __name__=='__main__':prepare()
