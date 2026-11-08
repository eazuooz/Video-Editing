"""One final precedence-resolved integration list for the parent's editor."""
from sources import *
from copy import deepcopy

def main():
    plan=read(H/'replacement-plan.json');delivery=read(H/'explanation-delivery.json')
    results=read(H/'observation-corrections.json');extension=read(H/'pacing-extension.json');legends=read(H/'legend-corrections.json')
    assert delivery['status']=='complete' and results['status']=='rendered-current-silent-overrides' and extension['status']=='rendered-current-silent-override'
    fixed={r['id']:r for r in results['rows']}
    fixed.update({r['id']:r for r in extension['bodyOverrides']})
    fixed.update({r['id']:r for r in legends['rows']})
    blend=read(H/'blend-crop-corrections.json')
    assert blend['status']=='rendered-current-silent-overrides'
    fixed.update({r['id']:r for r in blend['rows']})
    removed=set(extension['overridesBaseRows']);episodes=[]
    for ep in plan['episodes']:
        rows=[]
        for source_row in ep['rows']:
            if source_row['id'] in removed:continue
            r=deepcopy(fixed.get(source_row['id'],source_row))
            r['newFrames']=r['frames'];r['sha256']=sha(R/r['output'])
            r['retainsOriginalNarratedPCM']=True;r['silentReplacement']=True
            if r['id']in fixed:r.setdefault('overrideReason','Completed actual result or full finger endpoint; same-length body replacement.')
            rows.append(r)
        if ep['id']=='A15':
            rows.append({'id':'A15-keys-three-complete-native-passes','key':'keys','mode':'native','passCount':3,
                'frameStart':extension['originalInsertionAtFrame'],'frameEnd':extension['originalInsertionAtFrame'],
                'relationFrameStart':extension['relationBaselineStartFrame'],'relationFrameEnd':extension['relationBaselineEndFrame'],
                'frames':extension['relationBaselineEndFrame']-extension['relationBaselineStartFrame'],'newFrames':extension['newFrames'],
                'output':extension['output'],'sha256':extension['sha256'],'retainsOriginalNarratedPCM':True,
                'audioTreatment':'Old window is music-only. Extend that bed by230frames; do not stretch/cut narration. Shift all later old-clock material by the delta alongside other parent edits.',
                'deltaFrames':extension['deltaFrames'],'silentReplacement':True,'sourceFramesPerPass':130,'holdFramesPerPass':18})
        rows.sort(key=lambda r:r['relationFrameStart'])
        assert all(a['relationFrameEnd']<=b['relationFrameStart']for a,b in zip(rows,rows[1:])),ep['id']
        for r in rows:
            assert r['newFrames']>0 and r['sha256']==sha(R/r['output'])
            for protected in ep['preservedRelationRegions']:
                assert max(r['relationFrameStart'],protected['outputStartFrame'])>=min(r['relationFrameEnd'],protected['outputEndFrame']),(r['id'],'protected map overlap')
        episodes.append({'id':ep['id'],'slug':ep['slug'],'relationEdlSHA256':ep['relationEdlSHA256'],'originalCutPlanSHA256':ep['cutPlanSHA256'],
            'additionalFrames':230 if ep['id']=='A15' else 0,'rows':rows,'preservedRelationRegions':ep['preservedRelationRegions']})
    out={'schemaVersion':1,'status':'ready-for-parent-final-assembly','fps':60,'resolution':[1920,1080],
        'scope':'17 selected silent authored explanation revisions, A03 omitted. No new game sources/audio/full masters in this package.',
        'coordinate':'All relationFrameStart/End are the unchanged relations-v4 baseline clock, end-exclusive. Apply in that clock and rebase once with parent speech/game edits.',
        'precedenceResolved':True,'replaceBasePlanForIntegration':True,'baselinePlanSHA256':sha(H/'replacement-plan.json'),
        'observationCorrectionSHA256':sha(H/'observation-corrections.json'),'pacingExtensionSHA256':sha(H/'pacing-extension.json'),
        'legendCorrectionSHA256':sha(H/'legend-corrections.json'),
        'blendCropCorrectionSHA256':sha(H/'blend-crop-corrections.json'),
        'finalHumanReview':'pending after parent full assembly','A03Preserved':True,'episodes':episodes}
    (H/'integration-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Final integration ready:',len(episodes),'episodes',sum(len(e['rows'])for e in episodes),'ranges; A15 +230F',flush=True)
if __name__=='__main__':main()
