from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parent;R=P.parents[3];N=P.parent/'reference-preserving-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
t=read(P/'final-timeline-v1.json');dest=P/'publishing';dest.mkdir(exist_ok=True)
assert not (dest/'description.ko.txt').exists()
oldko=(N/'publishing/description.ko.txt').read_text(encoding='utf-8');olden=(N/'publishing/description.en.txt').read_text(encoding='utf-8')
footerko=oldko[oldko.index('🎮 게임 개발'):];footeren=olden[olden.index('Programming coaching\n'):]
pokeko='Pokémon Red — FCPlaythroughs, https://www.youtube.com/watch?v=D1SrSFZrV7A . 채널의 녹화 사용 허용 안내를 확인하고, 해당 녹화의 일부를 선택·재구성해 설명과 자막을 추가했습니다.'
pokeen='Pokémon Red — FCPlaythroughs, https://www.youtube.com/watch?v=D1SrSFZrV7A . Recording excerpts selected and reframed with original narration and captions, under the channel’s stated footage-reuse permission.'
def chapters(lang):
 script={s['id']:s['title'] for s in read(P/f'narration.{lang}.json')['scenes']};rows=[]
 for i,sc in enumerate(t['scenes']):
  seconds=0 if i==0 else sc['startFrame']//60
  rows.append(f'{seconds//60:02}:{seconds%60:02} '+script[sc['id']])
 seconds=(t['totalFrames']-600)//60;rows.append(f'{seconds//60:02}:{seconds%60:02} '+('멤버쉽가입 감사드립니다.' if lang=='ko' else 'Thanks to our members'))
 return '\n'.join(rows)
ko='메모가 많아질수록 필요한 규칙을 찾기 어려워지나요? 포켓몬 초기작을 소재로 만든 기획 메모를 탐험·전투·아이템 사용으로 묶으며, 계층형 정보가 필요한 이유부터 살펴봅니다.\n\n이어서 슈퍼 스매시브라더스 얼티밋의 메뉴와 기술 설명을 통해 접기·순서 이동·단계 변경을 구분하고, 다른 사람에게 전달할 문서로 다듬습니다. 화면의 기획문서는 직접 만든 설명용 예시이며 실제 개발사의 원본 문서가 아닙니다. 게임 화면은 별도로 확보한 플레이·메뉴 조작 녹화입니다.\n\n'+chapters('ko')+'\n\n'+footerko.rstrip()+'\n'+pokeko+'\n'
en='Why does a long list of design notes need levels? Start with an illustrative document based on early Pokémon, grouping Exploration, Battles, and Item Use so that related rules can be found together.\n\nThen use Super Smash Bros. Ultimate menus and move descriptions to distinguish collapsing, moving, and changing levels, before preparing a document for another reader. The planning document is our own teaching example, not an original developer document. Gameplay and menu operations come from independently obtained recordings.\n\n'+chapters('en')+'\n\n'+footeren.rstrip()+'\n'+pokeen+'\n'
for lang,text in [('ko',ko),('en',en)]:
 assert len(text)<5000 and not re.search('사쿠라이|마사히로|Sakurai|桜井',text,re.I)
 (dest/f'description.{lang}.txt').write_text(text,encoding='utf-8')
titles={'ko':'계층형 아웃라인으로 게임 기획서 정리하기 | 포켓몬 기획 메모부터 접기·이동까지','en':'Organize Game Design Notes with Hierarchical Outlines | A Pokémon Example'}
(dest/'titles.json').write_text(json.dumps(titles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'pinned-comment.ko.txt').write_text('포켓몬 기획 메모처럼 관련 조건과 결과를 같은 가지에 묶어 보세요. 접기·순서 이동·단계 변경은 서로 다른 작업입니다.\n\n프로그래밍 과외: https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\n',encoding='utf-8')
print(chapters('ko'));print('Description lengths',len(ko),len(en));print('PRIVATE only; prior uploads and reservations unchanged.')
