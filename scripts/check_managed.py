"""Exercise managed ownership, alias consistency and customization safety."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'scripts'))
import msshi_managed as managed_api
from msshi_managed import digest, register, refresh
from msshi_update import inventory


def link(path, target):
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(path), str(target)],
                       check=True, capture_output=True)
    else:
        path.symlink_to(target, target_is_directory=True)


def unlink(path):
    if os.name == 'nt':
        os.rmdir(path)
    else:
        path.unlink()


def fixture(root, slugs=('one',)):
    source = root / 'source'
    target = root / 'shared' / 'skills' / 'one'
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text('# old\n')
    for slug in slugs:
        skill = source / 'skills' / slug
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('# old\n')
    (source / 'VERSION.json').write_text('{"version":"3.0.0"}')
    home = root / 'data'
    home.mkdir()
    return source, target, home


passed = []
with TemporaryDirectory(prefix='msshi-managed-shared-') as temp:
    root = Path(temp)
    source, target, home = fixture(root)
    a, b = root / 'a' / 'skills', root / 'b' / 'skills'
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    junctions = [a / 'one', b / 'one']
    for logical in junctions:
        link(logical, target)
    try:
        result = register(home, source, [a, b], apply=True)
        assert len(result['additions']) == 2
        incoming = source / 'skills' / 'one' / 'SKILL.md'
        incoming.write_text('# new\n')
        with patch.object(managed_api, 'update_skill', wraps=managed_api.update_skill) as update:
            result = refresh(home, source, True)
            assert update.call_count == 1
        assert result['physical_targets'] == 1 and result['results'][0]['status'] == 'updated'
        assert (target / 'SKILL.md').read_text() == '# new\n'
        assert Path(result['results'][0]['backup'], 'one', 'SKILL.md').read_text() == '# old\n'
        assert refresh(home, source, True)['results'][0]['status'] == 'current'
        (target / 'SKILL.md').write_text('# user custom\n')
        assert refresh(home, source, True)['results'][0]['status'] == 'custom_preserved'
        unlink(a / 'one')
        other = root / 'other'
        other.mkdir()
        (other / 'SKILL.md').write_text('# unrelated\n')
        link(a / 'one', other)
        assert any(row['status'] == 'blocked' for row in refresh(home, source, True)['results'])
        assert (other / 'SKILL.md').read_text() == '# unrelated\n'
        passed.extend(['shared physical target updated once', 'rollback backup exact',
                       'repeat idempotent', 'custom edits preserved', 'retargeted junction blocked'])
    finally:
        for logical in junctions:
            unlink(logical)

with TemporaryDirectory(prefix='msshi-managed-alias-') as temp:
    root = Path(temp)
    source, target, home = fixture(root, ('one', 'alias'))
    logical_root = root / 'bot' / 'skills'
    logical_root.mkdir(parents=True)
    junctions = [logical_root / slug for slug in ('one', 'alias')]
    for logical in junctions:
        link(logical, target)
    try:
        assert len(register(home, source, [logical_root], apply=True)['additions']) == 2
        for slug in ('one', 'alias'):
            (source / 'skills' / slug / 'SKILL.md').write_text('# alias new\n')
        with patch.object(managed_api, 'update_skill', wraps=managed_api.update_skill) as update:
            result = refresh(home, source, True, names={'one'})
            assert update.call_count == 1
        row = result['results'][0]
        assert result['physical_targets'] == 1 and row['aliases'] == ['alias', 'one']
        assert row['logical_references'] == 2 and row['status'] == 'updated'
        state = json.loads((home / 'state.json').read_text())
        assert all(binding['fingerprint'] == digest(inventory(target)) for binding in state['managed_bindings'])
        assert refresh(home, source, True)['results'][0]['status'] == 'current'
        passed.append('two different aliases update one physical target once and checkpoint both')
        (source / 'skills' / 'one' / 'SKILL.md').write_text('# divergent one\n')
        (source / 'skills' / 'alias' / 'SKILL.md').write_text('# divergent alias\n')
        before_target, before_state = inventory(target), (home / 'state.json').read_bytes()
        with patch.object(managed_api, 'update_skill', wraps=managed_api.update_skill) as update:
            result = refresh(home, source, True, names={'one'})
            assert update.call_count == 0
        assert result['results'][0]['status'] == 'blocked'
        assert result['results'][0]['reason'] == 'ambiguous_alias_upstream'
        assert inventory(target) == before_target and (home / 'state.json').read_bytes() == before_state
        passed.append('divergent incoming aliases blocked without skill or state writes')
    finally:
        for logical in junctions:
            unlink(logical)

with TemporaryDirectory(prefix='msshi-managed-ordinary-') as temp:
    root = Path(temp)
    source, target, home = fixture(root)
    ordinary = {str(target.parent): {'one': digest(inventory(target))}}
    (home / 'state.json').write_text(json.dumps({'schema_version': 1, 'targets': ordinary}))
    result = register(home, source, [target.parent], apply=True)
    assert result['additions'] == []
    assert result['skipped'][0]['reason'] == 'ordinary_updater_owned'
    passed.append('ordinary updater ownership not enrolled a second time')
    # Historical duplicate: ordinary updater already applied a release, leaving
    # the managed binding's old fingerprint behind.
    old = digest(inventory(target))
    state = {'schema_version': 1, 'targets': ordinary, 'managed_bindings': [{
        'skill': 'one', 'logical': str(target), 'physical': str(target),
        'fingerprint': old, 'baseline_version': '3.0.0'}]}
    (source / 'skills' / 'one' / 'SKILL.md').write_text('# ordinary new\n')
    (target / 'SKILL.md').write_text('# ordinary new\n')
    state['targets'][str(target.parent)]['one'] = digest(inventory(target))
    (home / 'state.json').write_text(json.dumps(state))
    before = inventory(target)
    with patch.object(managed_api, 'update_skill', wraps=managed_api.update_skill) as update:
        result = refresh(home, source, True)
        assert update.call_count == 0
    assert result['results'][0]['status'] == 'ordinary_updater_owned'
    assert result['ordinary_ownership_transfers'] and result['bindings'] == 0
    assert inventory(target) == before
    after = (home / 'state.json').read_bytes()
    assert json.loads(after)['managed_bindings'] == []
    assert refresh(home, source, True)['results'] == []
    assert (home / 'state.json').read_bytes() == after
    passed.append('historical duplicate ownership transferred as metadata only, idempotently')

print(json.dumps({'passed': passed, 'fixture_groups': 3, 'live_state_modified': False}))
