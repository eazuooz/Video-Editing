"""Finite local revision queue; wait only for this task's current software capture."""
import subprocess
import time

from prepare import ROOT, HERE, WORK, read, save


def run(filename, *args):
    log=WORK/('queue-'+filename.replace('.py','')+'-'+('-'.join(args).replace('/','_'))+'.log')
    with log.open('wb') as out:
        result=subprocess.run([str(ROOT / 'qwen3-tts/.venv/Scripts/python.exe'), '-X', 'utf8',
                        str(HERE / filename), *args], stdout=out,stderr=subprocess.STDOUT,
                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if result.returncode:
        print(log.read_text('utf-8',errors='replace')[-5000:],flush=True)
        result.check_returncode()


def main():
    target = WORK / 'anim_GrabValve_R-capture.json'
    deadline = time.monotonic() + 1200
    expected = read(WORK / 'anim_GrabValve_R-build.json')['builderSha256']
    while time.monotonic() < deadline:
        if target.exists() and read(target).get('builderSha256') == expected:
            break
        time.sleep(2)
    else:
        raise TimeoutError('This task’s hand capture has not finished; preserve all other jobs.')
    # The original finite queue already generated its first nineteen lines.
    # Retakes are a separate explicit stage after this unchanged-body assembly.
    for ep in ('A03', 'A09', 'A13', 'A16'):
        from prepare import OUTPUT
        if (OUTPUT/ep/'delivery.json').is_file():continue
        run('assemble_delivery.py', ep)
    print('Four retained-native recap deliveries assembled; encoded final-summary sampling still required.', flush=True)


if __name__ == '__main__':
    main()
