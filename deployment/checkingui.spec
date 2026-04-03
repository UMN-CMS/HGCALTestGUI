%define version %{getenv:GUI_VERSION}
%define release %{getenv:GUI_RELEASE}
Name:         HGCALCheckinGUI

Version:	%{version}
Release:	%{release}

Summary:        HGCAL Checkin GUI
BuildArch:      x86_64

License:       GPL
Source0:       HGCALCheckinGUI-%{version}-%{release}.tar.gz

Requires:      python3 zebra-scanner-corescanner 
BuildRequires: zebra-scanner-corescanner, zebra-scanner-devel

%description
HGCAL Checkin GUI Build

%prep
%setup -q -n HGCALCheckinGUI-%{version}-%{release} -c

%build
cd HGCALCheckinGUI/PythonFiles/Scanner
make clean
make

%install
mkdir -p $RPM_BUILD_ROOT/opt
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/HGCALCheckinGUI
cp -r HGCALCheckinGUI $RPM_BUILD_ROOT/opt
cp hgcal_checkin_gui $RPM_BUILD_ROOT/%{_bindir}
cp hgcal_checkin_gui.desktop $RPM_BUILD_ROOT/%{_datadir}/applications
cp application_icon.png $RPM_BUILD_ROOT/%{_datadir}/HGCALCheckinGUI
cd $RPM_BUILD_ROOT/opt/HGCALCheckinGUI

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/HGCALCheckinGUI
%{_bindir}/hgcal_checkin_gui
%{_datadir}/applications/hgcal_checkin_gui.desktop
%{_datadir}/HGCALCheckinGUI/
