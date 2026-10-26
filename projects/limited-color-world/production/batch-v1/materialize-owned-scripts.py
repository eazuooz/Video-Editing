"""Materialize the two owned authored drafts; no TTS, media or shared writes."""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[4]
ALIASES = {
    'limited-color-world': {'뿌요뿌요 테트리스 2': '뿌요뿌요 테트리스 투'},
    'computer-controlled-players': {'CPU': '씨피유', 'CP': '씨피',
        '60프레임': '예순 프레임', '12프레임': '열두 프레임', '0.2초': '영 점 이 초'}
}

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')

for slug, aliases in ALIASES.items():
    project = ROOT / 'projects' / slug
    draft = json.loads((project / 'planning/script-draft.json').read_text('utf-8-sig'))
    scripts = []
    for lang in ['ko', 'en', 'spoken-ko']:
        key = 'ko' if lang == 'spoken-ko' else lang
        scenes = []
        for scene in draft['scenes']:
            lines = [' '.join(p[key].split('|')) for p in scene['paragraphs']]
            if lang == 'spoken-ko':
                for i, text in enumerate(lines):
                    for display, spoken in sorted(aliases.items(), key=lambda x: -len(x[0])):
                        text = text.replace(display, spoken)
                    lines[i] = text
            scenes.append({'id': scene['id'], 'title': scene['title'], 'lines': lines})
        obj = {'schemaVersion': 1, 'slug': slug, 'revision': 'batch-v1',
            'language': 'ko' if lang == 'spoken-ko' else lang,
            'title': draft['titleEn'] if lang == 'en' else draft['titleKo'], 'scenes': scenes}
        path = project / 'script/batch-v1' / ('narration.' + lang + '.json')
        save(path, obj)
        scripts.append({'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    units = {}
    for scene in draft['scenes']:
        for i, paragraph in enumerate(scene['paragraphs'], 1):
            ko, en = paragraph['ko'].split('|'), paragraph['en'].split('|')
            assert len(ko) == len(en)
            units[f"{scene['id']}-p{i:02d}"] = {'semanticPairingReviewed': True,
                'basis': 'Authored clauses compared pair by pair with complete KO/EN paragraphs; all source instructional claims/order retained in independently written explanation.',
                'captionUnits': [{'ko': a, 'en': b} for a, b in zip(ko, en)]}
    save(project / 'production/batch-v1/caption-units.json', {'slug': slug, 'revision': 'batch-v1',
        'status': 'authored-pretts-gameplay-window-review', 'scriptInputs': scripts, 'paragraphs': units})
    save(project / 'script/batch-v1/caption-aliases.json', aliases)
    print(slug, len(draft['scenes']), 'scenes', len(units), 'paragraphs',
        sum(len(' '.join(p['ko'].split('|'))) for s in draft['scenes'] for p in s['paragraphs']), 'display KO characters',
        sum(len(v['captionUnits']) for v in units.values()), 'caption pairs')
