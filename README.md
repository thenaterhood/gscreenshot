# gscreenshot

[![Code Climate](https://codeclimate.com/github/thenaterhood/gscreenshot/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/gscreenshot)
[![Code Health](https://landscape.io/github/thenaterhood/gscreenshot/master/landscape.svg?style=flat)](https://landscape.io/github/thenaterhood/gscreenshot/master)

[Available in the Archlinux User Repository](https://aur.archlinux.org/packages/gscreenshot/)

gscreenshot is a gtk frontend for scrot, an application for taking screenshots,
written in python and pygtk. This is a fork of the original project (last
updated in 2006) that updates it to use modern technologies and to provide
updated functionality.

This application was originally written by matej.horvath. The original project
can be found at https://code.google.com/p/gscreenshot/ while Google Code is
still up and running.

gscreenshot is licensed under the GPL.

## Usage
gscreenshot takes screenshots! Run it manually or bind it to a keystroke.

Buttons

* "Selection" allows you to drag-select an area to screenshot
* "Window" allows you to click a window to screenshot
* "All" takes a screenshot of the entire screen.
* "Save" brings up the file save dialog to save your screenshot

Keyboard shortcuts

* Control+S opens the save dialog
* Control+C copies the screenshot to the clipboard
* Escape quits the application

## Requirements
* Python 3
* Scrot
* python-pillow
* python-gobject
* Setuptools

## Development Requirements
The above, plus:
* Glade

## Installation
* Run the included setup.py script: `sudo python setup.py install`

