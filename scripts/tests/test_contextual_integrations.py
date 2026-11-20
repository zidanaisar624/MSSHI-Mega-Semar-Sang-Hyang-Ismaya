"""Offline fixtures for pinned contextual sources and role ownership."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_context_sources as sources


class ContextSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='msshi-context-', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def cache(self, name, files):
        root = sources.folder(self.home, name)
        for rel, data in files.items():
            sources.atomic(root / rel, data)
        repo, pin = sources.PINNED[name]
        sources.atomic(root / 'MSSHI_SNAPSHOT.json', sources.encode({
            'repository': repo, 'commit': pin,
            'files': {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}))
        return root

    def test_exact_native_app_matrix(self):
        matrix = json.loads((ROOT / 'configs/bot_role_and_skill_matrix.json').read_text())
        policy = json.loads((ROOT / 'configs/muza_app_policy.json').read_text())['artcraft']
        for bot in matrix['bots']:
            actual = {s.removeprefix('artcraft-') for s in bot['optional_skills'] if s.startswith('artcraft-')}
            self.assertEqual(actual, set(policy[bot['id']]))
        self.assertEqual([len(policy[p]) for p in ('val', 'shikaku', 'kiki-chii')], [4, 2, 13])
        self.assertEqual(set(policy['shikaku']) & set(policy['kiki-chii']), {'figcraft'})

    def test_roles_pins_and_small_wrappers(self):
        matrix = json.loads((ROOT / 'configs/bot_role_and_skill_matrix.json').read_text())
        upstreams = {s['id']: s for s in json.loads((ROOT / 'configs/upstreams.json').read_text())['entries']}
        all_roles = {'yukino', 'shizuka', 'val', 'kiki-chii', 'shikaku'}
        for slug, source in [('career-ops','career-ops'), ('remote-jobs','remote-jobs'),
                              ('mattpocock-engineering','mattpocock-skills'), ('harness2','harness2'),
                              ('rea-video','rea-video'), ('grim-prompter','grim-prompter'),
                              ('claude-bughunter','claude-bughunter')]:
            expected = {'kiki-chii'} if slug == 'rea-video' else ({'shikaku'} if slug in {'grim-prompter', 'claude-bughunter'} else all_roles)
            owners = {b['id'] for b in matrix['bots'] if slug in b['required_skills']}
            self.assertEqual(owners, expected)
            self.assertEqual(set(upstreams[source]['roles']), expected)
            self.assertFalse(upstreams[source]['auto_start'])
            if source in sources.PINNED:
                self.assertEqual(upstreams[source]['revision'], sources.PINNED[source][1])
            wrapper = ROOT / 'skills' / slug
            self.assertLess(sum(p.stat().st_size for p in wrapper.rglob('*') if p.is_file()), 1024*1024)

    def test_default_status_never_fetches_or_executes(self):
        with patch.object(sources, 'fetch', side_effect=AssertionError('network')), \
             patch.object(sources.subprocess, 'run', side_effect=AssertionError('execute')):
            for name in sources.PINNED:
                status = sources.status(self.home, name)
                self.assertFalse(status['source_cached'])
                self.assertFalse(status['auto_start'])
                self.assertEqual(status['model_calls'], 0)
        self.assertFalse((self.home / 'skills').exists())

    def test_pinned_fetch_verifies_blob_and_keeps_source_outside_scanner(self):
        files = {'README.md': b'Workflow', 'LICENSE': b'MIT', 'AGENTS.md': b'Read selected mode',
                 'package.json': b'{"name":"career-ops","dependencies":{}}', '.agents/skills/career-ops/SKILL.md': b'workflow',
                 'modes/_shared.md': b'shared', 'modes/_writing.md': b'writing'}
        rows = [{'path': name, 'type': 'blob', 'mode': '100644', 'size': len(data),
                 'sha': hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()}
                for name, data in files.items()]
        pin = sources.PINNED['career-ops'][1]
        def fake(url, limit=sources.MAX_FILE):
            if '/git/trees/' in url:return json.dumps({'sha': pin, 'tree': rows, 'truncated': False}).encode()
            return files[url.split(pin+'/')[1]]
        with patch.object(sources, 'fetch', side_effect=fake):
            cached = sources.materialize(self.home, 'career-ops')
        self.assertTrue(cached.is_relative_to(self.home / 'msshi-private'))
        self.assertEqual(len(sources.verify_cached(self.home, 'career-ops')['files']), len(files))
        self.assertFalse((cached / 'package-lock.json').exists(), 'The reviewed CLI upstream does not supply a root lock')
        self.assertFalse((self.home / 'skills').exists())
        with patch.object(sources, 'fetch', side_effect=AssertionError('fetch on cache hit')):
            self.assertEqual(sources.materialize(self.home, 'career-ops'), cached)

    def test_unmarked_partial_cache_resumes_only_verified_git_blobs(self):
        name = 'remote-jobs'
        files = {'README.md': b'Workflow', 'LICENSE': b'ISC', 'src/companies/example.md': b'Python tools'}
        rows = [{'path': rel, 'type': 'blob', 'mode': '100644', 'size': len(data),
                 'sha': hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()}
                for rel, data in files.items()]
        root = sources.folder(self.home, name)
        sources.atomic(root / 'README.md', files['README.md'])
        sources.atomic(root / 'LICENSE', files['LICENSE'])
        pin = sources.PINNED[name][1]
        fetched=[]
        def fake(url, limit=sources.MAX_FILE):
            fetched.append(url)
            if '/git/trees/' in url:return json.dumps({'sha':pin,'tree':rows,'truncated':False}).encode()
            rel=url.split(pin+'/')[1]
            if rel != 'src/companies/example.md':raise AssertionError('Already verified blob was fetched again')
            return files[rel]
        with patch.object(sources,'fetch',side_effect=fake):
            self.assertEqual(sources.materialize(self.home,name),root)
        self.assertEqual(len(fetched),2)
        (root / 'README.md').write_bytes(b'user-modified')
        with patch.object(sources,'fetch',side_effect=AssertionError('Marked cache must not fetch around tampering')):
            with self.assertRaises(ValueError):sources.materialize(self.home,name)

    def test_unmarked_partial_cache_mismatch_is_preserved(self):
        name='remote-jobs';pin=sources.PINNED[name][1]
        files={'README.md':b'reviewed', 'LICENSE':b'ISC'}
        rows=[{'path':rel,'type':'blob','mode':'100644','size':len(data),
               'sha':hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()} for rel,data in files.items()]
        root=sources.folder(self.home,name);sources.atomic(root/'README.md',b'local-change')
        def fake(url,limit=sources.MAX_FILE):
            if '/git/trees/' in url:return json.dumps({'sha':pin,'tree':rows,'truncated':False}).encode()
            return files[url.split(pin+'/')[1]]
        with patch.object(sources,'fetch',side_effect=fake):
            with self.assertRaisesRegex(ValueError,'Partial cached source differs'):sources.materialize(self.home,name)
        self.assertEqual((root/'README.md').read_bytes(),b'local-change')
        self.assertFalse((root/'MSSHI_SNAPSHOT.json').exists())

    def test_personal_layers_and_heavy_paths_excluded(self):
        for path in ('cv.md', 'modes/_profile.md', 'modes/_custom.md', 'modes/_brief.md',
                     'data/private.json', 'employers/list.json', 'node_modules/pkg/index.js',
                     '.git/config', 'tests/test.mjs'):
            self.assertFalse(sources.selected_file('career-ops', {'path': path, 'type':'blob','mode':'100644'}), path)
        for path in ('AGENTS.md', 'modes/_shared.md', 'modes/_writing.md', '.agents/skills/career-ops/SKILL.md'):
            self.assertTrue(sources.selected_file('career-ops', {'path': path,'type':'blob','mode':'100644'}), path)

    def test_tampered_or_untrusted_cache_is_rejected(self):
        root = self.cache('remote-jobs', {'README.md':b'index'})
        (root / 'README.md').write_text('tampered')
        with self.assertRaises(ValueError):sources.verify_cached(self.home, 'remote-jobs')
        for path in ('../secret', '/secret', 'C:/secret', r'dir\secret', 'x//y'):
            with self.assertRaises(ValueError):sources.relative(path)
        marker = root/'MSSHI_SNAPSHOT.json'
        state=json.loads(marker.read_text());state['commit']='0'*40;marker.write_text(json.dumps(state))
        with self.assertRaises(ValueError):sources.verify_cached(self.home, 'remote-jobs')

    def test_matt_explicit_only_and_local_directory_queries(self):
        self.cache('mattpocock-skills', {
            'skills/tdd/SKILL.md':b'---\nname: tdd\n---\nTDD',
            'skills/to-spec/SKILL.md':b'---\ndisable-model-invocation: true\n---\nPublish only on request'})
        self.cache('remote-jobs', {'src/companies/example.md': b'---\nname: Example\n---\nPython remote tools'})
        with patch.object(sources, 'fetch', side_effect=AssertionError('network')):
            rows={r['name']:r for r in sources.skills(self.home, 'mattpocock-skills')}
            self.assertFalse(rows['tdd']['explicit_only']);self.assertTrue(rows['to-spec']['explicit_only'])
            result=sources.query_companies(self.home,'python')
            self.assertEqual(len(result['results']),1)
            self.assertFalse(result['results'][0]['active_job_verified'])

    def test_career_runtime_explicit_install_suppresses_lifecycle_and_browser(self):
        package={'name':'career-ops', 'dependencies':{'example':'^1.0.0'}}
        root=self.cache('career-ops', {'README.md':b'workflow', 'package.json':json.dumps(package).encode()})
        calls=[]
        def run(args, **kwargs):
            calls.append((args,kwargs))
            if args[-1]=='--version':return type('Result',(),{'stdout':'v24.0.0'})()
            if '--package-lock-only' in args:
                (root/'package-lock.json').write_text(json.dumps({'lockfileVersion':3,'packages':{'':package}}))
            if 'ci' in args:
                (root/'node_modules').mkdir()
                (root/'node_modules/.package-lock.json').write_text('{}')
            return type('Result',(),{'returncode':0})()
        with patch.object(sources.shutil,'which',side_effect=lambda name:name), \
             patch.object(sources,'materialize',return_value=root), \
             patch.object(sources.shutil,'disk_usage',return_value=type('Usage',(),{'free':2*1024**3})()), \
             patch.object(sources.subprocess,'run',side_effect=run):
            result=sources.install_runtime(self.home,'career-ops')
        lock_generation=next(row for row in calls if '--package-lock-only' in row[0])
        self.assertIn('--ignore-scripts',lock_generation[0])
        install=next(row for row in calls if 'ci' in row[0])
        self.assertIn('--ignore-scripts',install[0]);self.assertEqual(install[1]['env']['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'],'1')
        self.assertNotIn('OPENAI_API_KEY',install[1]['env'])
        marker=json.loads((self.home/'msshi-private/context-runtimes/career-ops/installed.json').read_text())
        self.assertFalse(marker['models_downloaded']);self.assertFalse(marker['browser_downloaded'])
        self.assertFalse(marker['operations_tested']);self.assertFalse(marker['auto_start'])
        self.assertFalse(marker['upstream_root_lockfile'])
        self.assertEqual(marker['dependency_lock_origin'],'generated-local-resolution')
        self.assertTrue(result['runtime_installed']);self.assertTrue(result['dependency_lock_verified'])
        (root/'package-lock.json').write_text('{}')
        self.assertFalse(sources.status(self.home,'career-ops')['runtime_installed'])


if __name__ == '__main__':unittest.main(verbosity=2)
