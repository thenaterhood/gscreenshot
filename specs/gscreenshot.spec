%define name gscreenshot
%define version 3.10.0
%define unmangled_version 3.10.0
%define release 1

Summary: A simple screenshot tool
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
License: GPLv2
Source0: https://github.com/thenaterhood/gscreenshot/archive/v%{version}.tar.gz
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch

# Common BuildRequires for all distributions
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-pip
BuildRequires: gettext

# Handle Python build and installer modules
%if 0%{?fedora} >= 33 || 0%{?suse_version} >= 1550 || 0%{?centos} >= 999
BuildRequires: python3-build
BuildRequires: python3-installer
BuildRequires: python3-wheel
%else
BuildRequires: python3-pip
BuildRequires: python3-wheel
%endif

%if 0%{?fedora} >= 34 || 0%{?is_opensuse} || 0%{?centos} >= 999
# For systems that have pandoc available
BuildRequires: pandoc
%endif

# Distribution-specific dependencies
%if 0%{?fedora} || 0%{?rhel} >= 8 || 0%{?centos} >= 8 || 0%{?mageia}
Requires: scrot python3 python3-pillow python3-gobject python3-xlib python3-setuptools
%endif

%if 0%{?suse_version}
Requires: scrot python3 python3-Pillow python3-gobject python3-xlib python3-setuptools
%endif

Vendor: Nate Levesque <public@thenaterhood.com>
Url: https://github.com/thenaterhood/gscreenshot

%description
A graphical and CLI screenshot utility.

%prep
%setup -n %{name}-%{unmangled_version}

%build

%if 0%{?rhel} == 8
  python3 setup.py bdist_wheel
%else
  if python3 -m build --help >/dev/null 2>&1 && python3 -m wheel --help >/dev/null 2>&1; then
    python3 -m build --wheel --no-isolation
  else
    python3 -m pip install --user build wheel
    python3 -m build --wheel --no-isolation
  fi
%endif

%install

%if 0%{?rhel} == 8
  python3 -m pip install --ignore-installed --root=%{buildroot} --prefix=%{_prefix} --no-deps $(ls dist/*.whl 2>/dev/null || echo "")
%else
  # Use installer if available, otherwise install via pip
  if python3 -m installer --help >/dev/null 2>&1; then
      python3 -m installer --destdir=%{buildroot} dist/*.whl
  else
      python3 -m pip install --user installer
      python3 -m installer --destdir=%{buildroot} dist/*.whl
  fi
%endif

echo "Contents of buildroot:"
find %{buildroot} -type f | sort

# Generate list of installed files
find %{buildroot} -type f -or -type l | sed "s|^%{buildroot}||" > INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)