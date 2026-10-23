# Flare Combined Source

One AltStore-compatible app catalog for Flare Store, assembled from developer feeds and a selected community collection. See the live build report for current app and source counts.

## Add to Flare Store

In Flare Store's repository/source manager, add this source URL:

```text
https://masspimentel.github.io/flare-repo/repo.json
```

This endpoint becomes available after the first successful GitHub Pages deployment. It lists apps from the upstream feeds; it does not subscribe Flare Store to those feeds individually. IPA downloads and images use the original hosts. Your signing setup, app requirements, and any upstream access restrictions still apply.

The generated [source list](https://masspimentel.github.io/flare-repo/sources.json) contains the original repository URLs if you prefer to add them separately. The [build report](https://masspimentel.github.io/flare-repo/build-report.json) records each app's upstream source and the latest successful build time.

The catalog covers music and media, comics and reading, social clients, terminals and developer tools, wireless display, games, and emulation. Developer feeds take priority over the community collection when bundle identifiers overlap. Community listings can include modified apps; their publisher is recorded in the build report.

## Hosting on GitHub Pages

1. Put these project files in a public GitHub repository, including `.github/workflows/publish.yml`.
2. Set the default branch to `main`.
3. Under **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source.
4. Open **Actions → Publish source → Run workflow** and select `main`.
5. Wait for both `build` and `deploy` to succeed. Add the `/repo.json` address above to Flare Store.

For a fork or another repository name, substitute your account and repository in these example addresses. The JSON feed itself does not depend on this account name; you may also choose your own unique feed identifier in `build.py` before distributing it.

The workflow runs on pushes to `main`, manual requests, and every six hours at minute 17 UTC. GitHub schedules may be delayed, and inactive public repositories may have schedules disabled; check the Actions tab if builds stop. A failed build skips deployment, preserving the previous Pages catalog. Your computer does not need to stay on.

## Build locally

Requires Python 3.12 or newer; no packages to install.

```sh
python -m unittest discover -s tests -v
python build.py
```

The builder creates `public/repo.json`, `public/sources.json`, and `public/build-report.json`. These generated files are ignored by Git; GitHub Actions builds them again before publishing.

Paths default to this project directory, so `python /path/to/build.py` also works from another working directory. Optional `--sources PATH` and `--output PATH` override the locations.

To reproduce a build using saved feeds, put each feed in a directory under its configured ID (for example, `dolphinios.json`), then run:

```sh
python build.py --snapshots /path/to/saved-feeds
```

## Change the source list

Edit `sources.json`. Each entry needs a unique lowercase ID, a display name, and a public HTTPS JSON URL:

```json
{
  "id": "example",
  "name": "Example developer source",
  "url": "https://example.org/apps.json"
}
```

Order expresses preference: when app bundle identifiers clash, the first source wins. The builder keeps that source's full app record; it does not mix releases from different publishers. The report lists suppressed duplicates.

Modern version arrays and legacy flat version fields are supported. Version order, app permissions, OS requirements, and access restriction metadata are retained. Minor date formatting inconsistencies are normalized. Missing permissions are not invented. One combined source cannot represent conflicting source-level Patreon contexts; such a build fails with an explanation.

If any source is unavailable or malformed, the build fails instead of publishing an incomplete app list. If an upstream source goes away permanently, remove it from `sources.json` and rerun the workflow.

## Limits

- Upstream listings can lag behind a project's latest release.
- A listed app may require a different iOS version, JIT, special entitlements, or another installation method. Inclusion does not guarantee it will install or run through Flare Store.
- The builder validates catalog metadata. It does not download, scan, sign, or audit IPA files, and it does not bypass upstream access requirements.
- Upstream news is omitted. There is no web interface, database, or source discovery service.

New project code is MIT licensed. Third-party app names, descriptions, images, and other upstream metadata retain their respective ownership and terms.
