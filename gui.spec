%define version %{getenv:GUI_VERSION}
%define release %{getenv:GUI_RELEASE}
Name:         HGCALTestGUI

Version:	%{version}
Release:	%{release}

Summary:        HGCAL Testing GUI
BuildArch:      noarch

License:       GPL
Source0:       HGCALTestGUI-%{version}-%{release}.tar.gz

Requires:      python3

%description
HGCAL Test GUI Build

%prep
%setup -q -n HGCALTestGUI-%{version}-%{release} -c

%install
mkdir -p $RPM_BUILD_ROOT/opt
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALTestGUI
cp -r HGCALTestGUI $RPM_BUILD_ROOT/opt
cp Configs/LD_Engine_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALTestGUI/
cp Configs/HD_Engine_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALTestGUI/
cp Configs/LD_Wagon_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALTestGUI/
cp hgcal_test_gui $RPM_BUILD_ROOT/%{_bindir}
cd $RPM_BUILD_ROOT/opt/HGCALTestGUI

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/HGCALTestGUI
%{_sysconfdir}/HGCALTestGUI
%{_bindir}/hgcal_test_gui
