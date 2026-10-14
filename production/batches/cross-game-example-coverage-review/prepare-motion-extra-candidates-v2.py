from pathlib import Path
import os
root=Path('D:/Github/Video-Editing');raw=root/'shared/assets/presenting-game-scores/raw'
assert os.path.samefile(root/'shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',raw/'motion-four-games-portal2-v1.mp4')
html=(raw/'motion-comparison-native-review-v1.html').read_text('utf-8')
marker='<button id="play">'
new='<button data-id="Portal99.032267-112.4" data-src="motion-four-games-portal2-v1.mp4" data-start="99.032267" data-stop="112.4">Prepare Portal99.032267-112.4</button><button data-id="PowerWash227.3-251.5" data-src="motion-powerwash-additional-native-v1.mp4" data-start="227.3" data-stop="251.5">Prepare PowerWash227.3-251.5</button>'
dst=raw/'motion-extra-native-review-v2.html'; assert not dst.exists()
dst.write_text(html.replace(marker,new+marker),encoding='utf-8')
print('additional native candidate controls prepared; media copy0/render0')
