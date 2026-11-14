"""Resume the finite, selected recap jobs; never advance another production batch."""
import os
import shutil
import subprocess
import sys

from prepare import HERE, ROOT, WORK, VOICE_LOCAL, RECAPS, read, save


def run(filename, *args):
    python = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
    subprocess.run([str(python), '-X', 'utf8', str(HERE / filename), *args], check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)


def main():
    plan = read(HERE / 'plan.json')
    row = next(r for r in plan['episodes'] if r['id'] == 'A09')
    revised = row['recapKo'] != RECAPS['A09'][0]
    if revised:
        row['recapKo'], row['recapEn'] = RECAPS['A09']
        save(HERE / 'plan.json', plan)
        script = read(VOICE_LOCAL / 'recaps.json')
        target = next(r for r in script['scenes'] if r['id'] == 'A09')
        target.update(lines=[RECAPS['A09'][0]], en=RECAPS['A09'][1])
        save(VOICE_LOCAL / 'recaps.json', script)
        wav = VOICE_LOCAL / 'voice/chunks/A09-scene.wav'
        if wav.exists():
            preserved = wav.with_name('A09-before-diction-retake.wav')
            if not preserved.exists():
                shutil.copyfile(wav, preserved)
            wav.unlink()
    if not (VOICE_LOCAL / 'voice/chunks/A09-scene.wav').exists():
        run('render_recaps.py', '--episodes', 'A09')
    run('check_recaps.py', 'A09')
    for entry in plan['episodes']:
        ep = entry['id']
        receipt = WORK / ep / 'assembly/summary-components.json'
        if not receipt.exists() or read(receipt).get('summaryKo') != RECAPS[ep][0]:
            run('finish_episode.py', ep)
    print('All sixteen recap components ready; native-picture adoption remains a separate gate.', flush=True)


if __name__ == '__main__':
    main()
