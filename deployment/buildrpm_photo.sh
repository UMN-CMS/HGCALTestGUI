shopt -s globstar

: ${BUILDDIR:=BUILD}
: ${PHOTO_GUI_VERSION:=0.0.2}
: ${PHOTO_GUI_RELEASE:=NORELEASE}

CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/{RPMS,SOURCES,SPECS,SRPMS,BUILD}

rm -rf HGCALPhotoGUI
mkdir HGCALPhotoGUI
cp PhotoTakingGUI/MainFunctionVI.py HGCALPhotoGUI
cp -r PhotoTakingGUI/PythonFiles HGCALPhotoGUI
cp -r awthemes-10.4.0 HGCALPhotoGUI 

for f in HGCALPhotoGUI/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar cf \
    $BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar \
    -X $CWD/.gitignore \
    HGCALPhotoGUI/PythonFiles \
    HGCALPhotoGUI/MainFunctionVI.py \
    HGCALPhotoGUI/awthemes-10.4.0

tar uf $BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar Configs
tar uf $BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar requirements.txt

tmp=$(mktemp -d)
pushd $PWD
cd $tmp
cat <<EOF > hgcal_photo_gui
#!/usr/bin/env bash

DEFAULT_CONFIG_PATH="/etc/HGCALPhotoGUI/active.yaml"
if [[ -e \$DEFAULT_CONFIG_PATH ]]; then
   CONFIGFILE="\$DEFAULT_CONFIG_PATH"
else
   CONFIGFILE="/etc/HGCALPhotoGUI/\$1_cfg.yaml"
fi
python3 /opt/HGCALPhotoGUI/__main__.py "\$CONFIGFILE"
EOF

cat <<EOF > hgcal_photo_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=HGCAL Photo GUI
Icon=/usr/share/HGCALPhotoGUI/application_icon.png
Exec=/usr/bin/hgcal_photo_gui 
EOF

chmod a+x hgcal_photo_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar hgcal_photo_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar hgcal_photo_gui.desktop
popd

pushd $PWD
echo "$PWD"
cd deployment
tar uf $CWD/$BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar application_icon.png
popd

gzip $BUILDDIR/SOURCES/HGCALPhotoGUI-${PHOTO_GUI_VERSION}-${PHOTO_GUI_RELEASE}.tar 

cp deployment/photo_gui.spec $BUILDDIR/SPECS

rpmbuild --define "_topdir $(realpath BUILD)" -ba BUILD/SPECS/photo_gui.spec

