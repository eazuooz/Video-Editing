"""Versioned post-repair resource adapter; preserves every native guard.

Imports and source verification perform no process query, lease mutation or
render. Only busy_reason invokes the existing strict resource observation.
"""
from __future__ import annotations
import hashlib, importlib.util, sys, types, uuid
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PINS = {
    'run-solution-path-native-v4.py':'9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
    'run-first-native.py':'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9',
    'prospect-refuge-resource-qualification-v2.py':'fa045267401f4407ced7ffe7aed1a73cca0d48954cadaaaf31b64de01f5d0d4b',
}
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def checked_sources():
    if sha(__file__) != SELF_SHA: raise RuntimeError('Imported post-repair resource adapter changed')
    for name, expected in PINS.items():
        if not expected or sha(HERE/name) != expected: raise RuntimeError('Reviewed resource source changed: '+name)
def load(name):
    spec = importlib.util.spec_from_file_location('postrepair_resource_'+uuid.uuid4().hex,HERE/name)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
checked_sources()
native = load('run-solution-path-native-v4.py')
qualifier = load('prospect-refuge-resource-qualification-v2.py')
qualifier.BASE = native.BASE/'postrepair-resource-observations-v1'
rt = native.rt
scope = dict(native.__dict__,QUALIFIER=HERE/'prospect-refuge-resource-qualification-v2.py',
             QUALIFIER_SHA=PINS['prospect-refuge-resource-qualification-v2.py'],qualifier=qualifier)
# Private fresh function globals. Completed native-controller globals and
# qualifier1 remain untouched; this adapter exposes no capture/stage method.
scope['process_reason'] = types.FunctionType(native.process_reason.__code__,scope,'process_reason',native.process_reason.__defaults__)
_busy = types.FunctionType(native.busy_reason.__code__,scope,'busy_reason',native.busy_reason.__defaults__)
LAST_RESOURCE_CLASSIFICATION = None
def busy_reason(token=None):
    global LAST_RESOURCE_CLASSIFICATION
    checked_sources()
    reason = _busy(token)
    LAST_RESOURCE_CLASSIFICATION = scope.get('LAST_RESOURCE_CLASSIFICATION')
    return reason
