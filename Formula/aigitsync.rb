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
    requirement = 'identifier "com.aigitsync.cli" and anchor apple generic and ' \
                  "certificate 1[field.1.2.840.113635.100.6.2.6] exists and " \
                  "certificate leaf[field.1.2.840.113635.100.6.1.13] exists and " \
                  'certificate leaf[subject.OU] = "4N99UJ999D"'
    system "/usr/bin/codesign", "--verify", "--strict", "--all-architectures", "-R=#{requirement}", bin/"aigitsync"
  end

  test do
    require "digest"
    assert_equal "ad58e874cde95260ab6131fa49dd6c2940895999650b32894f960a3784e369fb",
                 Digest::SHA256.file(bin/"aigitsync").hexdigest
    requirement = 'identifier "com.aigitsync.cli" and anchor apple generic and ' \
                  "certificate 1[field.1.2.840.113635.100.6.2.6] exists and " \
                  "certificate leaf[field.1.2.840.113635.100.6.1.13] exists and " \
                  'certificate leaf[subject.OU] = "4N99UJ999D"'
    system "/usr/bin/codesign", "--verify", "--strict", "--all-architectures", "-R=#{requirement}", bin/"aigitsync"
    assert_equal "aigitsync #{version}", shell_output("#{bin}/aigitsync --version").strip
  end
end
