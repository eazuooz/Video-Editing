"""Apply the latest explicit three-title steering without authorizing other work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT/'projects/player-customization'
HERE = Path(__file__).resolve().parent
TITLES = ['Splatoon Raiders', 'Animal Crossing: New Horizons', 'The Legend of Zelda: Breath of the Wild']
KO = ['스플래툰 레이더스', '모여봐요 동물의 숲', '젤다의 전설 브레스 오브 더 와일드(야숨)']


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    at = datetime.now(timezone.utc).isoformat()
    snapshot = PROJECT/'production/local/reference-preserving-v3/superseded-series-selection'
    snapshot.mkdir(parents=True, exist_ok=True)
    superseded = []
    for path in [HERE/'authorization.json', HERE/'design-plan.json', HERE/'script-text-review.json',
                 HERE/'script-revision.json', HERE/'visual-adaptation.json', HERE/'visual-assets.json',
                 ROOT/'motion-canvas/src/projects/player-customization/revision-v3/visuals.tsx',
                 *sorted((PROJECT/'script/reference-preserving-v3').glob('*.json'))]:
        if not path.exists():
            continue
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        target = snapshot/(sha[:12]+'-'+path.name)
        if not target.exists():
            shutil.copy2(path, target)
        superseded.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha,
                           'preservedDraft': target.relative_to(ROOT).as_posix()})
    evidence = ['게임예시 예시를 스플래툰 동물의숲 젤다의전설(야숨)으로 가자', '스플래툰 레이더스가 좋을거같아']
    decision = {'schemaVersion': 1, 'slug': 'player-customization', 'revision': 'reference-preserving-v3',
                'selectedAt': at, 'userEvidence': evidence, 'selectedTitles': TITLES, 'canonicalKo': KO,
                'supersedesCandidateSelectionOnly': ['Splatoon 3', 'The Legend of Zelda: Tears of the Kingdom'],
                'priorDrafts': superseded, 'newTtsBeforeSteering': False,
                'currentFullProductionStillAuthorized': True, 'boundary': 'complete new private Drive final review',
                'youtubeUploadAuthorized': False, 'automaticNextVideo': False,
                'sourceRule': 'Secure and view independent1080p+ actual recordings before locking changed game claims. Never rename Splatoon3/TOTK footage as the selected games.',
                'lessonRule': 'Preserve original eight teaching stages; replace game roles with verified observable equivalents. No Fuse in BOTW.',
                'globalNintendoOneThirdPolicyUnchanged': True}
    save(HERE/'title-selection.json', decision)
    auth = read(HERE/'authorization.json')
    auth.update(updatedAt=at, latestUserEvidence=evidence, selectedGameTitles=TITLES,
                selectionRecord='projects/player-customization/production/reference-preserving-v3/title-selection.json')
    auth['authorizedScope'] = 'Revise selected D21 using only Splatoon Raiders, Animal Crossing: New Horizons and The Legend of Zelda: Breath of the Wild. Preserve reference lesson order and useful explanations, unchanged approved voice, prior v2 master/Drive/baseline. Complete internal QA, current1080p60 four outputs, new private Drive final review and selective Git. No YouTube before human review, no next video.'
    save(HERE/'authorization.json', auth)
    design = read(HERE/'design-plan.json')
    design.update(updatedAt=at, status='independent-raiders-and-botw-footage-research',
                  selectedGameTitles=TITLES, titleSelection='projects/player-customization/production/reference-preserving-v3/title-selection.json',
                  sourceSelection='Pending inspected Raiders/BOTW sources; prior Splatoon3/TOTK candidates excluded.',
                  scriptLock='not locked; prior three-series draft is superseded for changed titles',
                  ttsGeneration='not started; approved unchanged PCM will be preserved')
    save(HERE/'design-plan.json', design)
    for suffix in ['ko', 'en', 'spoken-ko']:
        path = PROJECT/f'script/reference-preserving-v3/narration.{suffix}.json'
        value = read(path)
        value['status'] = 'superseded-draft-awaiting-selected-raiders-and-botw-evidence'
        value['notProductionInputReason'] = 'Latest selected exact titles differ. Current old game-specific paragraphs require source-backed revision before TTS.'
        save(path, value)
    for name in ['script-text-review.json', 'script-revision.json', 'visual-adaptation.json', 'visual-assets.json']:
        path = HERE/name
        value = read(path)
        value['supersededByTitleSelection'] = 'projects/player-customization/production/reference-preserving-v3/title-selection.json'
        value['currentProductionApproval'] = False
        save(path, value)
    manifest = read(PROJECT/'project.json')
    manifest['updatedAt'] = at
    manifest['currentRevision'].update(selectedGameTitles=TITLES, status='revising-raiders-acnh-botw-examples', productionComplete=False)
    save(PROJECT/'project.json', manifest)
    plan = read(PROJECT/'planning/production-plan.json')
    plan.update(updatedAt=at, selectedGameTitles=TITLES, status='revising-raiders-acnh-botw-examples',
                nextAction='Secure/view Raiders and BOTW independent FHD examples, then revise changed passages and preserve unchanged approved PCM.')
    save(PROJECT/'planning/production-plan.json', plan)
    checkpoint = read(PROJECT/'production/latest-checkpoint.json')
    checkpoint.update(updatedAt=at, stage='selected-exact-titles-independent-footage-research', selectedGameTitles=TITLES,
                      nextAction='Inspect Raiders and BOTW independent FHD source behaviors before changed-script lock and voice generation.',
                      currentTtsGeneration='not started')
    save(PROJECT/'production/latest-checkpoint.json', checkpoint)
    ledger = read(PROJECT/'production/review-ledger.json')
    ledger.update(updatedAt=at, selectedGameTitles=TITLES)
    ledger['checks'].append({'id': 'latest-exact-title-selection', 'status': 'recorded',
                             'evidence': 'production/reference-preserving-v3/title-selection.json',
                             'priorThreeSeriesDraftApproval': 'superseded only where changed titles affect source/text/UI',
                             'newVoiceRenderDeliveryQa': 'pending'})
    save(PROJECT/'production/review-ledger.json', ledger)
    worklist = read(ROOT/'shared/publishing/video-worklist.json')
    row = next(row for row in worklist['rows'] if row['slug'] == 'player-customization')
    row.update(productionStatus='사용자 지정3작품으로 수정중 · 레이더스/동물의 숲/야숨',
               executionStatus='raiders-and-botw-independent-footage-research',
               reviewStatus='v2 Drive보존 / 새 레이더스·야숨 자료 검증 후 대본·화면·변경음성 제작',
               notes='최신 확정: 스플래툰 레이더스·모여봐요 동물의 숲·젤다의 전설 브레스 오브 더 와일드(야숨). 스플래툰3/왕눈 초안은 미선택 후보로 보존. 이번편만 닌텐도3/3 명시선택. 새Drive최종검수까지, 기존v2·YouTube보존, D22없음.')
    row['currentRevision']['selectedGameTitles'] = TITLES
    worklist['updatedAt'] = at
    save(ROOT/'shared/publishing/video-worklist.json', worklist)
    print('Applied explicit Raiders/ACNH/BOTW titles; prior candidates preserved, no new voice or render.')


if __name__ == '__main__':
    main()
