"""The one authorized D22 logical-D / physical-C media route, no I/O on import.

Only edit/ and rendered/ inside this exact directory can escape by junction.
Artifacts keep repository-relative D paths. A media writer must use local_output
and therefore cannot write before root's physical move/junction is verified.
Other C paths, including siblings, and nested symlink escapes are rejected.
"""
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LOGICAL = ROOT / 'projects/similar-game-design/production/local/reference-preserving-v2'
PHYSICAL = Path('C:/Users/1/.codex/video-production/similar-game-design/reference-preserving-v2')
OUTPUT_DIRS = ('edit','rendered')


def absolute(value):
    candidate = Path(value)
    return Path(os.path.abspath(candidate if candidate.is_absolute() else ROOT / candidate))


def routing_record():
    record = json.loads((HERE/'storage-routing.json').read_text('utf-8-sig'))
    if (record.get('project'),record.get('revision')) != ('similar-game-design','reference-preserving-v2'):
        raise ValueError('Storage route does not identify current D22 revision')
    if absolute(record['logicalRoot']) != absolute(LOGICAL) or absolute(record['physicalRoot']) != absolute(PHYSICAL):
        raise ValueError('Only the exact user-authorized D22 storage mapping is accepted')
    if tuple(record.get('allowedOutputSubdirectories',[])) != OUTPUT_DIRS:
        raise ValueError('Only edit and rendered output subdirectories are authorized')
    return record


def route_active(subdirectory):
    routing_record()
    if subdirectory not in OUTPUT_DIRS:
        return False
    logical,physical=LOGICAL/subdirectory,PHYSICAL/subdirectory
    return (logical.is_dir() and physical.is_dir() and logical.resolve()==absolute(physical)
            and physical.resolve()==absolute(physical))


def output_subdirectory(logical):
    if logical.is_relative_to(LOGICAL):
        parts=logical.relative_to(LOGICAL).parts
        return parts[0] if parts and parts[0] in OUTPUT_DIRS else None
    return None


def logical_path(value):
    raw = absolute(value)
    if raw.is_relative_to(absolute(PHYSICAL)):
        routing_record()
        logical = LOGICAL / raw.relative_to(absolute(PHYSICAL))
    elif raw.is_relative_to(absolute(ROOT)):
        logical = raw
    else:
        raise ValueError(f'Path outside repository or exact D22 media route: {raw}')
    resolved = raw.resolve()
    if logical.is_relative_to(LOGICAL):
        subdirectory=output_subdirectory(logical)
        if subdirectory and route_active(subdirectory):
            if not resolved.is_relative_to(absolute(PHYSICAL/subdirectory)):
                raise ValueError(f'Nested junction escapes the exact D22 physical root: {raw}')
        elif raw.is_relative_to(absolute(PHYSICAL)):
            raise ValueError('Physical D22 access requires the verified logical junction first')
        elif not resolved.is_relative_to(ROOT.resolve()):
            raise ValueError(f'Unverified local junction target: {raw}')
    elif not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError(f'Foreign repository junction/symlink is not authorized: {raw}')
    return logical


def repo_path(value):
    logical = logical_path(value)
    subdirectory=output_subdirectory(logical)
    if subdirectory and route_active(subdirectory):
        physical = (PHYSICAL / logical.relative_to(LOGICAL)).resolve()
        if not physical.is_relative_to(absolute(PHYSICAL/subdirectory)):
            raise ValueError('Nested media path escapes the exact D22 physical root')
        return physical
    return logical.resolve()


def relative(value):
    return logical_path(value).relative_to(ROOT).as_posix()


def local_output(value):
    logical = logical_path(value)
    if not logical.is_relative_to(LOGICAL):
        raise ValueError('Media output must remain inside current D22 local revision')
    subdirectory=output_subdirectory(logical)
    if not subdirectory:
        raise ValueError('New D22 local media writes are restricted to the exact edit/ and rendered/ junctions')
    if not route_active(subdirectory):
        raise ValueError('D22 media writing is paused until root completes the exact C subdirectory + D junction')
    return repo_path(logical)


def write_path(value):
    logical = logical_path(value)
    return local_output(logical) if logical.is_relative_to(LOGICAL) else repo_path(logical)


def same_logical_tree(value, ancestor):
    return logical_path(value).is_relative_to(logical_path(ancestor))
