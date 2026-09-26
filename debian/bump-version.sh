#!/bin/sh
# Run this before committing. Bumps the version to match the commit
# count your commit is about to produce (current count + 1), so once
# committed, the version in these files is exactly correct.
# Usage: debian/bump-version.sh
set -eu

cd "$(dirname "$0")/.."

COUNT="$(($(git rev-list --count HEAD) + 1))"
MAJOR="$(grep '^version' pyproject.toml | sed -E 's/version = "([0-9]+)\..*/\1/')"
VERSION="$MAJOR.$COUNT"

sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
sed -i "1s/^scriptures (.*)/scriptures ($VERSION)/" debian/changelog

echo "Bumped to $VERSION"
