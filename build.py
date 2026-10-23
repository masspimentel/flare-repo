"""Build a static Flare Store source without downloading app binaries."""

import argparse
import copy
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 8 * 1024 * 1024
VERSION_FIELDS = {
    'version': 'version', 'versionDate': 'date', 'versionDescription': 'localizedDescription',
    'downloadURL': 'downloadURL', 'size': 'size', 'buildVersion': 'buildVersion',
    'minOSVersion': 'minOSVersion', 'maxOSVersion': 'maxOSVersion',
}


def https_url(value):
    if not isinstance(value, str) or any(char.isspace() for char in value):
        raise ValueError('Expected an HTTPS URL without whitespace')
    parts = urlsplit(value)
    if parts.scheme != 'https' or not parts.hostname or parts.username is not None or parts.password is not None:
        raise ValueError('Expected an HTTPS URL without embedded credentials')
    _ = parts.port
    return value


class HTTPSRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        https_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = build_opener(HTTPSRedirectHandler())


def fetch_json(url):
    request = Request(https_url(url), headers={
        'Accept': 'application/json', 'User-Agent': 'FlareCombinedSource/1.0',
    })
    with OPENER.open(request, timeout=30) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Feed is too large (maximum 8 MiB)')
    return json.loads(raw.decode('utf-8-sig'))


def normalize_app(app):
    if not isinstance(app, dict):
        raise ValueError('Each app must be an object')
    app = copy.deepcopy(app)
    for key in ['name', 'bundleIdentifier', 'developerName', 'localizedDescription', 'iconURL']:
        if not isinstance(app.get(key), str) or not app[key].strip():
            raise ValueError(f'App has missing or invalid {key}')
    https_url(app['iconURL'])
    if 'versions' not in app:
        app['versions'] = [{modern: app[legacy] for legacy, modern in VERSION_FIELDS.items() if legacy in app}]
    versions = app['versions']
    if not isinstance(versions, list) or not versions:
        raise ValueError(f"{app['name']}: versions must be a nonempty array")
    if isinstance(versions[0], dict):
        for key in ['minOSVersion', 'maxOSVersion']:
            if key in app:
                versions[0].setdefault(key, app[key])
    for version in versions:
        if not isinstance(version, dict):
            raise ValueError('Each version must be an object')
        for key in ['version', 'date']:
            if not isinstance(version.get(key), str) or not version[key].strip():
                raise ValueError(f"{app['name']}: version has missing or invalid {key}")
        # Some published sources omit leading zeroes in the month or day.
        version['date'] = re.sub(
            r'^(\d{4})-(\d{1,2})-(\d{1,2})(?=T|$)',
            lambda match: f'{match[1]}-{int(match[2]):02d}-{int(match[3]):02d}',
            version['date'],
        )
        version['date'] = re.sub(r'([+-])(\d):(\d{2})$', r'\g<1>0\2:\3', version['date'])
        datetime.fromisoformat(version['date'].replace('Z', '+00:00'))
        if type(version.get('size')) is not int or version['size'] <= 0:
            raise ValueError(f"{app['name']}: version size must be a positive integer")
        https_url(version.get('downloadURL'))
    for legacy, modern in VERSION_FIELDS.items():
        if modern in versions[0]:
            app[legacy] = versions[0][modern]
        else:
            app.pop(legacy, None)
    if 'screenshots' not in app and 'screenshotURLs' in app:
        app['screenshots'] = copy.deepcopy(app['screenshotURLs'])
    return app


