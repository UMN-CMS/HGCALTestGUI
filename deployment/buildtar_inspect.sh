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
mkdir -p \$HOME/.gui_logs 
while read line; do
	echo "\$(date) \$line" 
	echo "\$(date) \$line" >> \$HOME/.gui_logs/active.log
	if [ -n "$(find \$HOME/.gui_logs/active.log -prune -size 10M)" ]; then
		( 
		echo "ROTATING LOGS"
		cd $\HOME/.gui_logs
		name="\$(date '+%Y-%m-%dT%H-%M-%S').log"
		mv active.log $name
		tar cvzf \$name.tar.gz \$name
	)
	fi
done < <(python3 \$HOME/.local/HGCAL-VI/MainFunctionVI.py 2>&1) 
EOF

cat <<EOF > HGCAL-VI/hgcal_vi_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=HGCAL Visual Inspection GUI
Icon=\$HOME/.local/HGCAL-VI/application_icon.png
Exec=\$HOME/.local/HGCAL-VI/hgcal_vi_gui
EOF

chmod a+x HGCAL-VI/hgcal_vi_gui
chmod a+x HGCAL-VI/hgcal_vi_gui.desktop
cp deployment/application_icon.png HGCAL-VI

for f in HGCAL-VI/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar vzcf ${BUILDDIR}/TAR/HGCAL-VI.tar.gz \
    -X $CWD/.gitignore \
    HGCAL-VI



