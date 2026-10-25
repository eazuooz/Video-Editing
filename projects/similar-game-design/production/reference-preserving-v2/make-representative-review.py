"""Reuse final cut pixels, exact captions and current mixed audio for bounded QA."""
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audio_pipeline import require_authorized
from storage_paths import repo_path, relative


def main():
    require_authorized('bounded representative final-layout review')
    plan = json.loads((HERE / 'edit-plan-final.json').read_text('utf-8-sig'))
    output = repo_path(plan['outputDir'])
    qa = output / 'qa'
    qa.mkdir(exist_ok=True)
    selected = {'cut007', 'cut013', 'cut016', 'cut018', 'cut022'}
    records = []
    for cut in plan['cuts']:
        if cut['id'] not in selected:
            continue
        file = qa / (cut['id'] + '-captioned-sample.mp4')
        if not file.exists():
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-threads', '2',
                '-i', str(output / (cut['id'] + '.mp4')),
                '-ss', f"{cut['startFrame'] / 60:.9f}", '-i', str(output / 'final-mix.wav'),
                '-map', '0:v:0', '-map', '1:a:0',
                '-vf', f"setpts=PTS+{cut['startFrame']}/(60*TB),ass=captions.ko.ass,setpts=PTS-STARTPTS",
                '-t', f"{cut['frames'] / 60:.9f}", '-frames:v', str(cut['frames']),
                '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-movflags', '+faststart', '-n', str(file)], cwd=output, check=True)
        records.append({'cut': cut['id'], 'globalStart': cut['startFrame'] / 60,
                        'frames': cut['frames'], 'file': relative(file)})
    (qa / 'representative-review-inputs.json').write_bytes((json.dumps({
        'scope': 'Five representative cuts only; complete review pending', 'samples': records,
        'captionTiming': 'Actual global ASS clock translated exactly to each cut origin',
        'sourceSpeechUnchanged': True}, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps(records))


if __name__ == '__main__':
    main()
