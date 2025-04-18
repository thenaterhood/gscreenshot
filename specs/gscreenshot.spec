%define name gscreenshot
%define version 3.9.2
%define unmangled_version 3.9.2
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
BuildRequires: python3
BuildRequires: python3-setuptools
BuildRequires: gettext
BuildRequires: pandoc
Requires: scrot python3 python3-pillow python3-gobject python3-setuptools python3-xlib
Vendor: Nate Levesque <public@thenaterhood.com>
Url: https://github.com/thenaterhood/gscreenshot

%description
A graphical and CLI screenshot utility.

%generate_buildrequires
echo "python3"
echo "python3-setuptools"
echo "gettext"
echo "python3-build"
echo "python3-installer"
echo "python3-wheel"
echo "pandoc"

%if 0%{?fedora} >= 34 || 0%{?is_opensuse} || 0%{?centos_ver} == 8
  echo "pandoc"
%endif

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python -m build --wheel --no-isolation

%install
python -m installer --destdir="%{buildroot}/" dist/*.whl
find %{buildroot} -type f -or -type l | sed -e s"|%{buildroot}||g" > INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
