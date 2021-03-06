# gditools3
![gditools3](screenshots/screenshot001win_small.png)

gditools3 is a fork of of https://sourceforge.net/projects/dcisotools/

This Python program/library is designed to handle GD-ROM image (GDI) files. It can be used to list files, extract data, generate sorttxt file, extract bootstrap (IP.BIN) file and more.

This project can be used in standalone mode, in interactive mode or as a library in another Python program (check the 'addons' folder to learn how).

You can use either the command-line interface (gditools3.py, for Python 2 or 3) or the GUI (gditools3gui.py, for Python 3 only).

This project was (barely!) tested with Python 2.7, 3.4 and 3.7.

See the README.TXT file for more informations.

Features
 - List and extract files from a GDI dump of a Dreamcast Gigabyte disc (GD-ROM)
 - Extract the bootsector (IP.BIN) of a GDI dump
 - Generate a sorttxt.txt of the files in a GDI dump
 - Transparent support for 2048 (iso) or 2352 (bin) data track format
 - Preserve the timestamp of extracted files
 - Usable as a library providing other programs with GDI-related functions
 - Python GUI (courtesy of [PySimpleGUI](https://github.com/MikeTheWatchGuy/PySimpleGUI)) with preview of text and image files and media playback via external player
