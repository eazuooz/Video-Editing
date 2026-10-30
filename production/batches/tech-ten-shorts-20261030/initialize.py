"""Create the exact authorized ten-project scaffolding, never generate media."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess

from scoped_context import AUTH_ID, BATCH, MEDIA, RESEARCH, RESEARCH_SHA, REVISION, ROOT, sha


def save_absent(path, data):
    path = Path(path)
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(payload)
    return True


def main():
    assert sha(RESEARCH) == RESEARCH_SHA
    selected = json.loads(RESEARCH.read_text(encoding='utf-8'))['candidates']
    assert len(selected) == 10
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence = '좋아~ 이 10개 전부 우리 쇼츠 제작 규칙에 맞춰서 만들어줘~'
    templates = ['render-voice', 'assemble-paragraphs', 'transcribe', 'time-captions',
                 'finish-audio', 'finish-video', 'prepare-header', 'build-review']
    template_records = {name: {'path': f'projects/shorts-factorio-belt-gaps/production/{name}.py',
        'sha256': sha(ROOT / f'projects/shorts-factorio-belt-gaps/production/{name}.py')} for name in templates}
    save_absent(BATCH / 'template-sources.json', {'revision': REVISION, 'templates': template_records,
        'reusePolicy': 'Hash-pinned algorithms, rebound only to selected project wrappers. Never mutate the template source project.'})
    rows = []
    voice_template = json.loads((ROOT / 'projects/shorts-factorio-belt-gaps/production/tts-manifest.json').read_text(encoding='utf-8'))
    for candidate in selected:
        slug = 'shorts-' + candidate['id']
        project = ROOT / 'projects' / slug
        physical = MEDIA / slug / 'local'
        physical.mkdir(parents=True, exist_ok=True)
        (project / 'production').mkdir(parents=True, exist_ok=True)
        link = project / 'production/local'
        if not link.exists():
            command = "New-Item -ItemType Junction -Path '" + str(link).replace("'", "''") + "' -Target '" + str(physical).replace("'", "''") + "' | Out-Null"
            subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], check=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        if link.resolve() != physical.resolve():
            raise RuntimeError('Existing media path has a different owner: ' + str(link))
        auth = {'id': AUTH_ID, 'userEvidence': evidence, 'recordedAt': timestamp,
                'fullProductionAuthorized': True, 'humanFinalReviewRequired': True,
                'youtubeAuthorized': False, 'driveAuthorized': False,
                'scope': 'This exact finite ten-candidate selection through local final review; no platform action.'}
        manifest = {'slug': slug, 'title': candidate['suggestedTitleKo'],
            'format': {'type': 'youtube-shorts', 'width': 1080, 'height': 1920, 'fps': 60},
            'status': 'preproduction', 'currentRevision': REVISION, 'authorization': auth,
            'mediaRoot': str(MEDIA / slug).replace('\\', '/'),
            'currentFinalDirectory': 'production/local/final-reviewed-v1', 'publishReady': False,
            'researchCandidateId': candidate['id'],
            'paths': {'script': f'projects/{slug}/script/narration.spoken.ko.json',
                      'checkpoint': f'projects/{slug}/production/checkpoint.json',
                      'productionPlan': f'projects/{slug}/planning/production-plan.json',
                      'timeline': f'projects/{slug}/production/visual-timing.json',
                      'videoBurnedCaptions': f'projects/{slug}/production/local/final-reviewed-v1/captioned.mp4',
                      'videoClean': f'projects/{slug}/production/local/final-reviewed-v1/clean.mp4',
                      'captionsKo': f'projects/{slug}/production/local/final-reviewed-v1/captions.ko.srt',
                      'captionsEn': f'projects/{slug}/production/local/final-reviewed-v1/captions.en.srt',
                      'localReview': f'projects/{slug}/production/local/final-reviewed-v1/index.html'}}
        save_absent(project / 'project.json', manifest)
        save_absent(project / 'production/checkpoint.json', {'revision': REVISION, 'status': 'preproduction',
            'recordedAt': timestamp, 'userEvidence': evidence,
            'completed': ['exact-topic-selection', 'research-candidate-record'],
            'pending': ['independent-fhd-footage-acquisition-and-viewing', 'final-script', 'Unity-scenes',
                        'TTS-ASR-caption-alignment', 'render-mix-four-outputs', 'internal-review', 'human-final-review'],
            'gpuJobStarted': False, 'platformActions': False})
        save_absent(project / 'planning/production-plan.json', {'revision': REVISION,
            'researchCandidateId': candidate['id'], 'researchRecord': RESEARCH.relative_to(ROOT).as_posix(),
            'researchSha256': RESEARCH_SHA, 'game': candidate['game'],
            'centralQuestion': candidate['suggestedHookKo'], 'canonicalTerms': candidate['canonicalTerms'],
            'claims': [candidate['verifiedMechanismKo']], 'limits': candidate['limitsKo'],
            'primarySources': candidate['primarySources'], 'suggestedScreens': candidate['suggestedScreensKo'],
            'oneVariableComparison': candidate['oneVariableComparison'], 'scriptFinalized': False,
            'independentFootageViewed': False, 'scenePlan': [], 'chapterLinks': [],
            'rendererPolicy': 'Unity implementation/behavior explanations with Motion Canvas compositing; choose per teaching need, preserve independently editable Unity scenes.',
            'footageRightsConfirmed': False, 'sourceFhdVerified': False, 'actualHumanListening': 'pending'})
        save_absent(project / 'production/review-ledger.json', {'revision': REVISION,
            'status': 'not-generated', 'actualCompleteHumanListening': False,
            'technicalChecks': 'pending', 'visualPlaybackReview': 'pending',
            'humanFinalReview': 'pending', 'youtubeUploaded': False, 'driveUploaded': False})
        voice = copy.deepcopy(voice_template)
        voice['slug'], voice['revision'] = slug, REVISION
        voice['paths']['script'] = f'projects/{slug}/script/narration.spoken.ko.json'
        voice['tts']['outputDir'] = f'projects/{slug}/production/local/audio-v1/voice'
        voice['tts']['gpuProfileReason'] = 'One serial job from explicit tech-ten selection. No imported prior-project editor exception; honor current batch permission and active game/editor/GPU lease checks.'
        save_absent(project / 'production/tts-manifest.json', voice)
        for name in templates:
            wrapper = f'''"""Scoped shared-pipeline wrapper; no work at import."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'production/batches/tech-ten-shorts-20261030'))
