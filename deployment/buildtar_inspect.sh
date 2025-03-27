set -euo pipefail
shopt -s globstar

: ${BUILDDIR:=BUILD}
CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/TAR

rm -rf HGCAL-VI
mkdir HGCAL-VI
cp -r CheckInGUI/PythonFiles HGCAL-VI
cp -r CheckInGUI/Configs HGCAL-VI
cp -r CheckInGUI/MainFunctionVI.py HGCAL-VI
cp -r awthemes-10.4.0 HGCAL-VI 
cat <<EOF > HGCAL-VI/hgcal_vi_gui
#!/usr/bin/env bash
python3 $HOME/.local/HGCAL-VI/MainFunctionVI.py
EOF

cat <<EOF > HGCAL-VI/hgcal_vi_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=HGCAL Test GUI
Icon=~/.local/HGCAL-VI/application_icon.png
Exec=~/.local/HGCAL-VI/hgcal_vi_gui
EOF

chmod a+x HGCAL-VI/hgcal_vi_gui
cp deployment/application_icon.png HGCAL-VI

for f in HGCAL-VI/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar vzcf ${BUILDDIR}/TAR/HGCAL-VI.tar.gz \
    -X $CWD/.gitignore \
    HGCAL-VI



