import copy
import importlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError


def modern_app():
    return {
        'name': 'Example', 'bundleIdentifier': 'org.example.App',
        'developerName': 'Example Developer', 'localizedDescription': 'An example app.',
        'iconURL': 'https://example.org/icon.png',
        'appPermissions': {'entitlements': ['test.permission'], 'privacy': {}},
        'versions': [
            {'version': 'Preview 2', 'date': '2026-10-22', 'size': 120,
             'downloadURL': 'https://example.org/new.ipa', 'minOSVersion': '17.0'},
            {'version': '1.0', 'date': '2025-01-01', 'size': 100,
             'downloadURL': 'https://example.org/old.ipa'},
        ],
    }


def source(slug='first'):
    return {'id': slug, 'name': slug.title(), 'url': f'https://{slug}.example.org/repo.json'}


class CatalogTests(unittest.TestCase):
    def builder(self):
        self.assertIsNotNone(importlib.util.find_spec('build'), 'Catalog builder is not implemented yet')
        return importlib.import_module('build')

    def test_preserves_versions_permissions_case_and_input(self):
        app = modern_app()
        original = copy.deepcopy(app)
        result = self.builder().normalize_app(app)
        self.assertEqual(result['versions'], original['versions'])
        self.assertEqual(result['appPermissions'], original['appPermissions'])
        self.assertEqual(result['bundleIdentifier'], 'org.example.App')
        self.assertEqual(result['version'], 'Preview 2')
        self.assertEqual(result['minOSVersion'], '17.0')
        self.assertEqual(result['downloadURL'], 'https://example.org/new.ipa')
        self.assertEqual(app, original)

    def test_converts_legacy_versions_and_screenshots_without_inventing_permissions(self):
        app = modern_app()
        app.pop('versions')
        app.pop('appPermissions')
        app.update(version='Build 813', versionDate='2026-08-22T06:12:33+00:00',
                   size=120, downloadURL='https://example.org/813.ipa',
                   screenshotURLs=['https://example.org/screen.png'])
        result = self.builder().normalize_app(app)
        self.assertEqual(result['versions'], [{'version': 'Build 813',
                         'date': '2026-08-22T06:12:33+00:00', 'size': 120,
                         'downloadURL': 'https://example.org/813.ipa'}])
        self.assertEqual(result['screenshots'], ['https://example.org/screen.png'])
        self.assertNotIn('appPermissions', result)

    def test_accepts_nonpadded_iso_dates_from_live_feed(self):
        app = modern_app()
        app['versions'][0]['date'] = '2024-9-07T18:30:00Z'
        result = self.builder().normalize_app(app)
        self.assertEqual(result['versions'][0]['date'], '2024-09-07T18:30:00Z')
        self.assertEqual(result['versionDate'], '2024-09-07T18:30:00Z')
        self.assertEqual(app['versions'][0]['date'], '2024-9-07T18:30:00Z')

    def test_accepts_nonpadded_timezone_offsets_from_live_feed(self):
        app = modern_app()
        app['versions'][0]['date'] = '2023-07-27T06:00:00-5:00'
        result = self.builder().normalize_app(app)
        self.assertEqual(result['versions'][0]['date'], '2023-07-27T06:00:00-05:00')

    def test_preserves_legacy_os_bounds_missing_from_latest_version(self):
        app = modern_app()
        app['minOSVersion'] = '16.0'
        app['maxOSVersion'] = '26.0'
        result = self.builder().normalize_app(app)
        self.assertEqual(result['versions'][0]['minOSVersion'], '17.0')
        self.assertEqual(result['versions'][0]['maxOSVersion'], '26.0')
        self.assertEqual(result['maxOSVersion'], '26.0')

    def test_rejects_nonstring_source_ids(self):
        builder = self.builder()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'sources.json'
            config.write_text(json.dumps([dict(source(), id=123)]), encoding='utf-8')
            with patch.object(builder, 'fetch_json', return_value={'apps': [modern_app()]}):
                with self.assertRaises(ValueError):
                    builder.build(config, root / 'public')

    def test_first_source_wins_duplicate_without_mixing_versions(self):
        first, second = modern_app(), modern_app()
        second['name'] = 'Other Publisher'
        second['versions'][0]['downloadURL'] = 'https://other.example.org/new.ipa'
        catalog, report = self.builder().merge_sources(
            [source(), source('second')], [{'apps': [first]}, {'apps': [second]}])
        self.assertEqual(len(catalog['apps']), 1)
        self.assertEqual(catalog['apps'][0]['name'], 'Example')
        self.assertEqual(catalog['apps'][0]['downloadURL'], 'https://example.org/new.ipa')
        self.assertEqual(report['duplicates'][0]['bundleIdentifier'], 'org.example.App')
        self.assertEqual(report['apps'][0]['sourceURL'], 'https://first.example.org/repo.json')

    def test_preserves_paid_access_context(self):
        app = modern_app()
        app['patreon'] = {'tiers': ['123']}
        catalog, _ = self.builder().merge_sources([source()], [
            {'apps': [app], 'patreonURL': 'https://www.patreon.com/example'}])
        self.assertEqual(catalog['patreonURL'], 'https://www.patreon.com/example')
        self.assertEqual(catalog['apps'][0]['patreon'], {'tiers': ['123']})

    def test_rejects_conflicting_paid_context(self):
        first, second = modern_app(), modern_app()
        second['bundleIdentifier'] = 'org.example.Other'
        first['patreon'] = second['patreon'] = {'pledge': 1}
        with self.assertRaisesRegex(ValueError, 'Patreon'):
            self.builder().merge_sources([source(), source('second')], [
                {'apps': [first], 'patreonURL': 'https://www.patreon.com/first'},
                {'apps': [second], 'patreonURL': 'https://www.patreon.com/second'}])

    def test_rejects_malformed_app_data(self):
        builder = self.builder()
        for key, value in [('name', ''), ('bundleIdentifier', None), ('versions', [])]:
            with self.subTest(key=key):
                app = modern_app()
                app[key] = value
                with self.assertRaises(ValueError):
                    builder.normalize_app(app)
        for key, value in [('date', 'yesterday'), ('size', True), ('size', -1),
                           ('downloadURL', 'http://example.org/app.ipa'),
                           ('downloadURL', 'https://user:password@example.org/app.ipa')]:
            with self.subTest(key=key, value=value):
                app = modern_app()
                app['versions'][0][key] = value
                with self.assertRaises(ValueError):
                    builder.normalize_app(app)

    def test_rejects_empty_or_nonobject_feeds(self):
        builder = self.builder()
        for feed in [[], {}, {'apps': []}, {'apps': 'invalid'}]:
            with self.subTest(feed=feed), self.assertRaises(ValueError):
                builder.merge_sources([source()], [feed])

    def test_ignores_unused_patreon_context(self):
        second = modern_app()
        second['bundleIdentifier'] = 'org.example.Second'
        catalog, _ = self.builder().merge_sources([source(), source('second')], [
            {'apps': [modern_app()], 'patreonURL': 'https://www.patreon.com/first'},
            {'apps': [second], 'patreonURL': 'https://www.patreon.com/second'}])
        self.assertNotIn('patreonURL', catalog)

    def test_failed_fetch_keeps_existing_output(self):
        builder = self.builder()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'sources.json'
            config.write_text(json.dumps([source()]), encoding='utf-8')
            output = root / 'public'
            output.mkdir()
            for name in ['repo.json', 'sources.json', 'build-report.json']:
                (output / name).write_text('previous output', encoding='utf-8')
            with patch.object(builder, 'fetch_json', side_effect=URLError('unavailable')):
                with self.assertRaises(ValueError):
                    builder.build(config, output)
            self.assertTrue(all(file.read_text() == 'previous output' for file in output.iterdir()))

    def test_builds_from_snapshots_and_cli_works_outside_repo(self):
        builder = self.builder()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'sources.json'
            config.write_text(json.dumps([source()]), encoding='utf-8')
            snapshots = root / 'snapshots'
            snapshots.mkdir()
            (snapshots / 'first.json').write_text(json.dumps({'apps': [modern_app()]}), encoding='utf-8')
            command = [sys.executable, builder.__file__, '--sources', str(config),
                       '--output', str(root / 'public'), '--snapshots', str(snapshots)]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            catalog = json.loads((root / 'public' / 'repo.json').read_text(encoding='utf-8'))
            self.assertEqual(len(catalog['apps']), 1)
            self.assertEqual(catalog['apps'][0]['name'], 'Example')

    def test_rejects_unsafe_source_configuration(self):
        builder = self.builder()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for entry in [source('../outside'), dict(source(), url='http://example.org/repo.json')]:
                with self.subTest(entry=entry):
                    config = root / 'sources.json'
                    config.write_text(json.dumps([entry]), encoding='utf-8')
                    with self.assertRaises(ValueError):
                        builder.build(config, root / 'public')

    def test_rejects_insecure_redirects(self):
        handler = self.builder().HTTPSRedirectHandler()
        with self.assertRaises(ValueError):
            handler.redirect_request(None, None, 302, 'Moved', {}, 'http://example.org/repo.json')

    def test_rejects_oversized_response(self):
        builder = self.builder()
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, limit):
                return b'x' * limit
        with patch.object(builder, 'MAX_BYTES', 10), patch.object(builder, 'OPENER') as opener:
            opener.open.return_value = Response()
            with self.assertRaisesRegex(ValueError, 'large'):
                builder.fetch_json('https://example.org/repo.json')


if __name__ == '__main__':
    unittest.main()
