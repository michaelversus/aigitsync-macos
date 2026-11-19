class Aigitsync < Formula
  desc "Commit-linked AI session context"
  homepage "https://github.com/michaelversus/aigitsync-macos"
  url "https://github.com/michaelversus/aigitsync-macos/releases/download/v0.1.0/aigitsync-0.1.0-macos-universal.tar.gz"
  sha256 "b7a49f9f9a1160bbb86dc664223f11c10e68afa7028a18bb5b03e778b4e86793"

  license :cannot_represent
  depends_on macos: :ventura

  skip_clean "bin/aigitsync"

  def install
    bin.install "aigitsync", "AIGitSync_AIGitSyncCLI.bundle"
    ohai "Verifying the original signed binary"
    require "digest"
    expected_sha256 = "ad58e874cde95260ab6131fa49dd6c2940895999650b32894f960a3784e369fb"
    odie "Signed binary changed" if Digest::SHA256.file(bin/"aigitsync").hexdigest != expected_sha256
    requirement = '-R=anchor apple generic and certificate leaf[subject.OU] = "4N99UJ999D" and notarized'
    system "/usr/bin/codesign", "--verify", "--strict", requirement, "--check-notarization", bin/"aigitsync"
  end

  test do
    require "digest"
    assert_equal "ad58e874cde95260ab6131fa49dd6c2940895999650b32894f960a3784e369fb",
                 Digest::SHA256.file(bin/"aigitsync").hexdigest
    requirement = '-R=anchor apple generic and certificate leaf[subject.OU] = "4N99UJ999D" and notarized'
    system "/usr/bin/codesign", "--verify", "--strict", requirement, "--check-notarization", bin/"aigitsync"
    assert_equal "aigitsync #{version}", shell_output("#{bin}/aigitsync --version").strip
  end
end
