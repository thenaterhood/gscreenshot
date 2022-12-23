% GSCREENSHOT(1)

# NAME

gscreenshot - screenshot frontend (CLI and GUI) for a variety of screenshot backends.

# SYNOPSIS

gscreenshot [-cosnp] [-f FILENAME] [-d DELAY] [--help] [-V --version]

gscreenshot-cli [-cosnp] [-f FILENAME] [-d DELAY] [--help] [-V --version]

# DESCRIPTION

gscreenshot provides a common frontend and expanded functionality to a number of X11 and Wayland utilties:

screenshot backends, including:

- scrot
- imagemagick
- grim
- xdg-desktop-portal
- PIL
- imlib2

region selection utilities, including:

- slurp
- slop

gscreenshot will automatically determine which utilities are available and which are the best for your situation.
Different combinations may require installing different dependencies. gscreenshot will automatically degrade
functionality as needed if dependencies are missing.

In a nutshell, gscreenshot supports the following (depending on your configuration):

- Capturing a full-screen screenshot
- Capturing a region of the screen interactively
- Capturing a window interactively
- Capturing the cursor
- Capturing the cursor, using an alternate cursor glyph
- Capturing a screenshot with a delay
- Showing a notification when a screenshot is taken
- Capturing a screenshot from the command line or a custom script
- Capturing a screenshot using a GUI
- Saving to a variety of image formats including 'bmp', 'eps', 'gif', 'jpeg', 'pcx',
    'pdf', 'ppm', 'tiff', 'png', and 'webp'.
- Copying a screenshot to the system clipboard
- Opening a screenshot in the configured application after capture

Other than region selection, gscreenshot's CLI is non-interactive and is suitable for use in scripts.

# OPTIONS

-h, \--help
:   Show the built-in help text

-d *DELAY*, \--delay *DELAY*
:   A numeric value in seconds to wait before taking the screenshot. Defaults to 0 (no delay).

-f *FILENAME*, \--filename *FILENAME*
:   A filename to store the screenshot to once taken.

    Defaults to gscreenshot_%Y-%m-%d-%H%M%S.png.

    Two types of format parameters are accepted:

    * $$: A literal $
    * $a: The system hostname
    * $h: The height of the screenshot in pixels
    * $p: The size of the screenshot in pixels
    * $w: The width of the screenshot in pixels

    * %%: A literal %
    * The full list of strftime format options in their standard format. See the examples section.

-c, \--clip
:   Copy the resulting screenshot to the clipboard. Relies on xclip or wl-clipboard.

-o, \--open
:   Pass the resulting screenshot to xdg-open to open it in the configured utility for the file type.

-s, \--selection
:   Use a region selection utility to select a region of the screen to capture (if available).

-V, \--version
:   Display the version, supported features, and additional relevant information.

-n, \--notify
:   Show a notification when the screenshot is taken. Gscreenshot will automatically show a notification
    if a screenshot is taken from a different session, so some situations may not need this option.
    Requires notify-send and a working configuration.

-p, \--pointer
:   Capture the cursor, if supported.

# EXAMPLES

gscreenshot
:   Open the gscreenshot GUI.

gscreenshot -f \'screenshot_\$hx\$w_%Y-%m-%d.png\' -s -c -d 1
:   Take a screenshot of a screen region (interactive) without the GUI, with a 1 second delay. Copy the
    screenshot to the clipboard and save it to a PNG file including the height, width, and day in the filename.
    Note that you can subsitute gscreenshot-cli for gscreenshot in this call, if so desired.

gscreenshot-cli
:   Take and save a screenshot to the current directory with default parameters, without starting the GUI.

# GRAPHICAL USER INTERFACE

Invoke gscreenshot with no parameters to open the graphical user interface.

## Buttons and Checkboxes

"Selection"
:   Allows you to drag-select an area to capture.

"Window"
:   Allows you to click a window to screenshot. On some setups this may be equivalent to "Selection".

"Everything"
:   Takes a screenshot of the entire screen.

"Overwrite"
:   Overwrites the screenshot displayed in the preview. Uncheck this box to take several screenshots.
    You can save multiple screenshots to a folder with the "Save All" option in the dropdown and right
    click menu.

"Hide gscreenshot"
:   Uncheck this to include gscreenshot's graphical user interface in your screenshot, or to simply
    leave the gscreenshot GUI visible while you select a different region of the screen.

"Capture Cursor"
:   Include the mouse cursor in the screenshot, if supported. Selecting this option will, if supported,
    reveal a menu where you can choose an alternate cursor glyph to use in the screenshot.

