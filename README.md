# gscreenshot

[![Code Climate](https://codeclimate.com/github/thenaterhood/gscreenshot/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/gscreenshot)


gscreenshot is a GTK frontend for taking screenshots, with support for multiple
screenshot and region selection backends. Built in Python and pygtk, with Glade.

This is a fork of the original project (last updated in 2006) that updates it
to use modern technologies and to provide updated functionality.

This application was originally written by matej.horvath. The original project
can be found at https://code.google.com/p/gscreenshot/ while Google Code is
still up and running.

gscreenshot is licensed under the GPLv2.

## Installation

v2.20.0 is the last gscreenshot with support for Python versions older than
Python 3.5. Minor bugfixes will be accepted for patch releases if necessary.

v3.0.0 and newer is aimed at Python 3.5 and newer.

### Requirements
_automatically installed by the setup script or your package manager_

**These requirements:**
* Python 3.5 or newer
* python-pillow
* python-gobject (may be called "python-gi" or "python3-gi")
* Setuptools
* gettext
* Your choice of a combination of the utilities listed in the following sections:

**Recommended Setup for X11:**
* Scrot 1.0 or newer (screenshot backend)
* Slop (region selection + cursor capture)
* xdg-open (for opening screenshots in your image viewer - optional)
* xclip (for command line clipboard functionality - optional)

**Alternative setups for X11, in order of recommendation:**
* Scrot (1.0 or older) + slop + python-xlib
* ImageMagick + slop + python-xlib
* Imlib2_grab + slop + python-xlib
* xdg-desktop-portal + slop + python-xlib + python-dbus
* PIL/python-pillow + slop + python-xlib
* Scrot only (any version) (cursor capture will not work in some scenarios, region selection may be glitchy due to scrot issues)

**Setup for Wayland:**
Wayland support is very limited, but available - your mileage will vary depending on
how your system is configured and what desktop environment you're using.
* grim (for screenshots)
* slurp (for region selection)
* xdg-open (for opening screenshots in your image viewer - optional)
* wl-clipboard (for copy to clipboard - optional)

**Alternative setups for Wayland, in order of recommendation:**
* xdg-desktop-portal + slurp + python-dbus

gscreenshot will automatically detect X11 versus Wayland and what utilities you have
available on your system. It will use them in the order of its preference.

Aside from the requirements, you can mix and match utilities. gscreenshot will gracefully degrade
its functionality if utilities are missing or if they have limitations.

### Development Requirements
The above, plus:
* Glade

### How to Install
ArchLinux and derivatives:
[Available in the AUR](https://aur.archlinux.org/packages/gscreenshot/)

Fedora/Mageia/OpenSUSE:
[Available in COPR](https://copr.fedorainfracloud.org/coprs/thenaterhood/gscreenshot/)

SparkyLinux:
Available in your distro's repositories. Run `sudo apt-get install gscreenshot`

Manual installation:

1. Download the latest version from [here](https://github.com/thenaterhood/gscreenshot/releases/latest)
2. Unzip or untar the file (depending which you downloaded)
3. From the command line, navigate to the unzipped files and run one of the following:
   - Install systemwide with `sudo pip install -e .`

Building a package:

The following command should work for building a package:
python setup.py install --root="$pkgdir/" --optimize=1 --force --single-version-externally-managed

gscreenshot automatically retrieves its version number from specs/gscreenshot.spec
and setup.py should generate appropriate menu entries and binaries.

## Usage
gscreenshot takes screenshots! Run it manually or bind it to a keystroke.
Both a graphical (gscreenshot) and CLI (gscreenshot-cli) interface are available.

### Command Line
Run `gscreenshot --help` for instructions. The shell interface is
non-interactive so it is suitable for use in scripts and pre-built
calls.

### Graphical

Buttons

* "Selection" allows you to drag-select an area to screenshot
* "Window" allows you to click a window to screenshot
* "Everything" takes a screenshot of the entire screen.
* "Save" brings up the file save dialog to save your screenshot

Keyboard shortcuts

* Control+S opens the save dialog
* Control+C copies the screenshot to the clipboard
* Control+O opens your screenshot in your default image application
* Escape quits the application

## Contributing
Find a problem? Have something to add? Just think gscreenshot is super
cool? gscreenshot accepts contributions!

### Localization
gscreenshot uses the standard gettext tools. Locale files can be found in
src/gscreenshot/resources/locale.

If you contribute a localization, do not add the compiled .mo files. They
are generated on demand as part of the installation.

Current supported languages are:
* English
* Español

### Contributing Code
Please base pull requests off of and open pull requests against the
'dev' branch. 'master' is reserved for stable code. You may be asked to
rebase your code against the latest version of the 'dev' branch if
there's been a flurry of activity before your contribution.

Pull requests may not be merged right away! Don't take offense,
sometimes it just takes a little while to get to them.

### Opening Issues
Don't worry about categorizing your issue properly, it'll get taken
care of on this end.

