"""Inspect remaining concept-specific source boundaries; no automatic selection."""
import pathlib,importlib.util
H=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('native_inspection',H/'inspect-native-extension.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.O=m.P/'production/local/beginner-revision-v1/native-final-candidates-6'
m.rows=[
 ('far-shadow-actor','production/research/game-lighting-history/local/epic-lighting-techniques.mp4',2254,2296),
 ('ao-opening','production/research/game-lighting-history/local/epic-post-processing.mp4',3076,3085),
 ('ao-boundary','production/research/game-lighting-history/local/epic-post-processing.mp4',3103,3105),
 ('quake2-opening','production/research/game-lighting-history/local/bethesda-quake2-enhanced-2023.mp4',14,28),
]
if __name__=='__main__':m.main()
