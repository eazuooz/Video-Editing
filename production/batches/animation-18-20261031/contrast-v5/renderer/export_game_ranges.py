"""Metadata-only complete independent-gameplay mask/ranges for parent integration."""
from sources import *
from config import EPISODES
def old_cuts(ep):
    p=project(ep);rev=ROWS[ep]['baselineRevision'];h=p/'production'/rev
    if ep=='A01':
        old=read(p/'production/grid-v1/edit-plan.json');lookup={c['id']:c for c in old['cuts']};out=[]
        for i,s in enumerate(read(h/'edit-plan-final.json')['segments']):
            c=lookup.get(s.get('cut'),{})
            if s['kind']=='old'and c.get('kind')=='independent-gameplay':out.append({**c,'index':i,'key':c.get('source'),'originalStart':s['start'],'originalEnd':s['start']+s['frames'],'cue':c.get('speechCues'),'chapter':s['chapter']})
        return out
    d=read(h/('edit-plan.json'if ep=='A02'else'edit-plan-final.json'));out=[]
    for i,c in enumerate(d['cuts']):
        good=c.get('kind')=='independent-gameplay'if ep=='A02'else c['key']in d['sourceEvidence']
        if good:
            start=c.get('startFrame',c.get('start'));out.append({**c,'index':i,'id':c.get('id',f'{ep}-cut-{i:03}'),'originalStart':start,'originalEnd':start+c['frames'],
                'key':c.get('key',c.get('source',c.get('gameLabel'))),'chapter':c.get('chapter',c.get('scene'))})
    return out
