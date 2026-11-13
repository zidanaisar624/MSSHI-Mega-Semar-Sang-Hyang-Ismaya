"""Exercise managed ownership, alias consistency and customization safety."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'scripts'))
import msshi_managed as managed_api
import msshi_optional as optional_api
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

def optional_fixture(root):
    source, target, home = fixture(root)
    wrapper = source / 'optional' / 'rea'
    wrapper.mkdir(parents=True)
    (wrapper / 'SKILL.md').write_text('# optional REA wrapper\n')
    (source / 'optional' / 'manifest.json').write_text(json.dumps({
        'schema_version': 1,
        'entries': [{'id': 'rea', 'path': 'optional/rea', 'public_default': False, 'roles': ['shikaku']}],
    }))
    (source / 'scripts').mkdir()
    (source / 'scripts' / 'msshi_rea.py').write_text('# fixture only, must never execute\n')
    return source, target, home, wrapper


with TemporaryDirectory(prefix='msshi-optional-off-') as temp:
    source, target, home, wrapper = optional_fixture(Path(temp))
    shutil.copytree(wrapper, target.parent / 'rea')
    result = register(home, source, [target.parent], apply=True)
    assert [binding['skill'] for binding in result['additions']] == ['one']
    assert all('source_rel' not in binding for binding in result['additions'])
    before = inventory(target.parent / 'rea')
    (wrapper / 'SKILL.md').write_text('# changed but not opted in\n')
    refresh(home, source, apply=True)
    assert inventory(target.parent / 'rea') == before
    assert not (source / 'skills' / 'rea').exists()
    passed.append('optional defaults OFF: ordinary register and refresh never adopt REA')
    old_manifest = (source / 'optional' / 'manifest.json').read_text()
    for invalid in ('../rea', 'skills/rea', 'optional/other', '/optional/rea', 'optional\\rea'):
        manifest = json.loads(old_manifest)
        manifest['entries'][0]['path'] = invalid
        (source / 'optional' / 'manifest.json').write_text(json.dumps(manifest))
        try:
            optional_api.optional_sources(source)
            raise AssertionError('invalid optional source accepted')
        except ValueError:
            pass
    (source / 'optional' / 'manifest.json').write_text(old_manifest)
    passed.append('manifest path allowlist rejects traversal and undeclared directories')

with TemporaryDirectory(prefix='msshi-optional-enable-') as temp:
    root = Path(temp)
    source, target, home, wrapper = optional_fixture(root)
    with patch.object(optional_api.subprocess, 'run') as runtime:
        result = optional_api.enable('rea', target.parent, source=source, home=home)
        assert result['status'] == 'enabled' and result['registered']
        runtime.assert_not_called()
    state = json.loads((home / 'state.json').read_text())
    assert [row['skill'] for row in state['managed_bindings']] == ['rea']
    binding = state['managed_bindings'][0]
    assert binding['source_rel'] == 'optional/rea' and binding['optional'] is True
    (wrapper / 'SKILL.md').write_text('# new optional wrapper\n')
    result = refresh(home, source, apply=True)
    assert result['results'][0]['status'] == 'updated'
    assert inventory(target.parent / 'rea') == inventory(wrapper)
    passed.append('explicit enable copies and enrolls REA only, then refresh updates registered wrapper')
    (target.parent / 'rea' / 'SKILL.md').write_text('# user optional edits\n')
    assert refresh(home, source, apply=True)['results'][0]['status'] == 'custom_preserved'
    assert (target.parent / 'rea' / 'SKILL.md').read_text() == '# user optional edits\n'
    passed.append('registered optional customization preserved by updater')
    # Every state source is validated, even when refresh selects a different name.
    original = (home / 'state.json').read_bytes()
    for invalid, optional in (('../optional/rea', True), ('optional/unknown', True),
                              ('skills/one', False), ('optional/rea', False),
                              (str(wrapper), True), ('optional\\rea', True)):
        state = json.loads(original)
        state['managed_bindings'][0].update(source_rel=invalid, optional=optional)
        (home / 'state.json').write_text(json.dumps(state))
        before_state, before_skill = (home / 'state.json').read_bytes(), inventory(target.parent / 'rea')
        try:
            refresh(home, source, apply=True, names={'one'})
            raise AssertionError('unapproved managed source accepted')
        except ValueError:
            pass
        assert (home / 'state.json').read_bytes() == before_state
        assert inventory(target.parent / 'rea') == before_skill
    (home / 'state.json').write_bytes(original)
    passed.append('invalid optional state source, traversal and retargeting rejected without writes')

with TemporaryDirectory(prefix='msshi-optional-existing-') as temp:
    root = Path(temp)
    source, target, home, wrapper = optional_fixture(root)
    shutil.copytree(wrapper, target.parent / 'rea')
    with patch.object(optional_api.subprocess, 'run') as runtime:
        result = optional_api.enable('rea', target.parent, source=source, home=home)
        assert result['status'] == 'already_present' and result['registered']
        runtime.assert_not_called()
        result = optional_api.enable('rea', target.parent, source=source, home=home,
                                     install_runtime=True, hermes_home=root / 'hermes')
        runtime.assert_called_once()
        command = runtime.call_args.args[0]
        assert command[-3:] == ['--hermes-home', str(root / 'hermes'), 'install']
        assert command[-4] == str(source / 'scripts' / 'msshi_rea.py')
        assert result['runtime_installed'] is True
    passed.append('source-only exact wrapper enrolled; runtime runs solely with explicit flag')
    other = root / 'custom' / 'skills'
    (other / 'rea').mkdir(parents=True)
    (other / 'rea' / 'SKILL.md').write_text('# custom existing REA\n')
    before = (home / 'state.json').read_bytes()
    with patch.object(optional_api.subprocess, 'run') as runtime:
        result = optional_api.enable('rea', other, source=source, home=home, install_runtime=True)
        runtime.assert_not_called()
    assert result['status'] == 'custom_preserved' and not result['registered']
    assert (other / 'rea' / 'SKILL.md').read_text() == '# custom existing REA\n'
    assert (home / 'state.json').read_bytes() == before
    passed.append('existing custom optional skill preserved and never enrolled or given a runtime')
    explicit_home = root / 'explicit-data'
    result = register(explicit_home, source, [target.parent], apply=True, include_optional=('rea',))
    assert {row['skill'] for row in result['additions']} == {'one', 'rea'}
    passed.append('register --include-optional explicitly enrolls exact optional copies')

with TemporaryDirectory(prefix='msshi-optional-setup-') as temp:
    root = Path(temp)
    source, target, home, wrapper = optional_fixture(root)
    selected = {root / 'team' / name / 'skills': [] for name in ('val', 'shikaku', 'custom-coder')}
    assert optional_api.setup_targets('solo', {target.parent: []}, source=source) == [target.parent]
    assert optional_api.setup_targets('muza-preset', selected, source=source) == [root / 'team' / 'shikaku' / 'skills']
    with patch.object(optional_api.sys.stdin, 'isatty', return_value=False), \
            patch.object(optional_api.sys, 'stdout', io.StringIO()):
        assert optional_api.setup_targets('custom-bots', selected, source=source) == []
    import msshi_cli
    with patch.object(optional_api.sys.stdin, 'isatty', return_value=True), \
            patch.object(msshi_cli, 'checklist', return_value=['custom-coder']):
        assert optional_api.setup_targets('custom-bots', selected, source=source) == [root / 'team' / 'custom-coder' / 'skills']
    passed.append('wizard REA targets only solo selection, preset Coder or explicit custom bot choice')

with TemporaryDirectory(prefix='msshi-optional-cli-') as temp:
    root = Path(temp)
    env = {**os.environ, 'MSSHI_HOME': str(root / 'data'), 'HERMES_HOME': str(root / 'hermes')}
    command = [sys.executable, '-B', '-X', 'utf8', str(repo / 'scripts' / 'msshi_cli.py')]
    listed = subprocess.run([*command, 'optional', 'list'], env=env, check=True, capture_output=True, text=True)
    options = json.loads(listed.stdout)['optional_skills']
    assert len(options) == 1
    assert {key: options[0][key] for key in ('id', 'path', 'public_default')} == {
        'id': 'rea', 'path': 'optional/rea', 'public_default': False}
    assert options[0]['description'] and options[0]['runtime']
    assert not (root / 'data').exists() and not (root / 'hermes').exists()
    enabled = subprocess.run([*command, 'optional', 'enable', 'rea', '--target-dir', str(root / 'skills')],
                             env=env, check=True, capture_output=True, text=True)
    assert json.loads(enabled.stdout)['registered'] is True
    assert not (root / 'hermes').exists()
    state = json.loads((root / 'data' / 'state.json').read_text())
    assert state['targets'] == {} and len(state['managed_bindings']) == 1
    assert state['managed_bindings'][0]['source_rel'] == 'optional/rea'
    passed.append('CLI optional list is read-only and explicit enable enrolls without runtime or profiles')

print(json.dumps({'passed': passed, 'fixture_groups': 8, 'live_state_modified': False}))
