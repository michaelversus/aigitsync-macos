class Aigitsync < Formula
  desc "Commit-linked AI session context"
  homepage "https://github.com/michaelversus/aigitsync-macos"
  url "https://github.com/michaelversus/aigitsync-macos/releases/download/v0.1.0/aigitsync-0.1.0-macos-universal.tar.gz"
  version "0.1.0"
  sha256 "b7a49f9f9a1160bbb86dc664223f11c10e68afa7028a18bb5b03e778b4e86793"

  license :cannot_represent
  skip_clean "bin/aigitsync"

  depends_on :macos
  depends_on macos: :ventura

  def install
    bin.install "aigitsync", "AIGitSync_AIGitSyncCLI.bundle"
    ohai "Verifying the original signed binary"
    require "digest"
    odie "Signed binary changed" unless Digest::SHA256.file(bin/"aigitsync").hexdigest == "ad58e874cde95260ab6131fa49dd6c2940895999650b32894f960a3784e369fb"
    system "/usr/bin/codesign", "--verify", "--strict", '-R=anchor apple generic and certificate leaf[subject.OU] = "4N99UJ999D" and notarized', "--check-notarization", bin/"aigitsync"
  end

  test do
    require "digest"
    assert_equal "ad58e874cde95260ab6131fa49dd6c2940895999650b32894f960a3784e369fb", Digest::SHA256.file(bin/"aigitsync").hexdigest
    system "/usr/bin/codesign", "--verify", "--strict", '-R=anchor apple generic and certificate leaf[subject.OU] = "4N99UJ999D" and notarized', "--check-notarization", bin/"aigitsync"
    assert_equal "aigitsync #{version}", shell_output("#{bin}/aigitsync --version").strip
  end
end