from scoped_pipeline import dispatch

def main():
    return dispatch({slug!r}, {name!r})

if __name__ == '__main__':
    main()
'''
            save_absent(project / 'production' / (name + '.py'), wrapper)
        save_absent(project / 'production/audio_revision.py', f'''"""Current selected project context; importing starts no jobs."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'production/batches/tech-ten-shorts-20261030'))
from scoped_context import make_context
globals().update(make_context({slug!r}))
''')
        rows.append({'order': candidate['order'], 'slug': slug, 'candidateId': candidate['id'],
                     'title': candidate['suggestedTitleKo'], 'game': candidate['game'],
                     'project': project.relative_to(ROOT).as_posix() + '/project.json',
                     'status': 'preproduction', 'revision': REVISION})
    save_absent(BATCH / 'batch.json', {'schemaVersion': 1, 'batchId': BATCH.name, 'revision': REVISION,
        'authorizationId': AUTH_ID, 'recordedAt': timestamp, 'userEvidence': evidence,
        'researchRecord': RESEARCH.relative_to(ROOT).as_posix(), 'researchSha256': RESEARCH_SHA,
        'fullProductionAuthorized': True, 'finiteBatch': True, 'localFinalReviewOnly': True,
        'youtubeActions': False, 'driveActions': False, 'mediaRoot': str(MEDIA).replace('\\', '/'),
        'resourcePermission': {'authorized': False, 'reason': 'Actual production Unity Editor detected; new-batch resource permission not inferred from older Factorio-only exception.'},
        'projects': rows})
    save_absent(BATCH / 'checkpoint.json', {'revision': REVISION, 'status': 'preproduction',
        'recordedAt': timestamp, 'userEvidence': evidence, 'projects': rows,
        'productionJobsStarted': 0, 'generatedReviewVideos': 0,
        'next': 'Acquire and inspect actual independent FHD game evidence, finalize scripts, author Unity scenes, resolve resource guard, then run expensive jobs one at a time.',
        'humanFinalReview': 'pending', 'platformActions': False})
    save_absent(BATCH / 'readiness.json', {'revision': REVISION, 'internalProductionReadinessOnly': True,
        'projects': {r['slug']: {'codeReadyForActualProduction': False, 'productionCodeSha256': {}} for r in rows}})
    print(json.dumps({'projects': len(rows), 'batch': str(BATCH), 'media': str(MEDIA),
                      'generatedMedia': False, 'platformActions': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
