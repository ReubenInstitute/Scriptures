#!/bin/sh
# Build python3-scriptures_<version>_all.deb and scriptures-data_<version>_all.deb.
# Usage: packaging/deb/build.sh
set -eu

cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"
VERSION="0.$(git rev-list --count HEAD)"
sed -i "s/^Version: .*/Version: $VERSION/" packaging/deb/control-scriptures
sed -i "s/^Version: .*/Version: $VERSION/" packaging/deb/control-scriptures-data
sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# --- python3-scriptures (code) ---
CODE_DIR="$REPO_ROOT/debian-pkg-scriptures"
rm -rf "$CODE_DIR"
mkdir -p "$CODE_DIR/DEBIAN" "$CODE_DIR/usr/lib/python3/dist-packages" "$CODE_DIR/usr/share/scriptures" "$CODE_DIR/usr/bin"
cp packaging/deb/control-scriptures "$CODE_DIR/DEBIAN/control"
cp Scriptures.py Bible.py Mishnah.py TalmudBavli.py TalmudYerushalmi.py \
   Zohar.py ZoharChadash.py ZoharTikkunim.py \
   "$CODE_DIR/usr/lib/python3/dist-packages/"
cp scriptures-web.py "$CODE_DIR/usr/share/scriptures/scriptures-web.py"
chmod +x "$CODE_DIR/usr/share/scriptures/scriptures-web.py"
ln -s ../share/scriptures/scriptures-web.py "$CODE_DIR/usr/bin/scriptures-web"
dpkg-deb --build --root-owner-group "$CODE_DIR" "python3-scriptures_${VERSION}_all.deb"
rm -rf "$CODE_DIR"
echo "Built python3-scriptures_${VERSION}_all.deb"

# --- scriptures-data (json + csv + Source) ---
DATA_DIR="$REPO_ROOT/debian-pkg-scriptures-data"
rm -rf "$DATA_DIR"
mkdir -p "$DATA_DIR/DEBIAN" "$DATA_DIR/usr/share/scriptures/csv" "$DATA_DIR/usr/bin"
cp packaging/deb/control-scriptures-data "$DATA_DIR/DEBIAN/control"
cp json/*.json "$DATA_DIR/usr/share/scriptures/"
cp csv/*.csv "$DATA_DIR/usr/share/scriptures/csv/"
cp Source.py "$DATA_DIR/usr/share/scriptures/Source.py"
chmod +x "$DATA_DIR/usr/share/scriptures/Source.py"
ln -s ../share/scriptures/Source.py "$DATA_DIR/usr/bin/Source"
dpkg-deb --build --root-owner-group "$DATA_DIR" "scriptures-data_${VERSION}_all.deb"
rm -rf "$DATA_DIR"
echo "Built scriptures-data_${VERSION}_all.deb"
