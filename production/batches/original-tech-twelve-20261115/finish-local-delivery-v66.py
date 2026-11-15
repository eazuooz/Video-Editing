"""Finish this exact12 local delivery once, after the existing producer completes."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

import psutil

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
M = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
R = M / 'production-resume-20261115T055255Z'
PY = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def pin(path):
    return dict(path=str(path.resolve()), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def run(script, args, receipt):
    assert not receipt.exists()
    result = subprocess.run(
        [str(PY), '-u', '-X', 'utf8', str(script), *args],
        cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        encoding='utf8', creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode:
        raise RuntimeError(f'{script.name} failed: {result.stdout}\n{result.stderr}')
    data = json.loads(result.stdout.strip())
    receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
    return data


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    receipt = R / 'final-delivery-prepared-v66.json'
    assert not receipt.exists()
    assert not (H / 'local-final-review-v1.html').exists()
    projects = read(H / 'batch.json')['projects']
    assert len(projects) == 12
    completion = M / 'finite-reviewed-finals-v54/completion.json'
    deadline = time.monotonic() + 15 * 60
    while not completion.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError('Existing finite producer did not complete; no retry or foreign-process action')
        time.sleep(10)
    complete = read(completion)
    assert len(complete['done']) == 8 and not complete['held']
    assert all((M / p['slug'] / 'final-review-v1/bundle.json').exists() for p in projects)
    checked = run(H / 'collect-local-final-review-v2.py', [], R / 'final-collection-readonly-v66.json')
    assert checked['verifiedFinalBundles'] == 12 and not checked['pending']
    prepared = run(H / 'collect-local-final-review-v2.py', ['--deliver'], R / 'final-collection-delivery-v66.json')
    assert prepared['verifiedFinalBundles'] == 12 and prepared['finalDeliveryPrepared']
    reconciled = run(H / 'finalize-production-progress-v64.py', [], R / 'final-reconciliation-run-v64.json')
    assert reconciled['progress']['finalVideos'] == 12
    published = run(R / 'publish-production-resume-v64.py', [], R / 'final-publish-run-v64.json')
    assert published['remoteVerified'] and published['finalVideos'] == 12
    data = dict(
        exactProjects=12, verifiedFinalBundles=12,
        page=pin(H / 'local-final-review-v1.html'),
        manifest=pin(H / 'local-final-review-manifest-v1.json'),
        validation=reconciled['validation'], publishedCommit=published['commit'],
        collectorReadOnly=pin(R / 'final-collection-readonly-v66.json'),
        collectorDeliveryPreparation=pin(R / 'final-collection-delivery-v66.json'),
        finiteProductionCompletion=pin(completion),
        deliveryPostedInChat=False, humanApproval=False, platformActions=[],
        original111AndOtherAutomationsChanged=False,
    )
    receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    main()
