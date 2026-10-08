"""Prepare one new official source, preserving all completed research and media."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
now = lambda: datetime.now(timezone.utc).isoformat()
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def save(path, value):
    tmp = path.with_name(path.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    for retry in range(40):
        try:
            os.replace(tmp, path)
            return
        except OSError:
            if retry == 39:
                raise
            time.sleep(.15)

targets = [BASE/'acquire-gauss129-v1.py', BASE/'inspect-gauss129-native-v1.py', BASE/'gauss129-public-source-review-v1.json']
assert not any(p.exists() for p in targets), 'Read actual checkpoint; preparation is single-use.'
acquisition = (BASE/'acquire-yareli155-v1.py').read_text('utf-8')
acquisition = acquisition.replace('yareli-devstream155-v1', 'gauss-devstream129-v1').replace('yareli155', 'gauss129')
acquisition = acquisition.replace('yareli', 'gauss').replace('8eUfnQ8mWXs', 'h7qntXMufKk')
acquisition = acquisition.replace('*00:45:21-00:51:27', '*00:37:24-00:44:43')
acquisition = acquisition.replace('gauss-2721-3087', 'gauss-2244-2683').replace('sourceOffsetSeconds=2721', 'sourceOffsetSeconds=2244').replace('requestedSeconds=366', 'requestedSeconds=439')
targets[0].write_text(acquisition, 'utf-8')
inspection = (BASE/'inspect-yareli155-native-v1.py').read_text('utf-8')
inspection = inspection.replace('yareli-devstream155-native-v1', 'gauss-devstream129-native-v1').replace('yareli-devstream155-v1', 'gauss-devstream129-v1').replace('yareli155', 'gauss129')
inspection = inspection.replace('yareli', 'gauss').replace('Yareli155', 'Gauss129').replace('8eUfnQ8mWXs', 'h7qntXMufKk')
inspection = inspection.replace('gauss-2721-3087', 'gauss-2244-2683').replace('sourceOffsetSeconds=2721', 'sourceOffsetSeconds=2244').replace('sourceSeconds=2721+', 'sourceSeconds=2244+')
targets[1].write_text(inspection, 'utf-8')
record = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(), sourceVideoId='h7qntXMufKk',
    url='https://www.youtube.com/watch?v=h7qntXMufKk', officialArticle='https://www.warframe.com/en/news/devstream-129-overview',
    officialOwner='PlayWarframe / @Warframe verified', title='Warframe | Devstream #129',
    requestedSourceIn=2244, requestedSourceOut=2683, publicPlayerAvailable=True,
    publicCuaPixelObservations=[
        dict(sourceSeconds=2275, observation='Gauss faces the open terrain after a forward movement; path and caster are visible. No nearby enemy contact is claimed from this frame.'),
        dict(sourceSeconds=2545, observation='Gauss stands near an orange ground effect with an opponent ahead amid blue effects; caster, near ground and target space are visible.'),
        dict(sourceSeconds=2726, observation='Later out-of-request view shows Gauss approaching a large mechanical opponent; this later interval is not acquired or allocated.')],
    transcriptRole='Research navigation only, never source-pixel proof or recognizer prompt. Devstream infinite-energy demonstration is not a controlled equipment-performance test.',
    recentUseCheck='Before registering this source, exact-ID rg over projects, production and shared/publishing JSON/Markdown, excluding rebuild manifests, found no matches (exit1).',
    selectionPurpose='Fresh unique Gauss dash/ground/caster/target observation for named Gauss paragraphs and general action-space bridges. Keep named Dante/Jade/Yareli paragraphs matched to their own characters.',
    diagramConnection='Projected path, caster origin and affected target space; no stats, optimality, build-change causality or unseen enemy contact inferred.',
    rightsStatus='Conditional DE Schedule C-1 evidence preserved; source audio excluded, opening notice retained, presenter/brand overlays must be cropped; human public-rights review pending.',
    cropApproval=False, nativeActionApproved=False, finalAllocationApproved=False, bodyRatioApproved=False, rawMediaLocalOnly=True, newGitImages=0,
    acquisition='projects/player-customization/production/gauss129-acquisition-execution-v1.json',
    rejectedAlternative=dict(sourceVideoId='0Om_gCEezUs', title='Dante Unbound official trailer', reason='Observed30s frontal cinematic pose/enemies and45s Styanax cinematic close view do not establish the needed continuous Dante action. Not acquired or counted as actual quota.'))
save(targets[2], record)
candidate_path = ROOT/'projects/player-customization/sources/game-candidates.json'
candidates = read(candidate_path)
candidates.setdefault('additionalOfficialProfiles', {})['freshGauss129Research'] = record
candidates['reviewedAt'] = now()
save(candidate_path, candidates)
cp_path = BASE/'latest-checkpoint.json'
cp = read(cp_path)
cp['ownedJob']['status'] = 'exact-yareli155-crops-directly-reviewed-completed'
cp.update(recordedAt=now(), gauss129PublicSourceReview=targets[2].relative_to(ROOT).as_posix(),
    nextAction='Acquire the newly observed official Gauss129 source once after current resource check; completed Yareli155152 crops and all prior voice/white/native work are preserved. Final allocation and all final media gates remain false.')
save(cp_path, cp)
qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
q = read(qp)
i = next(i for i in q['items'] if i['slug']=='player-customization')
i.update(currentExecution=cp['ownedJob'], gauss129PublicSourceReview=cp['gauss129PublicSourceReview'], nextAction=cp['nextAction'])
q['updatedAt'] = now()
save(qp, q)
print(json.dumps(dict(preparedPaths=[p.relative_to(ROOT).as_posix() for p in targets], newMedia=0, finalApproved=False)))
