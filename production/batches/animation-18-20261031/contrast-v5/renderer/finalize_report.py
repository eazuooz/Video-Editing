"""Bind the final silent package to inspected current encoded evidence."""
from sources import *
from datetime import datetime,timezone

OBSERVATIONS={
 'A01':'The normal and lowered walks differ in head height and limb posture; three captured instants remain distinct.',
 'A02':'Real1.8x joint-rotation excursion is visibly different while model scale is unchanged; the correct current/previous/path legend is retained.',
 'A04':'The same-time first change and the12/13/24F stages show the faster lead-in distinctly.',
 'A05':'Adjacent actual75/76F poses show the one-frame silhouette change; the preparation frame is separate.',
 'A06':'The remaining follow-through and recovered stance differ visibly; state labels match the saved control thresholds.',
 'A07':'The same captured pose is large versus small, explicitly a screen-occupancy comparison, followed by distinct actual motion stages.',
 'A08':'The same initial model is progressively corrected. The four-stage overview and171F final view include torso, arm, pelvis and legs; supporting foot is visible.',
 'A09':'Hand scaling is localized to the hand at the same position; the full changed hand remains inside the inspected crop.',
 'A10':'Upper and lower actual damage animations differ; the staged lower-hit sequence reaches a falling posture.',
 'A11':'The same endpoint uses different intermediate pose/time allocation; the actual12/18/20F kick stages are distinct.',
 'A12':'The mouth-open variants and close facial controls remain visible at375px.',
 'A13':'The held handle switches side under mirroring. This is a side/prop comparison, not an invented sword or shield.',
 'A14':'At49F the immediate walking pose differs from the50/50 mixture. The final common crop includes both feet;42/49/56F stage views are distinct.',
 'A15':'The stepped hand and continuous fingers differ at mid-motion and share the endpoint. Three full130F motions plus18F recorded end holds are retained.',
 'A16':'Early/late activation and the actual authored hit region are separated from the visible pose; three activation stages are shown.',
 'A17':'The same hand target has a clearly different elbow direction; close framing preserves the joint shape.',
 'A18':'At26F the face directions and nose paths differ, with saved yaw/pitch curves and playhead; the shared final pose is not used as the sole comparison.'}

