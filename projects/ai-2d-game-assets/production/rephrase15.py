from pathlib import Path
P=Path(__file__).resolve().parents[1]
changes=[('캐릭터가 정리되면 배경을 맞출 차례입니다.','이제 완성한 캐릭터 옆에 배경을 놓아 보겠습니다.'),('Once the character is prepared, match the background.','Now place a background alongside the prepared character.')]
for base in [P/'script',P/'planning']:
 for f in base.iterdir():
  if f.suffix not in ('.json','.md'):continue
  old=f.read_text('utf-8');new=old
  for a,b in changes:new=new.replace(a,b)
  if new!=old:f.write_text(new,'utf-8');print(f.name)
