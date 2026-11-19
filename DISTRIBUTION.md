# Distribution contract

This repository contains public distribution tooling and metadata. Release tags
target commits in this repository. Application source and provider session data
are not distributed here.

A formula is published only after its corresponding real release has been signed,
notarized, uploaded, and verified. There is no unsigned stable fallback and no
placeholder formula. [Version 0.1.0](https://github.com/michaelversus/aigitsync-macos/releases/tag/v0.1.0)
has been signed, notarized, published and verified as release assets. The checked-in
formula derives from that release manifest and preserves its archive URL,
archive/executable digests and strong signature checks. Mandatory online
notarization remains in the separate CI verifier. The tap can
carry Homebrew compatibility updates independently of the immutable release
formula asset. Actual Homebrew installation, distinct-version upgrade and application workflow acceptance remain
separate evidence.

## Public assets

For version `VERSION`, tag `vVERSION` contains:

- `aigitsync-VERSION-macos-universal.tar.gz`
- `SHA256SUMS`
- `release-manifest.json`
- `aigitsync.rb`, the generated formula subsequently committed as `Formula/aigitsync.rb`

The archive contains `bin/aigitsync` and its required version resource bundle,
`bin/AIGitSync_AIGitSyncCLI.bundle`. It contains no application source or debug caches.
Homebrew places these unchanged payload files together in `libexec` and exposes a
shell wrapper in `bin` that executes `opt_libexec/aigitsync`. The stable `opt`
target preserves executable paths saved by hooks across upgrades. The manifest's
executable digest applies to the signed payload, not the generated wrapper.

Homebrew package revision `1` delivers this launcher fix as `0.1.0_1` without
changing the 0.1.0 binary version, archive, signature or manifest. Packaging
revision metadata belongs to the tap formula, independently of binary releases.

The JSON manifest declares `version`, `source_revision` (a provenance commit hash),
`repository` (`michaelversus/aigitsync-macos`), `archive`, `sha256` (archive),
`binary_sha256` (signed executable), `architectures` (`arm64` and `x86_64`),
`minimum_macos` (`13.0`), `signing_team`, `signing_identifier` (`com.aigitsync.cli`),
and `notarization` with `id` and `status` (`Accepted`). No credential belongs in it.

Published version assets are immutable. A different executable requires a new
release; an existing tag or checksum must not be silently replaced.

## CI evidence

With no formula, CI checks bootstrap consistency and the distribution validators.
It explicitly reports that no release acceptance was executed.

Once a formula exists, CI uses fresh Apple silicon and Intel macOS runners to:

1. Audit the checked-out formula and read its exact version, URL, and archive digest.
2. Download the manifest for that version from this repository's release assets and
   require matching repository, version, archive URL, digest, and signing contract.
3. Install and run the formula's offline Homebrew test: exact binary digest and
   strict all-architecture Developer ID Application signature, team and identifier.
4. Outside the Homebrew sandbox, compare the installed executable digest with the signed executable digest, require
   both architecture slices, verify the Developer ID Application signature, team,
   identifier, hardened runtime, timestamp, and Apple's online notarization check.
5. Run the signed payload's version/help commands and the actual global `PATH`
   command on each runner's native CPU. Require the global command to resolve to
   this installed prefix's wrapper, and reject a missing, wrong or crashing
   launcher even when the direct payload succeeds.

These checks require no source checkout or signing credentials. Signature validation
uses Apple's trust chain as well as the manifest's expected team; checksums alone
are not a substitute for signature validation. The manifest records accepted
notarization, while CI independently checks the installed executable online.

CI installation checks do not establish a real upgrade between distinct released
versions, preservation of existing user configuration, or application workflow
acceptance. Those checks remain separate release evidence. A bare executable has
no stapled ticket, so this distribution makes no fresh offline notarization promise.

Homebrew's sandbox can deny access to Apple's syspolicy service even when the
unchanged binary passes online notarization verification outside the sandbox.
Formula install/test therefore perform offline cryptographic checks. The separate
CI verifier must still pass Apple's full online notarization requirement after
`brew test`; a successful offline formula test alone is not notarization
acceptance. The sandbox is kept enabled and its policy is not widened.