def main():
    plan=read(H/'integration-manifest.json');base=read(H/'replacement-plan.json');assert plan['status']=='ready-for-parent-final-assembly'
    checks=[];size=0
    for ep in plan['episodes']:
        b=next(e for e in base['episodes']if e['id']==ep['id']);p=R/'projects'/ep['slug']
        assert ep['id']!='A03'
        assert sha(R/b['cutPlan'])==b['cutPlanSHA256']
        assert sha(p/'production/pacing-v3/edit-plan.json')==b['pacingPlanSHA256']
        assert sha(p/'production/local/relations-v4/opening-edl.json')==b['relationEdlSHA256']
        for row in ep['rows']:
            path=R/row['output'];assert sha(path)==row['sha256'];size+=path.stat().st_size
        checks.append({'id':ep['id'],'finalRanges':len(ep['rows']),'newFrames':sum(r['newFrames']for r in ep['rows']),
            'baselineHashesUnchanged':True,'observation':OBSERVATIONS[ep['id']]})
    assert len(checks)==17 and sum(e['finalRanges']for e in checks)==443
    local=B/'local/contrast-v5/encoded-qa';audit=read(local/'encoded-audit.json');moments=read(local/'key-moments.json')
    assert {s['episode']for s in audit['samples']}=={e['id']for e in checks}
    for item in audit['samples']:
        row=next(r for e in plan['episodes']if e['id']==item['episode']for r in e['rows']if r['id']==item['rowId'])
        assert row['sha256']==item['plateSHA256']
        item['visualReview']='model-inspected-current-encoded1080-and375-samples'
        item['observation']=OBSERVATIONS[item['episode']]
        # Only the inspected samples: this is not a whole-video clearance test.
        for sample in item['samples']:
            with Image.open(R/sample['path'])as im:
                a=np.asarray(im.convert('RGB'))[920:]
                assert np.max(np.abs(a.astype(int)-np.array([8,12,10])))<20,(item['episode'],'caption reserve')
    for item in moments['samples']:item['review']='model-inspected-current-encoded1080-and375-key-moment'
    (local/'encoded-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')
    (local/'key-moments.json').write_text(json.dumps(moments,ensure_ascii=False,indent=2)+'\n','utf8')
    assets=read(H/'ue-assets/assets-manifest.json')
    for a in assets['assets']:assert sha(H/'ue-assets'/a['path'])==a['sha256']
    report={'schemaVersion':1,'status':'silent-explanation-package-ready','createdAt':datetime.now(timezone.utc).isoformat(),
        'integrationManifest':'production/batches/animation-18-20261031/contrast-v5/renderer/integration-manifest.json','integrationManifestSHA256':sha(H/'integration-manifest.json'),
        'scope':'17 selected explanation replacements only. Not17 finished full videos, not user approval. A03 and all old baseline files are preserved.',
        'resolution':[1920,1080],'fps':60,'finalRanges':443,'totalFrames':sum(e['newFrames']for e in checks),'totalMediaBytes':size,
        'A15AdditionalFrames':230,'coordinate':'Unchanged relations-v4 baseline, end-exclusive. Parent applies all length changes once.',
        'episodes':checks,'coverage':{'currentSelectedPlatesFullyDecoded':17,'decodedFrames':sum(s['decodedFrames']for s in audit['samples']),
            'staticEncodedSamples':34,'additionalKeyMoments':2,'additionalA08CompletedPoseSample':1,'additionalA15PassSamples':5,
            'A15NativeConcatDecodedFrames':444,'sourceStudyContacts':60,'sourceContactPages':8,
            'actualCaptionSample':'A02 435frames with current unchanged ASS; prior decode and sampled1080/375 inspection reused by exact SHA.',
            'captionReserve':'The34 inspected current silent samples keep y920..1079 clear. Final changed-caption assembly still requires parent QA.',
            'fullWatch':False,'humanListening':False,'humanApproval':False},
        'evidence':{'encodedAudit':str((local/'encoded-audit.json').relative_to(R)).replace('\\','/'),'encodedAuditSHA256':sha(local/'encoded-audit.json'),
            'keyMoments':str((local/'key-moments.json').relative_to(R)).replace('\\','/'),'keyMomentsSHA256':sha(local/'key-moments.json'),
            'nativeA15':'production/batches/animation-18-20261031/contrast-v5/renderer/pacing-extension.json','nativeA15SHA256':sha(H/'pacing-extension.json'),
            'modelChecks':'production/batches/animation-18-20261031/contrast-v5/renderer/validation.json','A08EditableAssets':len(assets['assets'])},
        'resolvedFindings':['A08 final pose reaches171F rather than stopping before leg changes.','A15 native passes reach the actual complete endpoint three times.','A06 state comparison reaches the recovered-input interval.','Incorrect generic legend removed outsideA02.','A14 full-body crop measured across every captured frame, preserving both feet during the blend.'],
        'remainingForParent':['Integrate independent gameplay and only approved necessary speech replacements.','Carry music through A15 extra230frames without stretching narrated PCM; rebase later picture/captions/audio once.','Inspect complete newly captioned audiovisual masters and deliver local four-file review bundles.'],
        'sourceLimitation':'A14 demonstrates authored pose blending without foot-lock IK. Its source reference-line crossing is preserved; this package does not claim grounded locomotion.',
        'noPlatformChanges':True,'noGitActions':True}
    (H/'final-renderer-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    files=[]
    for p in sorted(H.rglob('*')):
        if not p.is_file()or'__pycache__'in p.parts or p.name=='owned-files.json':continue
        files.append({'path':str(p.relative_to(R)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size})
    (H/'owned-files.json').write_text(json.dumps({'scope':'Only the renderer directory for selective parent commit. Excludes local media and Python cache; includes20 newly authored UE assets, no vendor assets.','sharedFilesChanged':[],
        'selfEntry':'production/batches/animation-18-20261031/contrast-v5/renderer/owned-files.json','files':files},ensure_ascii=False,indent=2)+'\n','utf8')
    print('Ready',len(files)+1,'owned files; manifestSHA',report['integrationManifestSHA256'],flush=True)
if __name__=='__main__':main()
