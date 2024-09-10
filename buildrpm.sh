: ${BUILDDIR:=BUILD}
: ${GUI_VERSION:=0.0.1}
: ${GUI_RELEASE:=NORELEASE}

CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/{RPMS,SOURCES,SPECS,SRPMS,BUILD}
pushd $PWD
cd ..
tar cf $CWD/$BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar \
    $BNAME/PythonFiles $BNAME/__main__.py 

popd
tar uf $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar \
    Configs

tmp=$(mktemp -d)
pushd $PWD
cd $tmp
cat <<EOF > hgcal_test_gui
#!/usr/bin/env bash

DEFAULT_CONFIG_PATH="/etc/HGCALTestGUI/active.yaml"
if [[ -e \$DEFAULT_CONFIG_PATH ]]; then
   CONFIGFILE="\$DEFAULT_CONFIG_PATH"
else
   CONFIGFILE="/etc/HGCALTestGui/\$1_cfg.yaml"
fi
python3 /opt/HGCALTestGUI/__main__.py "\$CONFIGFILE"

EOF
chmod a+x hgcal_test_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar hgcal_test_gui
popd

gzip $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar 

cp gui.spec $BUILDDIR/SPECS



rpmbuild --define "_topdir $(realpath BUILD)" -ba BUILD/SPECS/gui.spec

