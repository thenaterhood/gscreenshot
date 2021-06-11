# gscreenshot

[![Code Climate](https://codeclimate.com/github/thenaterhood/gscreenshot/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/gscreenshot)


gscreenshot is a gtk frontend for scrot, an application for taking screenshots,
written in python and pygtk. This is a fork of the original project (last
updated in 2006) that updates it to use modern technologies and to provide
updated functionality.

This application was originally written by matej.horvath. The original project
can be found at https://code.google.com/p/gscreenshot/ while Google Code is
still up and running.

gscreenshot is licensed under the GPLv2.

## Installation

### Requirements
_automatically installed by the setup script or your package manager_

**These requirements:**
* Python 2.7 or Python 3
* python-pillow
* python-gobject (may be called "python-gi" or "python3-gi")
* Setuptools
* gettext
* Your choice of a combination of the utilities listed in the following sections:

**Recommended Setup for X11:**
* Scrot (screenshot backend)
* Slop (region selection + cursor capture)
* xdg-open (for opening screenshots in your image viewer - optional)
* xclip (for command line clipboard functionality - optional)

**Alternative setups for X11, in order of recommendation:**
* ImageMagick + slop + python-xlib (full functionality)
* Imlib2_grab + slop + python-xlib (full functionality)
* PIL/python-pillow + slop + python-xlip (full functionality)
* Scrot (cursor capture will not work in some scenarios, region selection may be glitchy due to scrot issues)
* PIL/python-pillow + slop (no cursor capture)
* ImageMagick (no cursor capture)
* Imlib2_grab (no cursor capture)
* ImageMagick + slop (no cursor capture)
* Imlib2_grab + slop (no cursor capture)
* PIL/python-pillow only (no region selection or cursor capture)

**Setup for Wayland:**
Wayland support is very limited, but available - your mileage will vary depending on
how your system is configured and what desktop environment you're using.
* grim (for screenshots)
* slurp (for region selection)
* xdg-open (for opening screenshots in your image viewer - optional)

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
   - `sudo python setup.py install --single-version-externally-managed` - install systemwide
     - If this fails, exclude the `--single-version-externally-managed` flag -
       but you'll need to manually install icons and menu entries
   - `python setup.py install --user --single-version-externally-managed` - install to the current user
     (binary at ~/.local/bin/gscreenshot). See the previous note about `--single-version-externally-managed`
   - you can also install with `sudo pip install -e .` but this won't install pixmaps or menu entries

Building a package:

Generally, running one of the setup.py calls above with the --root parameter
should work fine for building a packageable version.

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

