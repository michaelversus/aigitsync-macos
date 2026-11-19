# aigitsync for macOS

Public distribution metadata and Homebrew tap for the aigitsync command-line tool.

[Version 0.1.1](https://github.com/michaelversus/aigitsync-macos/releases/tag/v0.1.1)
is available as a signed, notarized universal macOS binary. This tap contains its
verified release formula. Publication and installation acceptance are separate:
see [DISTRIBUTION.md](DISTRIBUTION.md) for the verified local upgrade and
remaining platform/application acceptance.

## Install

Requires macOS 13 Ventura or later on Apple silicon or Intel, and [Homebrew](https://brew.sh).

```sh
brew tap michaelversus/aigitsync-macos https://github.com/michaelversus/aigitsync-macos.git
if brew help trust >/dev/null 2>&1; then
  brew trust --formula michaelversus/aigitsync-macos/aigitsync
fi
brew install michaelversus/aigitsync-macos/aigitsync
aigitsync --version
aigitsync --help
```

The explicit tap URL is required because this repository does not use the
`homebrew-` naming prefix. On Homebrew versions with a trust command, the step
above trusts only this formula before loading it. See [Homebrew's tap documentation](https://docs.brew.sh/Taps).

Installation only installs the CLI. Capture remains opt-in; installation does not
enable hooks, background services, publishing, or telemetry.

## Update

```sh
brew update
brew upgrade michaelversus/aigitsync-macos/aigitsync
```

Version 0.1.1 improves Codex and Claude transcript ingestion and fixes private
checkpoint retention during pruning. `brew upgrade` updates earlier versions,
including the 0.1.0_1 packaging revision, to the new signed 0.1.1 executable.
Reinstalling the same package version is not an upgrade.

## Release verification

Published releases contain a universal macOS archive, checksums, a release
manifest, and a generated formula. The executable must be signed with Developer ID
Application and notarized by Apple. Homebrew verifies the archive checksum; this
formula's install/test check the original executable digest and its Developer ID
Application signature offline inside Homebrew's sandbox. The local release
validator checks the installed binary and Apple's online notarization outside
that sandbox on each available native Mac. Online notarization requires network
access; `brew test` alone does not establish that acceptance.

Build, signing, notarization, installation and upgrade checks run locally.
No GitHub Actions workflow is required for publication. Record the actual native
platforms checked and any remaining installation or upgrade coverage gaps. See
[DISTRIBUTION.md](DISTRIBUTION.md) for the public release contract and checks.
Report installation problems through this repository's
[issues](https://github.com/michaelversus/aigitsync-macos/issues). Include macOS version,
CPU architecture, Homebrew version, command, and a redacted error message. Do not
include credentials, session transcripts, or captured provider data.

The launcher is a Homebrew shell wrapper. The signed executable and its required
resource bundle remain together in `libexec`; the wrapper executes the stable
Homebrew `opt` path so installed hooks can survive later upgrades. Verification
checks the signed payload and also launches the global command found on `PATH`.
