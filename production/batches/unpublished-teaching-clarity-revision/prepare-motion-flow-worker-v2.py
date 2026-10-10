from pathlib import Path
B=Path(__file__).resolve().parent
text=(B/'prepare-motion-final-flow-helper-v1.py').read_text('utf-8-sig')
text=text.replace('final-pair-execution-v1','final-pair-execution-v2').replace('motion-reviewed-current-pair-v1','motion-reviewed-current-pair-v2').replace('motion-final-flow-review-v1','motion-final-flow-review-v2').replace('final-flow-helper-preparation-v1','final-flow-helper-preparation-v2')
out=B/'prepare-motion-final-flow-helper-v2.py';assert not out.exists();out.write_text(text,'utf-8')
print('Prepared currentV2 hardlink/helper worker, not yet executed.')
