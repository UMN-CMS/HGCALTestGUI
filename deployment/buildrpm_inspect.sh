set -e

shopt -s globstar

: ${BUILDDIR:=BUILD}
: ${GUI_VERSION:=0.0.3}
: ${GUI_RELEASE:=NORELEASE}

CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/{RPMS,SOURCES,SPECS,SRPMS,BUILD}

rm -rf HGCALCheckinGUI
mkdir HGCALCheckinGUI
cp CheckInGUI/MainFunctionVI.py HGCALCheckinGUI
cp -r CheckInGUI/PythonFiles HGCALCheckinGUI 
cp -r CheckInGUI/Configs HGCALCheckinGUI 
cp -r awthemes-10.4.0 HGCALCheckinGUI 


for f in HGCALCheckinGUI/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar cf \
    $BUILDDIR/SOURCES/HGCALCheckinGUI-${GUI_VERSION}-${GUI_RELEASE}.tar \
    -X $CWD/.gitignore \
    HGCALCheckinGUI/PythonFiles \
    HGCALCheckinGUI/MainFunctionVI.py \
    HGCALCheckinGUI/awthemes-10.4.0 \
    HGCALCheckinGUI/Configs


tmp=$(mktemp -d)
pushd $PWD
cd $tmp
cat <<EOF > hgcal_checkin_gui
#!/usr/bin/env bash

python3 /opt/HGCALCheckinGUI/MainFunctionVI.py
EOF

cat <<EOF > hgcal_checkin_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=HGCAL Checkin GUI
Icon=/usr/share/HGCALCheckinGUI/application_icon.png
Exec=/usr/bin/hgcal_checkin_gui 
EOF

echo $PWD
ls

chmod a+x hgcal_checkin_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALCheckinGUI-${GUI_VERSION}-${GUI_RELEASE}.tar hgcal_checkin_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALCheckinGUI-${GUI_VERSION}-${GUI_RELEASE}.tar hgcal_checkin_gui.desktop
popd

pushd $PWD
echo "$PWD"
cd deployment
tar uf $CWD/$BUILDDIR/SOURCES/HGCALCheckinGUI-${GUI_VERSION}-${GUI_RELEASE}.tar application_icon.png
popd

gzip $BUILDDIR/SOURCES/HGCALCheckinGUI-${GUI_VERSION}-${GUI_RELEASE}.tar 

cp deployment/checkingui.spec $BUILDDIR/SPECS

rpmbuild --define "_topdir $(realpath BUILD)" -ba BUILD/SPECS/checkingui.spec
