#!/bin/bash
# Script to upload the executable to GitHub Releases
# Usage: ./upload_to_releases.sh [version_tag]
# Example: ./upload_to_releases.sh v1.0.0

set -e

VERSION_TAG=${1:-"latest"}
EXECUTABLE_PATH="dist/youtube-transcript-manager"
REPO="droneshire/cis-youtube-transcript-manager"

if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "Error: Executable not found at $EXECUTABLE_PATH"
    echo "Run 'make py_package' first to build the executable"
    exit 1
fi

echo "Uploading $EXECUTABLE_PATH to GitHub Releases..."
echo "Repository: $REPO"
echo "Version tag: $VERSION_TAG"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    echo ""
    echo "Alternatively, you can manually:"
    echo "1. Go to https://github.com/$REPO/releases/new"
    echo "2. Create a new release with tag $VERSION_TAG"
    echo "3. Upload $EXECUTABLE_PATH as an asset"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Create or update release and upload asset
if [ "$VERSION_TAG" = "latest" ]; then
    # For latest, we'll use the latest tag or create a new one
    LATEST_TAG=$(gh release list --repo "$REPO" --limit 1 --json tagName -q '.[0].tagName' 2>/dev/null || echo "")
    if [ -z "$LATEST_TAG" ]; then
        VERSION_TAG="v1.0.0"
        echo "Creating new release: $VERSION_TAG"
        gh release create "$VERSION_TAG" \
            --repo "$REPO" \
            --title "Release $VERSION_TAG" \
            --notes "YouTube Transcript Manager executable" \
            "$EXECUTABLE_PATH"
    else
        echo "Updating latest release: $LATEST_TAG"
        gh release upload "$LATEST_TAG" \
            --repo "$REPO" \
            --clobber \
            "$EXECUTABLE_PATH"
    fi
else
    # Check if release exists
    if gh release view "$VERSION_TAG" --repo "$REPO" &> /dev/null; then
        echo "Release $VERSION_TAG exists, uploading asset..."
        gh release upload "$VERSION_TAG" \
            --repo "$REPO" \
            --clobber \
            "$EXECUTABLE_PATH"
    else
        echo "Creating new release: $VERSION_TAG"
        gh release create "$VERSION_TAG" \
            --repo "$REPO" \
            --title "Release $VERSION_TAG" \
            --notes "YouTube Transcript Manager executable" \
            "$EXECUTABLE_PATH"
    fi
fi

echo ""
echo "✅ Successfully uploaded to GitHub Releases!"
echo "Download URL: https://github.com/$REPO/releases/latest/download/youtube-transcript-manager"