"About"
:   Show information about gscreenshot.

"Save As"
:   Brings up the file save dialog to save the screenshot shown in the preview to a file.
    When setting a filename, you can use the same format parameters as supported by the `-f`
    command line option.

Save As dropdown (and right click menu):
:   Open extended options.


## Menu Options

"Copy"
:   Copy the displayed screenshot to the clipboard.

"Open"
:   Open the displayed screenshot in the configured utility for the file type and close gscreenshot.

"Copy and Close"
:   Copy the displayed screenshot to the clipboard and remove it from gscreenshot (closing gscreenshot
    if it's the last or only screenshot).

"Open With"
:   Choose a program to open the displayed screenshot in and close gscreenshot.

"Save All"
:   Choose or create a folder to save all the screenshots available in the preview into.
    When setting a folder name, you can use the same format parameters as supported by the `-f`
    command line option.

## Keyboard Shortcuts

Control+S
:   Opens the save dialog

Control+C
:   Copies the screenshot to the clipboard

Control+O
:   Opens your screenshot in your default image application

Control+X
:   Copies the displayed screenshot to the clipboard and removes it from gscreenshot

Left Arrow
:   Moves the preview to the previous screenshot from the session, if one exists

Right Arrow
:   Moves the preview to the next screenshot from the session, if one exists

INSERT
:   Toggles Overwrite mode

Escape
:   Quits the application

# INSTALLATION

Check your package manager or user contributed repositories first. gscreenshot may already
be available. If not, or if you want a more customized install, continue.

gscreenshot supports a number of system configurations. gscreenshot requires
the following, which should be available (or already installed by) your package manager:

* Python 3.5 or newer
* python-pillow
* python-gobject (may be called "python-gi" or "python3-gi")
* Setuptools
* gettext

At this point, you can install gscreenshot itself by running
"sudo pip install -e ."

## For full functionality on X11, the recommended packages are:

* Scrot 1.0 or newer (screenshot backend)
* Slop (region selection + cursor capture)
* xdg-open (for opening screenshots in your image viewer)
* xclip (for command line clipboard functionality)

## For alternate X11 configurations, choose from one of the following combinations:

* Scrot (1.0 or older) + slop + python-xlib
* ImageMagick + slop + python-xlib
* Imlib2_grab + slop + python-xlib
* xdg-desktop-portal + slop + python-xlib + python-dbus
* PIL/python-pillow + slop + python-xlib
* Scrot only (any version) (cursor capture will not work in some scenarios, region selection may be glitchy due to scrot issues)

## For full functionality on Wayland, the recommended packages are:

* grim (for screenshots)
* slurp (for region selection)
* xdg-open (for opening screenshots in your image viewer)
* wl-clipboard (for copy to clipboard)

## For alternate Wayland configurations, choose from one of the following combinations:

* xdg-desktop-portal + slurp + python-dbus

You can install X11 and Wayland package configurations in parallel - gscreenshot will detect if your
session is Wayland or X11.

Note that Wayland support may be limited - your mileage may vary depending on your system's configuration.

If you intend to develop gscreenshot, you may also want to install Glade (GTK designer) and pandoc
(for generating the manpage).

If you install manually, you may also want to install the data files by hand, which includes
the manpage, .desktop file, and icons. You can find these in the "generated" directory.

# AUTHOR

This is a fork of the original gscreenshot project (last updated in 2006) that updates it
to use modern technologies and to provide updated functionality.

This application was originally written by matej.horvath. The original project
used to be be found at https://code.google.com/p/gscreenshot/.

gscreenshot is now maintained by Nate Levesque (thenaterhood).

# COPYRIGHT

gscreenshot is licensed under the GPLv2.

# CONTRIBUTING

## Contributing code

Please base pull requests off of and open pull requests against the
'dev' branch. 'main' is reserved for stable code. You may be asked to
rebase your code against the latest version of the 'dev' branch if
there's been a flurry of activity before your contribution.

## Localizations

gscreenshot uses the standard gettext tools. Locale files can be found in
src/gscreenshot/resources/locale.

If you contribute a localization, do not add the compiled .mo files. They
are generated on demand as part of the installation.

Current supported languages are:

* English
* Español

## Packaging

The following command should be suitable, with minor adjustments, for creating
a gscreenshot package.
python setup.py install --root="$pkgdir/" --optimize=1 --force --single-version-externally-managed

# SEE ALSO

https://github.com/thenaterhood/gscreenshot for source code and bug tracking.
