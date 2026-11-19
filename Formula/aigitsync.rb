class Aigitsync < Formula
  desc "Commit-linked AI session context"
  homepage "https://github.com/michaelversus/aigitsync-macos"
  url "https://github.com/michaelversus/aigitsync-macos/releases/download/v0.1.3/aigitsync-0.1.3-macos-universal.tar.gz"
  sha256 "5a32dcba7a0f813262ce343c4828c0882fa7e25165f472b13273eabbd23d70ea"

  license :cannot_represent
  depends_on macos: :ventura

  skip_clean "libexec/aigitsync"

  def install
    libexec.install "aigitsync", "AIGitSync_AIGitSyncCLI.bundle"
    bin.write_exec_script opt_libexec/"aigitsync"
    ohai "Verifying the original signed binary"
    require "digest"
    expected_sha256 = "ca7f85baf889bca21746d9918e4472ef962eb76fb2cdce5b5302132b8bd046a0"
    odie "Signed binary changed" if Digest::SHA256.file(libexec/"aigitsync").hexdigest != expected_sha256
    requirement = 'identifier "com.aigitsync.cli" and anchor apple generic and ' \
                  "certificate 1[field.1.2.840.113635.100.6.2.6] exists and " \
                  "certificate leaf[field.1.2.840.113635.100.6.1.13] exists and " \
                  'certificate leaf[subject.OU] = "4N99UJ999D"'
    system "/usr/bin/codesign", "--verify", "--strict", "--all-architectures",
           "-R=#{requirement}", libexec/"aigitsync"
  end

  test do
    require "digest"
    assert_equal "ca7f85baf889bca21746d9918e4472ef962eb76fb2cdce5b5302132b8bd046a0",
                 Digest::SHA256.file(libexec/"aigitsync").hexdigest
    requirement = 'identifier "com.aigitsync.cli" and anchor apple generic and ' \
                  "certificate 1[field.1.2.840.113635.100.6.2.6] exists and " \
                  "certificate leaf[field.1.2.840.113635.100.6.1.13] exists and " \
                  'certificate leaf[subject.OU] = "4N99UJ999D"'
    system "/usr/bin/codesign", "--verify", "--strict", "--all-architectures",
           "-R=#{requirement}", libexec/"aigitsync"
    [bin/"aigitsync", HOMEBREW_PREFIX/"bin/aigitsync", "aigitsync"].each do |command|
      assert_equal "aigitsync #{version}", shell_output("#{command} --version").strip
    end
    system HOMEBREW_PREFIX/"bin/aigitsync", "--help"
  end
end
