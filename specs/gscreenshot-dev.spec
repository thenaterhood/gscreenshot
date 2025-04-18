%define name gscreenshot
%define version 999
%define unmangled_version 999
%define release 1

Summary: A simple screenshot tool
Name: %{name}
Version: %{version}
Release: %{release}
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch

Requires: scrot python3 python3-pillow python3-gobject python3-setuptools python3-xlib
Vendor: Nate Levesque <public@thenaterhood.com>
Url: https://github.com/thenaterhood/gscreenshot

%description
A graphical and CLI screenshot utility.

%if 0%{?fedora} >= 34 || 0%{?is_opensuse} || 0%{?centos_ver} == 8
  echo "pandoc"
%endif

%prep

%setup -q -c -T
cp -a %{_sourcedir}/* .

%build
python -m build --wheel --no-isolation

%install
python -m installer --destdir="$pkgdir/" dist/*.whl

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
