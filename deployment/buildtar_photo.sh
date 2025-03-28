set -euo pipefail
shopt -s globstar

: ${BUILDDIR:=BUILD}
CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/TAR

rm -rf HGCAL-Photo
mkdir HGCAL-Photo
cp -r PhotoTakingGUI/PythonFiles HGCAL-Photo
cp -r PhotoTakingGUI/Configs HGCAL-Photo
cp -r PhotoTakingGUI/MainFunctionPhoto.py HGCAL-Photo
cp -r awthemes-10.4.0 HGCAL-Photo 

cat <<EOF > HGCAL-Photo/hgcal_photo_gui
#!/usr/bin/env bash

mkdir -p \$HOME/.gui_logs/photogui
while read line; do
	echo "\$(date) \$line" 
	echo "\$(date) \$line" >> \$HOME/.gui_logs/photogui/active.log
	if [ -n "\$(find \$HOME/.gui_logs/photogui/active.log -prune -size 10M)" ]; then
		( 
		echo "ROTATING LOGS"
		cd $\HOME/.gui_logs/photogui
		name="\$(date '+%Y-%m-%dT%H-%M-%S').log"
		mv active.log \$name
		tar cvzf \$name.tar.gz \$name
	)
	fi
done < <(python3 \$HOME/.local/HGCAL-Photo/MainFunctionVI.py 2>&1) 
EOF

cat <<EOF > HGCAL-Photo/hgcal_photo_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=HGCAL Visual Inspection GUI
Icon=\$HOME/.local/HGCAL-Photo/application_icon.png
Exec=\$HOME/.local/HGCAL-Photo/hgcal_photo_gui
EOF

chmod a+x HGCAL-Photo/hgcal_photo_gui
chmod a+x HGCAL-Photo/hgcal_photo_gui.desktop
cp deployment/application_icon.png HGCAL-Photo

for f in HGCAL-Photo/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar vzcf ${BUILDDIR}/TAR/HGCAL-Photo.tar.gz \
    -X $CWD/.gitignore \
    HGCAL-Photo



