"""Create complete scene WAVs with the approved Qwen voice and sentence-boundary joins."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import soundfile as sf

B = Path(__file__).resolve().parent
R = B.parents[2]
sys.path.insert(0, str(R/'qwen3-tts'))
import render_narration as voice
from gpu_handoff_guard import schedule_gpu_handoff


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def group_sentences(lines, limit):
    groups = []
    current = []
    for line in lines:
        if current and len(' '.join([*current, line])) > limit:
            groups.append(' '.join(current))
            current = []
        current.append(line)
    if current:
        groups.append(' '.join(current))
    if len(groups) > 1 and len(groups[-1]) < 55 and len(groups[-2])+len(groups[-1]) < limit+30:
        groups[-2:] = [' '.join(groups[-2:])]
    return groups


def quiet_edge(wave, sr):
    """Count only consecutive very quiet 10 ms blocks at the edge."""
    step = sr//100
    end = 0
    for start in range(0, min(len(wave)-step+1,sr*2), step):
        if np.mean(wave[start:start+step]**2) > .0014**2:
            break
        end += step
    return end


def join_groups(items, output):
    pieces = []
    boundaries = []
    sr = sf.info(items[0].path).samplerate
    tail = 0
    for index, item in enumerate(items):
        signal, rate = sf.read(item.path, dtype='float32')
        if rate != sr or signal.ndim != 1 or not len(signal):
            raise ValueError(f'Unexpected format for {item.path}')
        head = quiet_edge(signal,sr)
        end = quiet_edge(signal[::-1],sr)
        if index:
            signal = signal[max(0,head-int(.10*sr)):]
            head = min(head,int(.10*sr))
            gap = max(0,int(.16*sr)-tail-head)
            if gap:
                pieces.append(np.zeros(gap,dtype='float32'))
        if index < len(items)-1 and end > int(.18*sr):
            signal = signal[:len(signal)-end+int(.18*sr)]
        tail = min(end,int(.18*sr))
        fade = min(round(.004*sr),len(signal)//2)
        if fade and len(items)>1:
            signal = signal.copy()
            if index:
                signal[:fade] *= np.linspace(0,1,fade,dtype=np.float32)
            if index < len(items)-1:
                signal[-fade:] *= np.linspace(1,0,fade,dtype=np.float32)
        boundaries.append(sum(map(len,pieces))/sr)
        pieces.append(signal)
    temp = output.with_suffix('.assembling.wav')
    if len(items)==1:
        shutil.copyfile(items[0].path,temp)
    else:
        sf.write(temp,np.concatenate(pieces),sr,subtype=sf.info(items[0].path).subtype)
    temp.replace(output)
    return boundaries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project',required=True)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--repair-scenes',default='')
    parser.add_argument('--max-group',type=int,default=210)
    args = parser.parse_args()
    project = R/'projects'/args.project
    h = project/'production/series-v1'
    assert (R/args.manifest).resolve() == (h/'tts-manifest.json').resolve()
    binding = json.loads((h/'production-binding.json').read_text('utf8'))
    batch = json.loads((B/'batch.json').read_text('utf8'))
    assert binding['episode'] in batch['episodeIds'] and batch['ttsAuthorized']
    voice.configure_project(args.project,args.manifest)
    schedule_gpu_handoff(args.project,'cuda:0',False,voice.GPU_MINIMUM_FREE_MIB)
    voice.load_tts_dependencies()
    jobs = voice.load_jobs()
    scene_items = voice.build_render_items(jobs)
    groups = (h/'narration-pairs.txt').read_text('utf8').strip().split('\n\n')
    assert len(groups)==len(scene_items)
    selected = set(filter(None,args.repair_scenes.split(',')))
    assert selected <= {x.key.split('-')[0] for x in scene_items}
    out = voice.CHUNK_DIR
    parts = out.parent/'sentence-groups'
    parts.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    recipe = hashlib.sha256((h/'tts-manifest.json').read_bytes()).hexdigest()
    to_join = []
    for item, group in zip(scene_items,groups):
        sid = item.key.split('-')[0]
        if selected and sid not in selected:
            assert voice.valid_wav(item.path)
            continue
        if not selected and voice.valid_wav(item.path):
            continue
        sentences = [line.split(' | ',1)[0].strip() for line in group.splitlines()]
        assert ' '.join(sentences)==item.text, f'Changed narration for {sid}'
        fragments = []
        for n, text in enumerate(group_sentences(sentences,args.max_group),1):
            key = hashlib.sha256((recipe+'\0'+text).encode()).hexdigest()[:18]
            fragments.append(voice.RenderItem(f'{sid}-{n:02}',text,parts/f'{sid}-{n:02}-{key}.wav'))
        to_join.append((item,fragments))
    # Shorter inputs use the same model, reference recording, language and acoustic checks.
    work = [piece for _, fragments in to_join for piece in fragments]
    voice.MAX_NEW_TOKENS = min(voice.MAX_NEW_TOKENS,1024)
    voice.render_chunks(work,1)
    receipt = out.parent/'sentence-groups.json'
    record = json.loads(receipt.read_text('utf8')) if receipt.is_file() else {}
    for target, fragments in to_join:
        for fragment in fragments:
            if sf.info(fragment.path).duration >= voice.MAX_NEW_TOKENS/12.5-.2:
                raise ValueError(f'Generation limit in {fragment.key}; retry that scene with shorter sentence groups')
        if target.path.is_file():
            archive=parts/'previous';archive.mkdir(exist_ok=True)
            backup=archive/f'{target.path.stem}-{digest(target.path)[:16]}.wav'
            if not backup.is_file():
                shutil.copy2(target.path,backup)
        starts=join_groups(fragments,target.path)
        record[target.key]={'sceneSha256':digest(target.path),'parts':[
            {'text':part.text,'startSeconds':start,'sha256':digest(part.path)} for part,start in zip(fragments,starts)]}
    receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
    voice.assemble_outputs(jobs)


if __name__=='__main__':
    main()
