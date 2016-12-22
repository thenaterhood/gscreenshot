# gscreenshot

[![Code Climate](https://codeclimate.com/github/thenaterhood/gscreenshot/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/gscreenshot)
[![Code Health](https://landscape.io/github/thenaterhood/gscreenshot/master/landscape.svg?style=flat)](https://landscape.io/github/thenaterhood/gscreenshot/master)


gscreenshot is a gtk frontend for scrot, an application for taking screenshots,
written in python and pygtk. This is a fork of the original project (last
updated in 2006) that updates it to use modern technologies and to provide
updated functionality.

This application was originally written by matej.horvath. The original project
can be found at https://code.google.com/p/gscreenshot/ while Google Code is
still up and running.

gscreenshot is licensed under the GPL.

## Installation

ArchLinux and derivatives:
[Available in the Archlinux User Repository](https://aur.archlinux.org/packages/gscreenshot/)

SparkyLinux:
Available in your distro's repositories. Run `sudo apt-get install gscreenshot`

Other distros:

1. Download the latest version from [here](https://github.com/thenaterhood/gscreenshot/releases/latest)
2. Unzip or untar the file (depending which you downloaded)
3. From the command line, navigate to the unzipped files and run
`sudo pip install -e .` NOTE: you *can* install gscreenshot by running
`sudo python setup.py install` but that method will not automatically handle
dependencies for you.

## Usage
gscreenshot takes screenshots! Run it manually or bind it to a keystroke. Both a graphical (gscreenshot) and CLI (gscreenshot-cli) interface are available.

### Command Line
Run `gscreenshot-cli --help` for instructions. The shell interface is
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
* Escape quits the application

## Contributing
Find a problem? Have something to add? Just think gscreenshot is super
cool? gscreenshot accepts contributions!

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

## Requirements
_automatically installed by the setup script or your package manager_

* Python 2.7 or Python 3
* Scrot
* python-pillow
* python-gobject
* Setuptools
* Slop (Optional; used for improved region and window selection)

## Development Requirements
The above, plus:
* Glade

