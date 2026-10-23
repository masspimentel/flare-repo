# Screenshot compatibility test

Status: awaiting an on-device result; this is a diagnostic source, not a confirmed fix.

Add this as a separate source in Flare Store, then open its app list:

```text
https://masspimentel.github.io/flare-repo/diagnostics/no-modern-screenshots.json
```

Its display name is **Flare Screenshot Test**. Report whether it opens or closes Flare Store. No app installation is needed. Remove the test source afterward.

This frozen snapshot has the same 52 apps as the main source captured on 2026-10-23 UTC. Only the `screenshots` field was removed from app records; existing `screenshotURLs` remain. The source name and identifier differ to distinguish the test and avoid reusing the existing source identity. Download links, complete version history, OS requirements, permissions, and Patreon restrictions are unchanged.

The original published JSON's SHA-256 was `dc08ba60fb87506376f8976134f1b50c37101b3eb5958e18dafef3d66a6db1c9`.

Reason for the test: the main feed contains string arrays, object arrays, and device dictionaries in `screenshots`. [Flare Store's own creator](https://flarestore.app/repo-creator/) exports the older `screenshotURLs` string list. This difference suggests a hypothesis; it does not establish the cause of the device crash. If the test also closes Flare Store, investigate other fields using a crash report rather than treating screenshot normalization as a fix.

The normal six-hour catalog refresh continues. This diagnostic snapshot deliberately stays fixed for comparison.
