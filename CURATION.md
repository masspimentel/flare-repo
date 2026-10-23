# Source curation log

This log records source reviews and their limits. Acceptance means a feed passed the checks described here at the time of review. It is not a malware audit, an endorsement of every future release, or a device installation test.

Reviews consider the upstream project's identity and public history, release ownership, available source and build information, metadata validity, download availability, and installation requirements. Community feeds are acceptable when their provenance is transparent. HTTPS and a successful download response alone do not establish safety. Existing source preference and upstream access restrictions are retained.

Daily discovery aims to investigate 5–10 new candidates across varied categories. Additions depend on the evidence; there is no minimum quota. The six-hour catalog refresh updates listings from already configured feeds separately.

## 2026-10-22 — seven feeds added

Eight new candidate feeds were reviewed. Seven were accepted, adding seven distinct app identifiers to the previous 45 listings. The expected catalog after this batch is 52 listings from 30 feeds.

The seven accepted feeds are generated individually by [AltGallery](https://github.com/bebound/AltGallery), a public MIT-licensed collection with visible generation configurations and update workflows. Each reviewed app's release URL points directly to its upstream GitHub project. All current IPA links returned HTTP 200 with binary content types, followed HTTPS redirects to GitHub release infrastructure, and matched release assets with GitHub-published SHA-256 digests. No IPA files were downloaded or executed, so those digests were recorded rather than independently recomputed.

| App | Category | Feed and upstream evidence | Requirements or limitations |
| --- | --- | --- | --- |
| Musly | Music | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/Musly/apps.json) · [Project](https://github.com/dddevid/Musly) · [Reviewed release 2.0.3](https://github.com/dddevid/Musly/releases/tag/v2.0.3) | iOS 15+. A self-hosted library needs a compatible music server; other music sources depend on the app's services. |
| MiniWatts | Device utilities | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/MiniWatts/apps.json) · [Project](https://github.com/ResistanceTo/MiniWatts) · [Reviewed release 1.5.1](https://github.com/ResistanceTo/MiniWatts/releases/tag/v1.5.1) | iOS 17+. Uses private diagnostic APIs, which may change in iOS updates. The public app/widget entitlement files declare an app group; the developer documents ordinary sideloading. |
| Tsumiru | Reading | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/Suwayomi-Tsumiru/apps.json) · [Project](https://github.com/Suwayomi/Suwayomi-Tsumiru) · [Reviewed release 1.5.1](https://github.com/Suwayomi/Suwayomi-Tsumiru/releases/tag/v1.5.1) | iOS 14+. Requires a Suwayomi-Server instance. |
| Doer | Social | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/Doer/apps.json) · [Project](https://github.com/moliango/doer) · [Reviewed release 1.8.6](https://github.com/moliango/doer/releases/tag/v1.8.6) | iOS 15+. A third-party Linux.do client; site login and account rules apply. A smaller project with public source and CI-uploaded release assets; authentication code was not audited. |
| Novella | Books | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/Novella/apps.json) · [Project](https://github.com/celia-sh/Novella) · [Reviewed release 2.6.0](https://github.com/celia-sh/Novella/releases/tag/v2.6.0) | iOS 16.4+. Third-party client for a Chinese-language reading service; its account and content rules apply. |
| MoviePilotLite | Media management | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/MoviePilotLite/apps.json) · [Project](https://github.com/singleton-altman/MoviePilotLite) · [Reviewed release 1.2.5](https://github.com/singleton-altman/MoviePilotLite/releases/tag/release-v1.2.5-2026-10-16) | iOS 15+. Requires a MoviePilot v2 server; this is a management client, not a bundled media library. |
| Pixiv-SwiftUI | Art | [Feed](https://raw.githubusercontent.com/bebound/AltGallery/master/apps/Pixiv-SwiftUI/apps.json) · [Project](https://github.com/Eslzzyl/Pixiv-SwiftUI) · [Reviewed release 0.16.3](https://github.com/Eslzzyl/Pixiv-SwiftUI/releases/tag/v0.16.3) | iOS 17+ per feed. Third-party Pixiv client; the developer calls it experimental and notes that iOS 17 support is untested. Account and content settings apply. |

The generated per-app feeds do not provide permission declarations. These were left absent rather than invented. MiniWatts' upstream entitlement files were inspected separately; the remaining apps' complete entitlements were not verified against binaries. These limitations matter especially for clients that require explicit permission lists.

### Deferred candidate

[Tools for Autodarts](https://github.com/creazy231/tools-for-autodarts) publishes a developer-owned [source](https://raw.githubusercontent.com/creazy231/tools-for-autodarts/main/Autodarts_Tools_Source.json) with a working current IPA. However, all five historical version records use the same mutable `releases/latest/download` URL. Selecting an older version could therefore download the current binary with mismatched version metadata. Defer until the source pins each release correctly. This is a metadata concern, not a malware allegation.

### Recorded release digests

GitHub's published digests for the assets reviewed above:

```text
Musly             669c35e111c30e6161bbc5eae192d6598f48d669397a06dfb1f6ea1af8bb1450
MiniWatts         3325a991710d3b9cb9bbd8e2bd37c2a5e8ab48edc3cbb8abdb23aae06a7853e0
Tsumiru           8229708b98dfbcb190c32a91042ce030655b7b2e1c96f776fe89f35a330e3880
Doer              246c9de45c3a402e13c7528c31050981763afda5ae40cf552c8d7abfa10bdefa
Novella           e138a10f177386de28110061051e5842da3e139eb780e35a225e947f98378cc1
MoviePilotLite    4ac33d9b23f7b750cfcc09d22bc42f187d102c9d009327a8320dbc1e104d95f7
Pixiv-SwiftUI     8da30168148c9a1e4a1a2eeb53329653f897ec92fe50ef6267845f05ad2907eb
```
