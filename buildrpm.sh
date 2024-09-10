shopt -s globstar

: ${BUILDDIR:=BUILD}
: ${GUI_VERSION:=0.0.1}
: ${GUI_RELEASE:=NORELEASE}

CWD=$PWD
BNAME=$(basename $CWD)

rm -fr "$BUILDDIR"
mkdir -p "${BUILDDIR}"/{RPMS,SOURCES,SPECS,SRPMS,BUILD}

rm -rf HGCALTestGUI
mkdir HGCALTestGUI
cp __main__.py HGCALTestGUI
cp -r PythonFiles HGCALTestGUI 
cp -r awthemes-10.4.0 HGCALTestGUI 

for f in HGCALTestGUI/**/*.py; do
    sed -i '1,1{/^#!/d}' "$f"
done

tar cf \
    $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar \
    -X $CWD/.gitignore \
    HGCALTestGUI/PythonFiles \
    HGCALTestGUI/__main__.py \
    HGCALTestGUI/awthemes-10.4.0

tar uf $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar Configs
tar uf $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar requirements.txt

tmp=$(mktemp -d)
pushd $PWD
cd $tmp
cat <<EOF > hgcal_test_gui
#!/usr/bin/env bash

DEFAULT_CONFIG_PATH="/etc/HGCALTestGUI/active.yaml"
if [[ -e \$DEFAULT_CONFIG_PATH ]]; then
   CONFIGFILE="\$DEFAULT_CONFIG_PATH"
else
   CONFIGFILE="/etc/HGCALTestGUI/\$1_cfg.yaml"
fi
python3 /opt/HGCALTestGUI/__main__.py "\$CONFIGFILE"

EOF
chmod a+x hgcal_test_gui
tar uf $CWD/$BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar hgcal_test_gui
popd

gzip $BUILDDIR/SOURCES/HGCALTestGUI-${GUI_VERSION}-${GUI_RELEASE}.tar 

cp gui.spec $BUILDDIR/SPECS





rpmbuild --define "_topdir $(realpath BUILD)" -ba BUILD/SPECS/gui.spec

