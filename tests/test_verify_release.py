"""Synthetic metadata tests; these do not certify a release or install Homebrew."""

import copy
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("verify_release", Path(__file__).parents[1] / "scripts/verify_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "version": "0.1.0", "source_revision": "a" * 40,
            "repository": release.REPOSITORY,
            "archive": "aigitsync-0.1.0-macos-universal.tar.gz",
            "sha256": "b" * 64, "binary_sha256": hashlib.sha256(b"synthetic fixture").hexdigest(),
            "architectures": ["arm64", "x86_64"], "minimum_macos": "13.0",
            "signing_team": "ABC1234567", "signing_identifier": release.IDENTIFIER,
            "notarization": {"id": "12345678-1234-1234-1234-123456789abc", "status": "Accepted"},
        }
        self.info = {"formulae": [{"versions": {"stable": "0.1.0"}, "urls": {"stable": {
            "url": f"https://github.com/{release.REPOSITORY}/releases/download/v0.1.0/{self.manifest['archive']}",
            "checksum": self.manifest["sha256"],
        }}}]}

    def test_matching_metadata(self):
        release.validate_metadata(self.info, self.manifest)
        self.assertEqual(release.manifest_url(self.info),
                         f"https://github.com/{release.REPOSITORY}/releases/download/v0.1.0/release-manifest.json")

    def test_rejects_wrong_manifest_contract(self):
        for field, value in {
            "version": "0.2.0", "source_revision": "main", "repository": "other/repo",
            "archive": "../archive.tar.gz", "sha256": "invalid", "binary_sha256": "invalid",
            "architectures": ["arm64"], "minimum_macos": "12.0", "signing_team": 'x" or true',
            "signing_identifier": "other", "notarization": {"id": "invalid", "status": "Accepted"},
        }.items():
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest[field] = value
                with self.assertRaises(ValueError):
                    release.validate_metadata(self.info, manifest)

    def test_rejects_unaccepted_notarization(self):
        for status in ("In Progress", "Rejected", None):
            self.manifest["notarization"]["status"] = status
            with self.assertRaises(ValueError):
                release.validate_metadata(self.info, self.manifest)

    def test_rejects_wrong_archive_url_or_hash(self):
        for field, value in (("url", "https://example.com/archive.tar.gz"), ("checksum", "c" * 64)):
            info = copy.deepcopy(self.info)
            info["formulae"][0]["urls"]["stable"][field] = value
            with self.assertRaises(ValueError):
                release.validate_metadata(info, self.manifest)

    def test_rejects_nonrelease_version_and_extra_formulae(self):
        for version in ("HEAD", "0.1.0-rc1", "../0.1.0", "01.0.0", None):
            self.info["formulae"][0]["versions"]["stable"] = version
            with self.assertRaises(ValueError):
                release.manifest_url(self.info)
        self.info["formulae"] = []
        with self.assertRaises(ValueError):
            release.manifest_url(self.info)

    def binary(self, root):
        binary = Path(root) / "aigitsync"
        binary.write_bytes(b"synthetic fixture")
        return binary

    def test_rejects_homebrew_rewritten_binary_before_execution(self):
        with tempfile.TemporaryDirectory() as root, patch.object(release, "run") as run:
            binary = self.binary(root)
            binary.write_bytes(b"changed by relocation")
            with self.assertRaisesRegex(ValueError, "digest"):
                release.verify_installed(binary, self.manifest)
            run.assert_not_called()

    def test_verifies_both_slices_and_apple_trust_before_cli(self):
        outputs = ["arm64 x86_64", "", "flags=0x10000(runtime)\nTimestamp=Nov 19 2026",
                   "flags=0x10000(runtime)\nTimestamp=Nov 19 2026", "aigitsync 0.1.0", "help"]
        with tempfile.TemporaryDirectory() as root, patch.object(release, "run", side_effect=outputs) as run:
            release.verify_installed(self.binary(root), self.manifest)
            signature = run.call_args_list[1].args
            self.assertIn("--all-architectures", signature)
            self.assertIn("--check-notarization", signature)
            self.assertIn("anchor apple generic", signature[4])
            self.assertIn("1.2.840.113635.100.6.1.13", signature[4])
            self.assertIn(self.manifest["signing_team"], signature[4])

    def test_rejects_wrong_architecture_or_missing_runtime(self):
        for outputs in (["arm64"], ["arm64 x86_64", "", "Timestamp=today"]):
            with self.subTest(outputs=outputs), tempfile.TemporaryDirectory() as root:
                with patch.object(release, "run", side_effect=outputs), self.assertRaises(ValueError):
                    release.verify_installed(self.binary(root), self.manifest)

    def test_signature_or_notarization_failure_stops_cli_execution(self):
        with tempfile.TemporaryDirectory() as root:
            failure = subprocess.CalledProcessError(1, ["codesign"])
            with patch.object(release, "run", side_effect=["arm64 x86_64", failure]) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    release.verify_installed(self.binary(root), self.manifest)
                self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
