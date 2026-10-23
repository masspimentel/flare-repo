# Flare Combined Source

A community-maintained app catalog for Flare Store. Add one source to browse music and media apps, readers, social clients, utilities, games, and emulators from a collection of developer and community feeds.

## Add the source

1. Open Flare Store and go to its repository/source manager.
2. Add the URL below and let the app load the catalog.
3. Browse the listings, choose an app, and use your usual Flare Store signing and installation setup.

```text
https://masspimentel.github.io/flare-repo/repo.json
```

[Open the source JSON](https://masspimentel.github.io/flare-repo/repo.json)

Already added it? Refresh **Flare Combined Source** in Flare Store to pick up new listings. You can keep using the same URL as the collection grows.

## What you can find

| Category | Examples |
| --- | --- |
| Music and video | Spotube, ByeTunes, Yattee |
| Comics and reading | Aidoku, Paperback, Venera |
| Social | Winston for Reddit, Apollo, Sable |
| Utilities and tools | iSH, gTerm, OpenAirDisplay |
| Games and emulation | Delta, PPSSPP, PokeMMO, Pocket8 |

These are examples; listings and available versions can change. The [current source list](https://masspimentel.github.io/flare-repo/sources.json) shows the feeds included in the catalog.

## Updates

The catalog is scheduled to refresh every six hours. Refresh the source in Flare Store to see the latest published listings. Installing an app update still uses your normal Flare Store process.

An app's listing follows its original source, which may update later than the project's website or GitHub releases. If a catalog refresh fails, the previous working catalog stays available.

You can check the [last successful refresh](https://masspimentel.github.io/flare-repo/build-report.json) or [publishing status](https://github.com/masspimentel/flare-repo/actions/workflows/publish.yml).

## Before installing

- Use your own working Flare Store signing setup. This source does not provide a signing certificate.
- Check the app's iOS and device requirements. Some apps need JIT, special entitlements, or another installation method.
- Any accounts, subscriptions, API keys, or other requirements set by the app's developer still apply.
- Downloads come from the original hosts. Community feeds may include modified apps; inclusion here is not a security review or a guarantee that an app will run on your device.

## Having trouble?

| Problem | What to try |
| --- | --- |
| New apps are missing | Refresh the existing source in Flare Store, then check the last successful refresh linked above. |
| An app's version looks old | Check its original source; a new project release may not have reached that feed yet. |
| A download fails | Try again later. The original download host may be unavailable or the link may have changed. |
| An app will not install or open | Check its iOS requirements, signing requirements, and developer's installation instructions. |

Still stuck? [Report a problem](https://github.com/masspimentel/flare-repo/issues/new) with the app name, version, your iOS version, and the error message you see.

## Suggest an app or source

[Open a request](https://github.com/masspimentel/flare-repo/issues/new) with the app's name and a link to its developer or source feed. A developer-maintained HTTPS source is the easiest to keep current.

Apps are combined into one catalog. If multiple feeds list the same app identifier, the first configured source wins. The [build report](https://masspimentel.github.io/flare-repo/build-report.json) records where each listing came from.

## For maintainers

For self-hosting, local builds, or editing the source list, see [MAINTAINING.md](MAINTAINING.md).

Project code is [MIT licensed](LICENSE). App names, descriptions, images, and other upstream material belong to their respective owners.
