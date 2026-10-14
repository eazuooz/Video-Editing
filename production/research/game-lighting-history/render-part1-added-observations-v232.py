"""Generate only two newly observed paragraphs; preserve all selected narration."""
from pathlib import Path
source=Path(__file__).with_name('render-part1-scoped-repair-v176.py').read_text('utf-8')
source=source.replace('part1-scoped-repair-tts-request-v176','part1-added-observations-tts-request-v232').replace('part1-scoped-repair-tts-execution-v176','part1-added-observations-tts-execution-v232').replace('episode04Part1ScopedTtsV176','episode04Part1AddedObservationsTtsV232').replace('.tts176.tmp','.tts232.tmp')
exec(compile(source,str(__file__),'exec'))
