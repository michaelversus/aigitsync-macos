class Aigitsync < Formula
  desc "Commit-linked AI session context"
  homepage "https://github.com/michaelversus/aigitsync-macos"
  url "https://github.com/michaelversus/aigitsync-macos/releases/download/v0.1.2/aigitsync-0.1.2-macos-universal.tar.gz"
  sha256 "b61daa1efe9aa985f3888c8e9144ac03de446da6a6b031e191f0e0ca47cae821"

  license :cannot_represent
  depends_on macos: :ventura

  skip_clean "libexec/aigitsync"

  def install
    libexec.install "aigitsync", "AIGitSync_AIGitSyncCLI.bundle"
    bin.write_exec_script opt_libexec/"aigitsync"
    ohai "Verifying the original signed binary"
    require "digest"
    expected_sha256 = "aead141fa9047067518246e054c94d6cb2f8771bf3096273e275f208ba30ef84"
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
    assert_equal "aead141fa9047067518246e054c94d6cb2f8771bf3096273e275f208ba30ef84",
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
