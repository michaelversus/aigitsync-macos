# Distribution contract

This repository contains public distribution tooling and metadata. Release tags
target commits in this repository. Application source and provider session data
are not distributed here.

A formula is published only after its corresponding real release has been signed,
notarized, uploaded, and verified. There is no unsigned stable fallback and no
placeholder formula. [Version 0.1.1](https://github.com/michaelversus/aigitsync-macos/releases/tag/v0.1.1)
has been signed, notarized, published and verified as release assets. The checked-in
formula derives from that release manifest and preserves its archive URL,
archive/executable digests and strong signature checks. Mandatory online
notarization remains in the separate local installed validator. The tap can
carry Homebrew compatibility updates independently of the immutable release
formula asset. Homebrew installation, distinct-version upgrade and application
workflow acceptance are recorded separately.

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

## Local release verification

Release and development checks run locally. This tap has no automatic GitHub
Actions workflow. Before publishing a formula, run its validators:

```sh
python3 -B -m unittest discover -s tests -v
```

On each available native Mac, record the exact tap commit and:

1. Audit the formula and read its exact version, URL and archive digest with
   `brew info --json=v2`.
2. Use `scripts/verify_release.py fetch INFO MANIFEST` to download and validate
   the version's published manifest against the formula metadata.
3. Install the formula on a clean machine, or perform a real `brew upgrade`
   from the previous installed version. Record the prior version and snapshot
   existing hook/configuration hashes before an upgrade.
4. Run `brew test` for the offline signed-binary digest and Developer ID checks.
5. Run `scripts/verify_release.py installed INFO MANIFEST PAYLOAD GLOBAL_COMMAND`
   outside Homebrew's sandbox for universal slices, Developer ID, hardened
   runtime, timestamp, online notarization, version and global launcher checks.
6. After upgrade, compare existing hook/configuration hashes. Record the actual
   native OS/CPU and version transition; report unavailable clean-Mac or Intel
   coverage rather than inferring it from universal slices or emulation.

These checks require no application source checkout or signing credentials.
Signature validation uses Apple's trust chain as well as the manifest's expected
team; checksums alone
are not a substitute for signature validation. The manifest records accepted
notarization; the local validator independently checks the installed executable
online.

Local observations establish acceptance only for the actual machine and version
transition checked. Real application/provider workflows remain separate evidence.
A bare executable has no stapled ticket, so this distribution makes no fresh
offline notarization promise.

Homebrew's sandbox can deny access to Apple's syspolicy service even when the
unchanged binary passes online notarization verification outside the sandbox.
Formula install/test therefore perform offline cryptographic checks. The separate
local validator must still pass Apple's full online notarization requirement after
`brew test`; a successful offline formula test alone is not notarization
acceptance. The sandbox is kept enabled and its policy is not widened.
