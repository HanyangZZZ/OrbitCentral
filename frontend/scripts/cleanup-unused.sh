#!/bin/bash
# Cleanup script for unused frontend assets
# Run from frontend directory: ./scripts/cleanup-unused.sh

echo "🧹 Cleaning up unused assets..."

# Remove empty figma-export-3 folder
if [ -d "public/figma-export-3" ]; then
    rm -rf "public/figma-export-3"
    echo "✓ Removed empty public/figma-export-3"
fi

# Remove duplicate figma-discovery folder (same as figma-discovery-page)
if [ -d "public/figma-discovery" ]; then
    rm -rf "public/figma-discovery"
    echo "✓ Removed duplicate public/figma-discovery"
fi

# Remove raw Figma export folders (these are source files, not needed in production)
# Keep only the public/ versions which are used in the app
folders_to_remove=(
    "Figma business details page"
    "Figma discovery page"
    "Figma Favorite Page"
    "figma home page"
    "Figma leadership board page "
)

for folder in "${folders_to_remove[@]}"; do
    if [ -d "$folder" ]; then
        rm -rf "$folder"
        echo "✓ Removed source folder: $folder"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Note: The following folders in public/ are actively used by the app:"
echo "  - public/figma-business-details-page"
echo "  - public/figma-discovery-page"
echo "  - public/figma-favorites-page"
echo "  - public/figma-home-page"
echo "  - public/figma-leaderboard-page"
