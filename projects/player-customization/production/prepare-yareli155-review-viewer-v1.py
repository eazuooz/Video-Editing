"""Prepare a narrow read-only local viewer from the owned research template."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
p=BASE/'yareli155-review-server-v1.cjs'
assert not p.exists(),'Reuse the prepared viewer instead of recreating it.'
s=(BASE/'dante-review-server-v1.cjs').read_text('utf-8-sig')
start=s.index('const files={');end=s.index('const html=',start)
s=s[:start]+"const files={yareli155:path.join(root,'shared/output/player-customization/research/yareli-devstream155-v1/8eUfnQ8mWXs-yareli-2721-3087.mp4')};\n"+s[end:]
s=s.replace('9245','9248')
s=s.replace('Dante/Jade/UI: 2024 developer previews','Yareli: 2021 official developer preview')
s=s.replace('<option value="dante">2024 Dante developer preview</option><option value="jade">2024 Jade preview</option><option value="ui">2024 UI/QoL preview</option>','<option value="yareli155">2021 Yareli developer preview</option>')
s=s.replace("let key='dante'","let key='yareli155'")
s=s.replace('{dante:2530,jade:1280,ui:3900}','{yareli155:2721}')
s=s.replace('Only three acquired local research sources including Dante','Only acquired local Yareli155 source')
s=s.replace('Player customization native research review','Player customization Yareli155 native review')
p.write_text(s,'utf-8')
print(p.relative_to(ROOT).as_posix())
