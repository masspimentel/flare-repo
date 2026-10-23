# Flare Store crash investigation

## Device results

- Main 52-app source: closes Flare Store when opening its app list on iOS 27.2, using the latest Flare Store according to the user.
- Screenshot test below: the user reports the same crash. Removing modern screenshots alone is insufficient; do not publish it as a fix.
- Minimal test: awaiting an on-device result.

## One-app test

Add this source and open **Flare Minimal Test**; no installation is needed:

```text
https://masspimentel.github.io/flare-repo/diagnostics/minimal.json
```

This frozen fixture contains only MiniWatts, with the legacy version fields exported by Flare Store's creator, no screenshot images, and explicit source artwork. The app's identity, description, icon, latest download, version, size, date, and minimum iOS requirement are copied from the captured main feed. It has no Patreon restriction or permission metadata to omit. Version history is deliberately absent from this small diagnostic fixture. This reduces the input to a baseline; it does not isolate one field or prove the cause if it succeeds.

Report whether its app list opens, and whether other sources open successfully in Flare Store. If this also crashes, obtain the Flare Store crash report before trying further feed transformations.

## Screenshot test

Status: still crashes on the user's device. Retained to record the unsuccessful test.

Add this as a separate source in Flare Store, then open its app list:

```text
https://masspimentel.github.io/flare-repo/diagnostics/no-modern-screenshots.json
```

Its display name is **Flare Screenshot Test**. Report whether it opens or closes Flare Store. No app installation is needed. Remove the test source afterward.

This frozen snapshot has the same 52 apps as the main source captured on 2026-10-23 UTC. Only the `screenshots` field was removed from app records; existing `screenshotURLs` remain. The source name and identifier differ to distinguish the test and avoid reusing the existing source identity. Download links, complete version history, OS requirements, permissions, and Patreon restrictions are unchanged.

The original published JSON's SHA-256 was `dc08ba60fb87506376f8976134f1b50c37101b3eb5958e18dafef3d66a6db1c9`.

Reason for the test: the main feed contains string arrays, object arrays, and device dictionaries in `screenshots`. [Flare Store's own creator](https://flarestore.app/repo-creator/) exports the older `screenshotURLs` string list. This difference suggests a hypothesis; it does not establish the cause of the device crash. If the test also closes Flare Store, investigate other fields using a crash report rather than treating screenshot normalization as a fix.

The normal six-hour catalog refresh continues. This diagnostic snapshot deliberately stays fixed for comparison.
