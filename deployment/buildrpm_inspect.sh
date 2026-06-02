set -e

shopt -s globstar

: ${BUILDDIR:=BUILD}
: ${GUI_VERSION:=0.0.3}
: ${GUI_RELEASE:=NORELEASE}
: ${GUI_NAME:=HGCALCheckinGUI}
: ${GUI_IMAGE:=application_icon.png}
: ${GUI_PREFIX:=hgcal}

export GUI_PREFIX
export GUI_NAME
export GUI_IMAGE

CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/{RPMS,SOURCES,SPECS,SRPMS,BUILD}

rm -rf $GUI_NAME
mkdir $GUI_NAME
cp CheckInGUI/MainFunctionVI.py $GUI_NAME
cp -r CheckInGUI/PythonFiles $GUI_NAME 
cp -r CheckInGUI/Configs $GUI_NAME 
cp -r awthemes-10.4.0 $GUI_NAME 


for f in $GUI_NAME/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar cf \
    $BUILDDIR/SOURCES/$GUI_NAME-${GUI_VERSION}-${GUI_RELEASE}.tar \
    -X $CWD/.gitignore \
    $GUI_NAME/PythonFiles \
    $GUI_NAME/MainFunctionVI.py \
    $GUI_NAME/awthemes-10.4.0 \
    $GUI_NAME/Configs


tmp=$(mktemp -d)
pushd $PWD
cd $tmp
cat <<EOF > ${GUI_PREFIX}_checkin_gui
#!/usr/bin/env bash

python3 /opt/$GUI_NAME/MainFunctionVI.py
EOF

cat <<EOF > ${GUI_PREFIX}_checkin_gui.desktop
[Desktop Entry]
Type=Application
Terminal=True
Name=$GUI_NAME
Icon=/usr/share/$GUI_NAME/$GUI_IMAGE
Exec=gnome-terminal -- /usr/bin/${GUI_PREFIX}_checkin_gui 
EOF

echo $PWD
ls

chmod a+x ${GUI_PREFIX}_checkin_gui
tar uf $CWD/$BUILDDIR/SOURCES/$GUI_NAME-${GUI_VERSION}-${GUI_RELEASE}.tar ${GUI_PREFIX}_checkin_gui
tar uf $CWD/$BUILDDIR/SOURCES/$GUI_NAME-${GUI_VERSION}-${GUI_RELEASE}.tar ${GUI_PREFIX}_checkin_gui.desktop
popd

pushd $PWD
echo "$PWD"
cd deployment
tar uf $CWD/$BUILDDIR/SOURCES/$GUI_NAME-${GUI_VERSION}-${GUI_RELEASE}.tar $GUI_IMAGE
popd

gzip $BUILDDIR/SOURCES/$GUI_NAME-${GUI_VERSION}-${GUI_RELEASE}.tar 

cp deployment/checkingui.spec $BUILDDIR/SPECS

rpmbuild --define "_topdir $(realpath BUILD)" -ba BUILD/SPECS/checkingui.spec
