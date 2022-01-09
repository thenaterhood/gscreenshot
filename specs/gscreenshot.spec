%define name gscreenshot
%define version 2.17.2
%define unmangled_version 2.17.2
%define release 1

Summary: A simple screenshot tool
Name: %{name}
Version: %{version}
Release: %{release}
Source0: https://github.com/thenaterhood/gscreenshot/archive/v%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
BuildRequires: python3 python3-setuptools gettext
Requires: scrot python3 python3-pillow python3-gobject python3-setuptools python3-xlib
Vendor: Nate Levesque <public@thenaterhood.com>
Url: https://github.com/thenaterhood/gscreenshot

%description
A graphical and CLI screenshot utility.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
