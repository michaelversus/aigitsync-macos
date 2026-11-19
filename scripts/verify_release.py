#!/usr/bin/env python3
"""Verify public distribution metadata and the exact Homebrew-installed executable."""

import hashlib
import json
import re
import subprocess
import sys
import urllib.request
import uuid
from pathlib import Path

REPOSITORY = "michaelversus/aigitsync-macos"
IDENTIFIER = "com.aigitsync.cli"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def formula_release(info):
    formulae = info.get("formulae", [])
    require(len(formulae) == 1, "expected exactly one formula")
    formula = formulae[0]
    version = formula.get("versions", {}).get("stable", "")
    require(isinstance(version, str) and re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version),
            "expected stable numeric semantic version")
    return formula, version


def manifest_url(info):
    _, version = formula_release(info)
    return f"https://github.com/{REPOSITORY}/releases/download/v{version}/release-manifest.json"


def validate_metadata(info, manifest):
    formula, version = formula_release(info)
    archive = f"aigitsync-{version}-macos-universal.tar.gz"
    require(manifest.get("version") == version, "manifest version mismatch")
    require(manifest.get("repository") == REPOSITORY, "manifest repository mismatch")
    require(manifest.get("archive") == archive, "manifest archive mismatch")
    require(manifest.get("minimum_macos") == "13.0", "unexpected minimum macOS")
    require(manifest.get("architectures") == ["arm64", "x86_64"], "unexpected architectures")
    require(manifest.get("signing_identifier") == IDENTIFIER, "unexpected signing identifier")
    for field, pattern in (("source_revision", r"[a-f0-9]{40}"),
                           ("sha256", r"[a-f0-9]{64}"),
                           ("binary_sha256", r"[a-f0-9]{64}"),
                           ("signing_team", r"[A-Z0-9]{10}")):
        require(isinstance(manifest.get(field), str) and re.fullmatch(pattern, manifest[field]),
                f"invalid {field}")
    notary = manifest.get("notarization", {})
    require(notary.get("status") == "Accepted", "notarization is not Accepted")
    uuid.UUID(notary.get("id", ""))
    stable = formula.get("urls", {}).get("stable", {})
    expected_url = f"https://github.com/{REPOSITORY}/releases/download/v{version}/{archive}"
    require(stable.get("url") == expected_url, "formula archive URL mismatch")
    require(stable.get("checksum") == manifest["sha256"], "formula archive digest mismatch")


def run(*args):
    result = subprocess.run(args, check=True, text=True, capture_output=True)
    return result.stdout + result.stderr


def verify_installed(binary, manifest):
    require(binary.is_file(), "installed executable missing")
    require(hashlib.sha256(binary.read_bytes()).hexdigest() == manifest["binary_sha256"],
            "Homebrew changed the signed executable digest")
    require(set(run("lipo", "-archs", str(binary)).split()) == {"arm64", "x86_64"},
            "installed executable is not universal")
    team = manifest["signing_team"]
    # Apple's Developer ID intermediate and Application leaf OIDs distinguish this
    # from Apple Development, App Store distribution, and ad-hoc signatures.
    requirement = (f'identifier "{IDENTIFIER}" and anchor apple generic and '
                   'certificate 1[field.1.2.840.113635.100.6.2.6] exists and '
                   'certificate leaf[field.1.2.840.113635.100.6.1.13] exists and '
                   f'certificate leaf[subject.OU] = "{team}" and notarized')
    run("codesign", "--verify", "--strict", "--all-architectures", "-R=" + requirement,
        "--check-notarization", str(binary))
    for arch in manifest["architectures"]:
        details = run("codesign", "--display", "--verbose=4", "--arch", arch, str(binary))
        require(re.search(r"^.*flags=.*\([^\n]*\bruntime\b[^\n]*\)", details, re.MULTILINE)
                and re.search(r"^Timestamp=(?!none$|not set$).+$", details, re.MULTILINE),
                f"missing hardened runtime or signing timestamp for {arch}")
    output = run(str(binary), "--version")
    require(re.search(r"(?<![\d.])" + re.escape(manifest["version"]) + r"(?![\d.])", output),
            "installed version mismatch")
    run(str(binary), "--help")


def main():
    require(len(sys.argv) in (4, 5), "usage: verify_release.py fetch|installed INFO MANIFEST [BINARY]")
    command, info_path, manifest_path = sys.argv[1:4]
    info = json.loads(Path(info_path).read_text())
    if command == "fetch":
        require(len(sys.argv) == 4, "fetch does not accept a binary")
        with urllib.request.urlopen(manifest_url(info), timeout=60) as response:
            data = response.read(65537)
        require(len(data) <= 65536, "manifest exceeds size limit")
        manifest = json.loads(data)
        validate_metadata(info, manifest)
        Path(manifest_path).write_text(json.dumps(manifest, indent=2) + "\n")
        print("Verified public release manifest against formula metadata")
    elif command == "installed":
        require(len(sys.argv) == 5, "installed requires a binary")
        manifest = json.loads(Path(manifest_path).read_text())
        validate_metadata(info, manifest)
        verify_installed(Path(sys.argv[4]), manifest)
        print("Verified installed digest, universal slices, Developer ID, runtime, timestamp, notarization, version and help")
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.CalledProcessError) as error:
        print(f"Release verification failed: {error}", file=sys.stderr)
        sys.exit(1)
