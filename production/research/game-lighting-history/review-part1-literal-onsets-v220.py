"""Five changed whole/complete contexts; no unchanged69 or original111 repeat."""
from pathlib import Path
source=Path(__file__).with_name('review-part1-onset-replacements-v209.py').read_text('utf-8')
source=source.replace('part1-selected-current-tts-request-v208','part1-selected-current-tts-request-v219').replace('part1-selected-current-tts-execution-v208','part1-selected-current-tts-execution-v219').replace('part1-onset-replacement-asr-execution-v209','part1-literal-onset-asr-execution-v220').replace('part1-onset-replacement-asr-v209','part1-literal-onset-asr-v220').replace('review-part1-onset-replacements-v209.py','review-part1-literal-onsets-v220.py')
exec(compile(source,str(__file__),'exec'))
