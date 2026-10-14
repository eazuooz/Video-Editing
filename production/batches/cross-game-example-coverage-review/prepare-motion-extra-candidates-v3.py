from pathlib import Path
raw=Path('D:/Github/Video-Editing/shared/assets/presenting-game-scores/raw')
dst=raw/'motion-extra-native-review-v3.html';assert not dst.exists()
html=(raw/'motion-extra-native-review-v2.html').read_text('utf-8')
b='<button data-id="Portal40.006633-58.024633" data-src="motion-four-games-portal2-v1.mp4" data-start="40.006633" data-stop="58.024633">Prepare Portal40.006633-58.024633</button>'
dst.write_text(html.replace('<button id="play">',b+'<button id="play">'),encoding='utf-8')
print('Portal unused intervening window prepared; no media acquisition or render')
