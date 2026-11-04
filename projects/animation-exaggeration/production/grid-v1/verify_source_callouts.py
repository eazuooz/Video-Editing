"""Resume the exact A02 source proposal without generating or editing media."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def asset(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,value): p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    proposal_path=H/'source-callout-proposal.json'
    original=proposal_path.read_bytes();old_sha=hashlib.sha256(original).hexdigest()
    proposal=read(proposal_path)
    assert proposal['episode']=='A02' and proposal['revision']=='grid-v1'
    assert sha(ROOT/proposal['sourcePlan']['path'])==proposal['sourcePlan']['sha256']
    sources=[]
    for row in proposal['sources']:
        source=ROOT/row['sourceFile']
        assert sha(source)==row['sourceSha256']
        sources.append(asset(source))
    manifest_path=ROOT/proposal['extraction']['manifest']
    assert sha(manifest_path)==proposal['extraction']['sha256']
    manifest=read(manifest_path);frame_count=0
    for source in manifest['sources']:
        for frame in source['frames']:
            assert sha(ROOT/frame['path'])==frame['sha256']
            frame_count+=1
    assert frame_count==46
    viewed=[];selected=[]
    for row in proposal['stillChoices']:
        source_frame=ROOT/row['decodedFrame']['path']
        assert sha(source_frame)==row['decodedFrame']['sha256']
        rgb=Image.open(source_frame).convert('RGB')
        assert rgb.size==(1920,1080)
        row['decodedFrame']['rgb24PixelSha256']=hashlib.sha256(rgb.tobytes()).hexdigest()
        row['decodedFrame']['pixelHashContract']='1920x1080 row-major RGB24; compare decoded pixels after extraction, not PNG compression metadata.'
        row['frameSelectionRequirement']='Select the exact decoded ordinal or verify timestamp extraction against rgb24PixelSha256 before final still rendering.'
        for mark in row['marks']:
            if 'points' in mark:
                assert all(0<=x<=1920 and 160<=y<892 for x,y in mark['points'])
            else:
                assert 0<=mark['x'] and 160<=mark['y'] and mark['x']+mark['w']<=1920 and mark['y']+mark['h']<892
        selected.append({'id':row['id'],'frame':row['sourceFrame'],'source':row['sourceKey'],
                         'exactFrame':row['decodedFrame'],'crop':row['crop'],'actualFit':row['actualFit']})
        viewed.append(asset(ROOT/row['proposalPreview375']))
    tekken=next(x for x in proposal['stillChoices'] if x['sourceKey']=='tekken8-kazuya-movelist')
    prior_anchors=tekken['narrationAnchors']
    tekken['narrationAnchors']=['허리가 놀랄 만큼 돌아가거나','한 장만 보면 몸이 이상해 보이기도 하죠']
    proposal['cueBindingCaution']='If an anchor starts after the native cut ends, place the mark on the corresponding analytical still. Do not delay/repeat/slow the actual clip just to accommodate the label.'
    proposal['resumeCheck']={'reviewer':'/root/a02_callouts_resume','clientDate':'2026-11-04',
        'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'priorProposalSha256':old_sha,
        'priorSourceAnd46FrameEvidenceHashesReused':True,
        'currentDirectViews':{'mobile375StillProposals':4,'fhdStillProposals':2,'kirbySequenceContactSheets':1},
        'change':'Removed arm-swing anchor from a kick still; added exact RGB24 pixel checks for four selected frames.',
        'finalCaptionedVideoInspected':False,'fullMotionOrAudioApproved':False}
    assert proposal_path.read_bytes()==original,'Concurrent proposal change'
    write(proposal_path,proposal)
    extra=['proposal-tekken8-kazuya-movelist-10086.png','proposal-vf5revo-lau-official-1848.png','kirby-needle-evolution/contact-02.jpg']
    evidence_root=manifest_path.parent
    viewed.extend(asset(evidence_root/p) for p in extra)
    write(H/'source-callout-resume-review.json',{
        'episode':'A02','revision':'grid-v1','status':'proposal-ready-for-measured-cue-binding',
        'clientDate':'2026-11-04','recordedAtUtc':datetime.now(timezone.utc).isoformat(),
        'priorProposalSha256':old_sha,'currentProposal':asset(proposal_path),'sources':sources,
        'all46PreviouslyExtractedFrameHashesMatch':True,'extractionManifest':asset(manifest_path),
        'currentDirectlyViewed':viewed,'selectedStills':selected,
        'anchorCorrection':{'source':'tekken8-kazuya-movelist','previous':prior_anchors,
            'current':tekken['narrationAnchors'],'reason':'Actual selected pose is a kick; do not place it under an arm-swing demonstration claim.'},
        'approvedScope':'Static source choices, crop/fit, visible targets and speech-phrase anchors only.',
        'finalTimingChosen':False,'movingInterpolationInspected':False,'finalEncodedCaptionPixelsInspected':False,
        'audioActuallyListened':False,'sourceMediaModified':False,'newMediaGenerated':False,
        'gitOrSharedFilesOrUnityModified':False})
    print(json.dumps({'status':'ready','proposalSha256':sha(proposal_path),
                      'reviewSha256':sha(H/'source-callout-resume-review.json'),'verifiedSourceFiles':3,
                      'verifiedExistingDecodedFrames':46,'directlyViewedArtifactsThisResume':7}))

if __name__=='__main__':main()
