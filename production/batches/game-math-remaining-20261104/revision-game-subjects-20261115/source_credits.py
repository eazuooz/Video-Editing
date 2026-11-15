"""Credit the actual recordings used for cropped game images."""
from subject_revision import *


def main():
    files=subprocess.check_output(['rg','--files','projects','shared/output/game-math-part2-full-series','production/batches/game-math-remaining-20261104','-g','*info.json'],cwd=ROOT,text=True).splitlines()
    required={'mario','kart-sprite','forza','doom','windmill','beamng','town','train','maker'}
    result=[]
    for source in read(HERE/'sources.json'):
        if source['id'] not in required:continue
        matches=[ROOT/f for f in files if Path(f).name.startswith(source['sourceId'])]
        assert matches,source['id'];metadata=read(matches[0]);assert metadata['id']==source['sourceId']
        assert min(source['decodedDimensions'])>=1080
        label=metadata.get('license')
        permission=label if label else 'Explicit FREE TO USE GAMEPLAY title and freetousegameplay description; not relabeled as Creative Commons.'
        assert label or source['id']=='town'
        result.append(dict(frameId=source['id'],game=source['game'],recordingUrl=source['recordingUrl'],
            title=metadata['title'],uploader=metadata['uploader'],licenseLabel=label,
            recorderPermissionEvidence=permission,metadata=str(matches[0]),metadataSha256=sha(matches[0]),
            existingPublisherReview=source['rightsEvidence'],
            changes='Extracted frame, cropped / background removed where applicable, resized and connected to our explanatory labels and analytic motion. Original game and recording are not claimed as ours.'))
    save(HERE/'source-rights-review.json',dict(sources=result,scope='Actual game-image recorder credits and unchanged existing publisher/source review; no new raw game/asset redistribution.'))


if __name__=='__main__':main()
