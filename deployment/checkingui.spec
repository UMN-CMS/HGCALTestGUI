%define version %{getenv:GUI_VERSION}
%define release %{getenv:GUI_RELEASE}
Name:       %{getenv:GUI_NAME}

Version:	%{version}
Release:	%{release}

Summary:        HGCAL Checkin GUI
BuildArch:      x86_64

License:       GPL
Source0:       %{getenv:GUI_NAME}-%{version}-%{release}.tar.gz

Requires:      python3 zebra-scanner-corescanner 
BuildRequires: zebra-scanner-corescanner, zebra-scanner-devel

%description
Checkin GUI

%prep
%setup -q -n %{getenv:GUI_NAME}-%{version}-%{release} -c

%build
cd %{getenv:GUI_NAME}/PythonFiles/Scanner
make clean
make

%install
mkdir -p $RPM_BUILD_ROOT/opt
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/%{getenv:GUI_NAME}
cp -r %{getenv:GUI_NAME} $RPM_BUILD_ROOT/opt
cp %{getenv:GUI_PREFIX}_checkin_gui $RPM_BUILD_ROOT/%{_bindir}
cp %{getenv:GUI_PREFIX}_checkin_gui.desktop $RPM_BUILD_ROOT/%{_datadir}/applications
cp %{getenv:GUI_IMAGE} $RPM_BUILD_ROOT/%{_datadir}/%{getenv:GUI_NAME}
cd $RPM_BUILD_ROOT/opt/%{getenv:GUI_NAME}

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/%{getenv:GUI_NAME}
%{_bindir}/%{getenv:GUI_PREFIX}_checkin_gui
%{_datadir}/applications/%{getenv:GUI_PREFIX}_checkin_gui.desktop
%{_datadir}/%{getenv:GUI_NAME}/
