"""Prepare the already-reviewed CPU extractor for only ten new intervals."""
from pathlib import Path
base=Path(__file__).resolve().parent
target=base/'extract-additional-edges-v3.py'
assert not target.exists()
text=(base/'extract-additional-edges-v2.py').read_text(encoding='utf-8')
text=text.replace('additional-action-bank-candidates-v2.json','source-action-bank-v3.json')
text=text.replace('resource-observation-v13.json','resource-observation-v15.json')
text=text.replace("assert len(bank['clips'])==13","assert len(bank['clips'])==10")
text=text.replace('additional-cut-edges-v2','additional-cut-edges-v3')
text=text.replace('additional-cut-edges-execution-v2.json','additional-cut-edges-execution-v3.json')
text=text.replace("c['requiresNewBoundaryExtraction']", "c.get('requiresNewBoundaryExtraction',False)")
text=text.replace('Directly read13 refined boundary boards and compare retained actions with old source bank. Preserve current11PCM; exact cuts, final ratio, narration, render and upload remain unapproved.','Directly read10 new boundary boards:9 Hype Train and1 trimmed rainy-container. Preserve current11PCM and147.2s white; source framing, final ratio, narration, render and private remain unapproved.')
text=text.replace("assert not out.exists(),'Preserve extracted files; no repeat'","assert not out.exists(),'Preserve extracted files; no repeat'")
target.write_text(text,encoding='utf-8')
print(target)