def merge_sources(sources, feeds):
    if not sources or len(sources) != len(feeds):
        raise ValueError('Every source must have a feed')
    catalog = {
        'name': 'Flare Combined Source',
        'identifier': 'io.github.masspimentel.flare-repo',
        'subtitle': 'Developer feeds in one source',
        'description': 'Combined developer app listings. Downloads remain on the original hosts.',
        'apps': [], 'news': [],
    }
    report = {'generatedAt': datetime.now(timezone.utc).isoformat(), 'sources': [], 'apps': [], 'duplicates': []}
    seen = set()
    patreon_urls = set()
    for source, feed in zip(sources, feeds):
        if not isinstance(feed, dict) or not isinstance(feed.get('apps'), list) or not feed['apps']:
            raise ValueError(f"{source['name']}: expected a nonempty apps array")
        report['sources'].append(dict(source, appCount=len(feed['apps'])))
        if feed.get('nsfw'):
            catalog['nsfw'] = True
        for raw_app in feed['apps']:
            app = normalize_app(raw_app)
            bundle = app['bundleIdentifier']
            if bundle in seen:
                report['duplicates'].append({'bundleIdentifier': bundle, 'ignoredSourceURL': source['url']})
                continue
            if 'patreon' in app:
                if not isinstance(app['patreon'], dict):
                    raise ValueError(f"{app['name']}: invalid Patreon restriction metadata")
                patreon_urls.add(https_url(feed.get('patreonURL')))
            seen.add(bundle)
            catalog['apps'].append(app)
            report['apps'].append({'bundleIdentifier': bundle, 'name': app['name'], 'sourceURL': source['url']})
    if len(patreon_urls) > 1:
        raise ValueError('Patreon source contexts conflict; keep restricted apps in separate sources')
    if patreon_urls:
        catalog['patreonURL'] = patreon_urls.pop()
    report['appCount'] = len(catalog['apps'])
    report['sourceCount'] = len(sources)
    return catalog, report


def build(sources_path, output_dir, snapshots=None):
    sources = json.loads(Path(sources_path).read_text(encoding='utf-8-sig'))
    if not isinstance(sources, list) or not sources:
        raise ValueError('sources.json must be a nonempty array')
    ids, urls = set(), set()
    for source in sources:
        if (not isinstance(source, dict) or not isinstance(source.get('id'), str)
                or not re.fullmatch(r'[a-z0-9-]+', source['id'])):
            raise ValueError('Every source needs a lowercase alphanumeric id with optional hyphens')
        if not isinstance(source.get('name'), str) or not source['name'].strip():
            raise ValueError('Every source needs a name')
        url = https_url(source.get('url'))
        if source['id'] in ids or url in urls:
            raise ValueError('Source ids and URLs must be unique')
        ids.add(source['id'])
        urls.add(url)
    feeds = []
    # shortcut: one unavailable feed blocks refresh; add per-source caching if outages become frequent.
    for source in sources:
        try:
            if snapshots is None:
                feeds.append(fetch_json(source['url']))
            else:
                path = Path(snapshots) / (source['id'] + '.json')
                if path.stat().st_size > MAX_BYTES:
                    raise ValueError('Snapshot is too large')
                feeds.append(json.loads(path.read_text(encoding='utf-8-sig')))
        except (OSError, ValueError, URLError) as exc:
            raise ValueError(f"Cannot read source {source['name']}: {exc}") from exc
    catalog, report = merge_sources(sources, feeds)
    documents = {'repo.json': catalog, 'sources.json': sources, 'build-report.json': report}
    encoded = {name: json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
               for name, value in documents.items()}
    output_dir = Path(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.flare-build-', dir=output_dir.parent) as temp:
        for name, value in encoded.items():
            (Path(temp) / name).write_text(value, encoding='utf-8')
        output_dir.mkdir(exist_ok=True)
        for name in encoded:
            (Path(temp) / name).replace(output_dir / name)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=ROOT / 'sources.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'public')
    parser.add_argument('--snapshots', type=Path, help='Use ID.json files in this directory instead of the network')
    args = parser.parse_args()
    try:
        report = build(args.sources, args.output, args.snapshots)
    except (OSError, ValueError) as exc:
        print(f'Build failed: {exc}', file=sys.stderr)
        return 1
    print(f"Built {report['appCount']} apps from {report['sourceCount']} sources into {args.output.resolve()}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
