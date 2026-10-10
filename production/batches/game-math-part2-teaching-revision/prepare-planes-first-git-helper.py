"""Adapt the reviewed isolated-index delivery helper for this plane episode."""
from pathlib import Path
B=Path(__file__).parent
s=(B/'deliver-lines-second-git.py').read_text(encoding='utf8')
s=s.replace('one reviewed lines episode','one reviewed plane episode').replace('lines-second','planes-first')
s=s.replace("'__pycache__' not in p.parts", "'__pycache__' not in p.parts and 'delivery-history' not in p.parts")
s=s.replace('game-math-bounds-transform-v2','game-math-plane-distances-v2')
s=s.replace("for suffix in ['bounds-teaching-additions-v2','narration-retakes-v3','opening-retake-v4','numeric-retakes-v5','unit-retake-v6']:add_tree(ROOT/'projects'/('game-math-lines-'+suffix))", "for suffix in ['teaching-additions-v2','retakes-v3']:add_tree(ROOT/'projects'/('game-math-planes-'+suffix))")
s=s.replace("('lines' in p.name or p.name in ['README.md','queue.json','interpolation-git-delivery.json','complete-revision-source-records.py'])", "('planes' in p.name or p.name in ['README.md','queue.json','lines-second-git-delivery.json'])")
s=s.replace("B/'lines-tracks',B/'baselines/game-math-lines-bounds'", "B/'planes-tracks',B/'baselines/game-math-planes-barycentric'")
s=s.replace('lines_additions.py','planes_additions.py')
start=s.index(' # Reviewed documentation repair')
end=s.index(' registry=read',start)
s=s[:start]+s[end:]
s=s.replace('Deliver coherent bounds and transform lecture with reviewed private upload','Deliver coherent plane distance lecture with reviewed private upload')
s=s.replace("['W5UkJkep7yo']", "['Rzrt47-u4G0']")
s=s.replace("if i['slug']=='game-math-lines-bounds'", "if i['slug']=='game-math-planes-barycentric'")
s=s.replace('secondEpisodeGitDelivered','firstEpisodeGitDelivered').replace('secondEpisodeGitCommit','firstEpisodeGitCommit').replace('secondEpisodeRemoteVerifiedSha','firstEpisodeRemoteVerifiedSha')
(B/'deliver-planes-first-git.py').write_text(s,encoding='utf8')
print('Prepared plane-specific isolated index delivery helper')
