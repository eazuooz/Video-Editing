"""Inspect only remaining unviewed native boundaries, without selecting them."""
import pathlib,importlib.util
H=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('native_inspection',H/'inspect-native-extension.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.O=m.P/'production/local/beginner-revision-v1/native-boundaries-5'
m.rows=[
 ('quake-opening','production/research/game-lighting-history/local/steam-quake-launch-2021.mp4',6,10),
 ('quake-corridor','production/research/game-lighting-history/local/steam-quake-launch-2021.mp4',43,47),
 ('quake-stone','production/research/game-lighting-history/local/steam-quake-launch-2021.mp4',59,61),
 ('quake2-a','production/research/game-lighting-history/local/bethesda-quake2-enhanced-2023.mp4',43,48),
 ('quake2-b','production/research/game-lighting-history/local/bethesda-quake2-enhanced-2023.mp4',54,58),
 ('shadow-camera','production/research/game-lighting-history/local/epic-lighting-techniques.mp4',2382,2400),
]
if __name__=='__main__':m.main()
