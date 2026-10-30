"""Manually chosen clause boundaries; exact complete narration is preserved."""
import json
from scoped_context import ROOT, read


def main():
    records = {
      'shorts-starcraft-eud-compatibility-emulator': {
        'p1-1': [('스타크래프트인데,','It is StarCraft,'),('길을 따라오는 적을 막는 디펜스 게임이 됐죠.','turned into a lane-defense game.')],
        'p1-2': [('이런 유저맵의 자유를 살리려고,','To keep this custom-map freedom alive,'),('블리자드는 에뮬레이터까지 만들었습니다.','Blizzard even built an emulator.')],
        'p2-2': [('제작자들은 이 기능을 예상 밖으로 활용해,','Creators used that feature in unexpected ways,'),('원래 없던 규칙을 만들었어요.','building rules the original game never had.')],
        'p3-2': [('하지만 같은 틈이 보안 공격에도 쓰일 수 있어서,','But that opening could also enable attacks,'),('사용이 막혔죠.','so its use was blocked.')],
        'p4-1': [('문제는 그 기능에 기대던 옛 유저맵도','But custom maps that depended on it'),('작동하지 않는다는 겁니다.','could no longer work.')],
        'p4-2': [('옛 맵의 요청과 새 게임 사이에','Between the old request and the new game,'),('통역기를 둔다면 어떨까요?','what if we put a translator?')],
        'p5-2': [('지원하는 옛 요청을 받아,','It accepts supported old requests,'),('새 게임의 데이터에 맞게 처리합니다.','and handles them using the new game data.')],
        'p6-2': [('모든 기능을 복원한 건 아니지만,','It did not restore every feature,'),('보안을 지키면서','but it preserved security'),('유저가 만든 놀이를 살린 거예요.','while keeping user-created play alive.')],
      },
      'shorts-starcraft2-replay-input-resimulation': {
        'p1-1': [('스타크래프트 투 리플레이에선,','In a StarCraft II replay,','스타크래프트 II 리플레이에선,'),('지난 경기를 보면서 시점을 옮길 수 있죠.','you can move the view around a past match.')],
        'p2-1': [('저장하는 핵심은 매 순간의 화면이 아니라,','The essential record is not every rendered frame,'),('플레이어가 내린 명령입니다.','but the commands given by players.')],
        'p3-1': [('우리 예시에선','In our example,'),('이 초에 이동,','move at two seconds,','2초에 이동,'),('사 초에 공격을 기록해 볼게요.','and record an attack at four.','4초에 공격을 기록해 볼게요.')],
        'p4-1': [('출발 상태와 규칙이 같으면,','With the same starting state and rules,'),('움직임과 전투 결과도 다시 나옵니다.','movement and combat results return.')],
        'p4-2': [('같은 조건에서 같은 결과가 나오는','The same conditions give the same result:'),('결정론적 시뮬레이션이죠.','deterministic simulation.')],
        'p5-1': [('그런데 규칙이 패치로 바뀌었다면','But if a patch changes the rules,'),('결과도 달라질 수 있겠죠.','the result could change too.')],
        'p5-2': [('그래서 원래 맵과 게임 실행파일,','So the original map, executable,'),('데이터 버전을 맞춰야 합니다.','and game-data version must match.')],
        'p6-2': [('이 조건을 맞추고 명령을 다시 실행해서,','Match those conditions and replay the commands,'),('지난 경기를 살아 있는 게임처럼 보는 겁니다.','and the old match becomes a running game again.')],
      },
    }
    for slug, splits in records.items():
        path = ROOT / 'projects' / slug / 'script/caption-clauses.json'; doc = read(path); out = []
        for row in doc['clauses']:
            if row['id'] not in splits or any(q['id'] == row['id'] + 'b' for q in doc['clauses']):
                out.append(row); continue
            parts = splits[row['id']]
            if ''.join(row['spoken'].split()) != ''.join(''.join(p[0].split()) for p in parts): raise RuntimeError('Narration would change: ' + row['id'])
            for i, part in enumerate(parts):
                spoken, english = part[:2]
                out.append({**row, 'id': row['id'] + (chr(97 + i) if i else ''), 'spoken': spoken,
                            'ko': part[2] if len(part) > 2 else spoken, 'en': english})
        doc['clauses'] = out
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__': main()
