"""Lossless spoken clause split for the measured fixed 60px caption geometry."""
from scoped_context import ROOT, read
import json

def main():
    path = ROOT / 'projects/shorts-sea-of-thieves-water-masking/script/caption-clauses.json'
    doc = read(path)
    splits = {
        'p2-2': [('넓은 바다 면을 그대로 그리면,', 'Draw the whole ocean surface,'), ('선체를 뚫고 내부까지 들어옵니다.', 'and it passes through the hull into the cabin.')],
        'p3-1': [('그래서 배 안쪽에 맞춘 보이지 않는 틀,', 'Add an invisible shape fitted to the inside:'), ('마스크 메시를 둡니다.', 'a mask mesh.')],
        'p4-2': [('마스크만 켰더니, 바깥 파도는 그대로인데', 'Turn on only the mask; the outside waves stay the same,'), ('배 안의 바다는 사라졌죠.', 'but the ocean inside disappears.')],
        'p5-2': [('이번엔 반대로,', 'Now reverse the visible region:'), ('틀 안에만 보이는 수면을 따로 두고', 'use a separate surface visible only inside,'), ('높이를 올립니다.', 'then raise its level.')],
        'p6-2': [('각 수면이 보일 영역을 따로 정해서,', 'Give each surface its own visible region,'), ('거친 바다와 배 안의 침수를', 'so rough seas and flooding inside'), ('함께 보여 주는 겁니다.', 'can appear together.')],
    }
    out = []
    for row in doc['clauses']:
        if row['id'] not in splits or any(q['id'] == row['id'] + 'b' for q in doc['clauses']):
            out.append(row); continue
        parts = splits[row['id']]
        if ''.join(row['spoken'].split()) != ''.join(''.join(p[0].split()) for p in parts):
            raise RuntimeError('Do not change narration while splitting ' + row['id'])
        for index, (spoken, english) in enumerate(parts):
            new = {**row, 'id': row['id'] + (chr(97 + index) if index else ''), 'spoken': spoken, 'ko': spoken, 'en': english}
            if new.get('emphasis', {}).get('text') not in spoken: new.pop('emphasis', None)
            out.append(new)
    doc['clauses'] = out
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

if __name__ == '__main__': main()
