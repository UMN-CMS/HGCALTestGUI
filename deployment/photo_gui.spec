%define version %{getenv:PHOTO_GUI_VERSION}
%define release %{getenv:PHOTO_GUI_RELEASE}
Name:         HGCALPhotoGUI

Version:	%{version}
Release:	%{release}

Summary:        HGCAL Photo GUI
BuildArch:      x86_64

License:       GPL
Source0:       HGCALPhotoGUI-%{version}-%{release}.tar.gz

Requires:      python3 zebra-scanner-corescanner 
# BuildRequires: zebra-scanner-corescanner, zebra-scanner-devel

%description
HGCAL Photo GUI Build

%prep
%setup -q -n HGCALPhotoGUI-%{version}-%{release} -c


%install
mkdir -p $RPM_BUILD_ROOT/opt
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/HGCALPhotoGUI
cp -r HGCALPhotoGUI $RPM_BUILD_ROOT/opt
cp Configs/LD_Engine_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI/
cp Configs/HD_Engine_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI/
cp Configs/HD_Wagon_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI/
cp Configs/LD_Wagon_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI/
cp Configs/Zipper_cfg.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/HGCALPhotoGUI/
cp hgcal_photo_gui $RPM_BUILD_ROOT/%{_bindir}
cp hgcal_photo_gui.desktop $RPM_BUILD_ROOT/%{_datadir}/applications
cp application_icon.png $RPM_BUILD_ROOT/%{_datadir}/HGCALPhotoGUI
cd $RPM_BUILD_ROOT/opt/HGCALPhotoGUI

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/HGCALPhotoGUI
%{_sysconfdir}/HGCALPhotoGUI/
%{_bindir}/hgcal_photo_gui
%{_datadir}/applications/hgcal_photo_gui.desktop
%{_datadir}/HGCALPhotoGUI/

%post
cd %{_datadir}/HGCALPhotoGUI/PythonFiles/Scanner
make clean
make