def main():
    result={'schemaVersion':1,'fps':60,'scope':'Metadata only. All original independent-gameplay cuts and their preserved native observation insertions; map/repair/explanation/native-demo regions omitted. A03 untouched.',
      'coordinates':'originalStart/originalEnd refer to the matching pre-pacing full-master frame clock; relationStart/relationEnd address current relations-v4. End exclusive. Repeats may refer to the same source range.',
      'episodes':[]}
    for ep in EPISODES:
        p=project(ep);pc=read(p/'production/pacing-v3/edit-plan.json');edl=read(p/'production/local/relations-v4/opening-edl.json');assembly=read(p/'production/local/relations-v4/assembly.json');cs=old_cuts(ep);rows=[]
        mask=np.zeros(pc['baselineFrames'],np.uint8)
        for c in cs:mask[c['originalStart']:c['originalEnd']]=1
        chunks=[];cursor=0
        for e in pc['events']:
            chunks.extend([mask[cursor:e['pictureAt']],np.full(e['frames'],int(e['kind']=='independent-gameplay'),np.uint8)]);cursor=e['pictureAt']
        chunks.append(mask[cursor:]);paced=np.concatenate(chunks);assert len(paced)==pc['totalFrames']
        expected=np.zeros(assembly['totalFrames'],np.uint8)
        for part in edl['pictureEdl']:
            if part['kind']=='baseline':expected[part['outputStartFrame']:part['outputEndFrame']]=paced[part['sourceStartFrame']:part['sourceStartFrame']+part['frames']]
        def mapped(start,end,detail):
            for part in edl['pictureEdl']:
                if part['kind']!='baseline':continue
                a=max(start,part['sourceStartFrame']);b=min(end,part['sourceStartFrame']+part['frames'])
                if b>a:rows.append({**detail,'originalStart':detail['originalStart']+a-start,'originalEnd':detail['originalStart']+b-start,'relationStart':part['outputStartFrame']+a-part['sourceStartFrame'],'relationEnd':part['outputStartFrame']+b-part['sourceStartFrame'],
                    'pacingStart':a,'pacingEnd':b,'sourceOffsetFrames':a-start,'frames':b-a})
        for c in cs:
            start,end=c['originalStart'],c['originalEnd'];edges=sorted({start,end,*[e['pictureAt']for e in pc['events']if start<e['pictureAt']<end]})
            for a,b in zip(edges,edges[1:]):
                offset=sum(e['frames']for e in pc['events']if e['pictureAt']<=a)
                detail={k:c.get(k)for k in ('id','key','cue','chapter','playbackSpeed','sourceFile','sourceUrl','sourceStart','sourceEndExclusive','sourcePoint','focus','gameLabel')}
                mapped(a+offset,b+offset,{**detail,'originalStart':a,'originalEnd':b,'originalCutStart':start,'originalCutEnd':end,'kind':'baseline-gameplay','repeatLabel':None})
        inserted=0
        for e in pc['events']:
            if e['kind']=='independent-gameplay':
                n=e['sourceEndFrame']-e['sourceStartFrame'];at=e['pictureAt']+inserted
                match=next((c for c in cs if c['id']==e.get('sourceCut')),None)
                if match is None:match=next((c for c in cs if c['originalStart']<=e['sourceStartFrame']<c['originalEnd']),None)
                originalStart=e['sourceStartFrame']+(match['originalStart']if ep=='A02'and match else 0)
                for repeat in range(e['repeatCount']):
                    num=repeat+1 if e.get('followingNativePass')else repeat+2 if e.get('firstPassAlreadyInBaseline')else repeat+1
                    detail={'id':ep+'-'+e['key']+f'-repeat-{num}','key':(match or{}).get('key',e['key'].removeprefix('game-')),'cue':(match or{}).get('cue'),
                        'chapter':(match or{}).get('chapter'),'originalStart':originalStart,'originalEnd':originalStart+n,'kind':'native-gameplay-repeat','repeatIndex':num,
                        'repeatTotal':3,'repeatLabel':f'기본 속도 {num}/3','normalSpeed':1,'source':e['source'],'sourceSHA256':e['sourceSHA256'],
                        'repeatSourceStartFrame':e['sourceStartFrame'],'repeatSourceEndFrame':e['sourceEndFrame'],'originalInsertionAt':e['pictureAt'],
                        'firstPassAlreadyInBaseline':e.get('firstPassAlreadyInBaseline'),'followingNativePass':e.get('followingNativePass')}
                    mapped(at+repeat*n,at+(repeat+1)*n,detail)
            inserted+=e['frames']
        rows.sort(key=lambda r:r['relationStart']);assert all(a['relationEnd']<=b['relationStart']for a,b in zip(rows,rows[1:])),ep
        counts={r['id']:sum(q['id']==r['id']for q in rows)for r in rows};seen={}
        for r in rows:
            originalId=r['id'];r['originalId']=originalId;seen[originalId]=seen.get(originalId,0)+1
            if counts[originalId]>1:r['id']+=f'-part-{seen[originalId]}'
        got=np.zeros_like(expected)
        for r in rows:got[r['relationStart']:r['relationEnd']]=1
        assert np.array_equal(expected,got),(ep,'game range/mask mismatch')
        published=assembly['measuredScreenShare']['actualGameplayFrames'];assert int(got.sum())==published,(ep,int(got.sum()),published)
        result['episodes'].append({'id':ep,'slug':p.name,'relationTimelineFrames':len(got),'gameFrames':int(got.sum()),'originalGameFrames':int(mask.sum()),
            'maskSHA256':hashlib.sha256(got.tobytes()).hexdigest(),'maskMatchesIndependentReconstruction':True,'countMatchesCurrentAssembly':True,
            'pacingPlanSHA256':sha(p/'production/pacing-v3/edit-plan.json'),'openingEdlSHA256':sha(p/'production/local/relations-v4/opening-edl.json'),
            'assemblySHA256':sha(p/'production/local/relations-v4/assembly.json'),'rows':rows})
    out=H/'game-baseline-ranges.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print('Exported complete',len(result['episodes']),'episode gameplay masks:',sum(len(e['rows'])for e in result['episodes']),'ranges')
if __name__=='__main__':main()
