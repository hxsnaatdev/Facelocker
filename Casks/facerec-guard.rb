cask "facerec-guard" do
  version "0.1.0"
  sha256 "REPLACE_WITH_DMG_SHA256"

  url "https://github.com/ariz/facerec/releases/download/v#{version}/FaceRecGuard-#{version}.dmg"
  name "FaceRec Guard"
  desc "Locks macOS when no authorized face is present"
  homepage "https://github.com/ariz/facerec"

  app "FaceRecGuard.app"

  zap trash: [
    "~/Library/Application Support/FaceRecGuard",
    "~/Library/Preferences/com.ariz.facerecguard.plist",
  ]
end
