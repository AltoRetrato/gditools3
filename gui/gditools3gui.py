#!/usr/bin/python3
# -*- coding: utf-8 -*-
# By Ricardo Mendonça Ferreira - ric@mpcnet.com.br - GNU GPL v3

# 2018.11.04  0.0.1  First release
# 2018.10.25  0.0.0  Creating 1st version, GNU GPL v3

# TO-DO:
# - test everything (inc. on Python 2x/3x, Win/Linux)
# - test with other images
# - compare & enhance performance, compared to original gditools (Python 2)
# - add dropdown box for encoding (to see Japanese text in .ini, etc.)

# Bugs / problems / to-do:
# - can't preview jpeg, pvr, animated GIFs & others
# - can't have canvas for image preview with scrollbars
# - can't open AFS (or ZIP, or other) packages (could implement this on a second window?)
# - sg.Tree:
#       - doesn't support [Home], [End], [Ctrl+A], ...
#       - #585 no way to set currently visible or selected elements (so I can implement the keyboard shortcuts above)

import os
import sys
import json
import base64
import platform
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gditools3
import PySimpleGUI as sg
try:
   import winsound
except:
   winsound = None


# Misc. global variables

__version__ = "0.0.1"

prvSize  = ( 74,  10) # size of hex   preview panel in "chars", "rows"
imgSize  = (512, 286) # size of image preview panel in pixels - (586, 440)
emptyGIF = b'R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICTAEAOw==\n' # 1x1 px
icon     = "gditools64.ico"

asciiPreviewLimit =   4*1024 # max. no. of bytes to load/display for previewing
hexPreviewLimit   = 150*1024 # max. no. of bytes to load/display for previewing
previewLimit      = max(asciiPreviewLimit, hexPreviewLimit)

asciiExt = set(["htm", "html", "ini", "txt", "dps"])
imgExt   = set(["gif", "png", "jpg", "bmp", "pvr"])
audioExt = set(["adx", "wav", "mp3"])
videoExt = set(["avi", "wmv"])

gdiFiles = (("GDI files", "*.gdi"),("All files", "*.*"))
if platform.system() == "Windows":
      exeFiles = (("Executable files", "*.exe *.cmd *.bat"),("All files", "*.*"))
else: exeFiles = (("All files", "*.*"),)


class Options:
    def __init__(self, filename="options.json"):
        self.filename = filename
        self.value    = self.load()

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except:
            return {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(self.value, indent=2, sort_keys=True))

    def get(self, key, default=None):
        return self.value.get(key, default)

    def set(self, key, value):
        self.value[key] = value


def openGDI(fn):
    gdi      = None
    treedata = sg.TreeData()
    fileList = set()

    # Read list of files from GDI image
    if fn and os.path.exists(fn):
        gdi  = gditools3.GDIfile(fn, verbose=False)
        data = gdi._sorted_records(crit="name")[::-1]
        #files = list(gdi.tree())

        treedata.Insert("", '/', '/', [])
        for entry in data:
            name = entry["name"  ]               # "/0GDTEX.PVR"
            size = entry["ex_len"]               # 3147776
            when = gdi.get_time_by_record(entry) # '2000-11-08 11:18:20 (localtime)'
            if name == "/": continue
            parent, value = name.rsplit("/", 1)
            key = parent + "/" + value
            if parent == "": 
               parent = "/"
            if parent not in treedata.tree_dict:
                # Insert each and all necessary parent folders for this file, e.g., /1/2/3/4:
                # parent is /,    folder is /1
                # parent is /1,   folder is /1/2
                # parent is /1/2, folder is /1/2/3 ...
                folders = parent.split("/")[1:]
                grandparent = "/"
                child = ""
                for folder in folders:
                    child += "/"+folder
                    if child not in treedata.tree_dict:
                        #print("{} >> parent {} | key {} | value {}".format(parent, grandparent, child, child))
                        treedata.Insert(grandparent, child, folder, [])
                    grandparent = child
            #print("{} | {} | {}".format(parent, key, value))
            treedata.Insert(parent, key, value, [format("{:,}".format(int(size)))])
            fileList.add(key)
    return gdi, treedata, fileList


def setStatus(msg):
    window.FindElement("statusBar").Update(msg)
    window.Refresh()

PREVIEW_TEXT = sg.WRITE_ONLY_KEY + 'previewText'

def createWindow(treedata, img=None):
    status = 'Welcome to gditools3gui {} (using gditools3 {})\nSelect a GDI disc image to explore; Select files to preview and [Dump].'.format(
       __version__,
       gditools3.__version__,
    )
    menu = [
        ['&File',    ['E&xit'  ]],
       #['&Options', ["Set media player path"]], # see set_mediaPlayer_path
        ['&Help',    ['&Help', '&Limitations', '&About']],
    ] 
    layout = [
        [sg.Menu(menu)],
        [sg.Text('Disc Image',   size=(11, 1), auto_size_text=False, justification='right'), sg.InputText(options.get("gdiPath", ""),        do_not_clear=True, size=(80,1), key="gdiPath",         change_submits=True), sg.FileBrowse(file_types=gdiFiles)],
        [sg.Text('Output Path',  size=(11, 1), auto_size_text=False, justification='right'), sg.InputText(options.get("outputPath",""),      do_not_clear=True, size=(80,1), key="outputPath",      change_submits=True), sg.FolderBrowse()],
        [sg.Text('Media Player', size=(11, 1), auto_size_text=False, justification='right'), sg.InputText(options.get("mediaPlayerPath",""), do_not_clear=True, size=(80,1), key="mediaPlayerPath", change_submits=True), sg.FileBrowse(file_types=exeFiles)],
        [sg.Frame('Files', [
                [sg.Tree(data=treedata, headings=["size"], auto_size_columns=True, num_rows=22, col0_width=25, key="tree", change_submits=True)]
            ]),
            sg.Frame('Preview', [
                [sg.Radio('auto', 'previewMode', default=True, change_submits=True, key="previewModeAuto"), 
                 sg.Radio('hex',  'previewMode',               change_submits=True, key="previewModeHex"), 
                 sg.Radio('ascii','previewMode',               change_submits=True, key="previewModeAscii")],
                [sg.Multiline(do_not_clear=True, size=prvSize, default_text='', key=PREVIEW_TEXT, font=("Courier",8) )], 
                [sg.Image(data=img, key='previewImage', size=imgSize)],
            ])
        ],
        [sg.RButton('Play Selected'),
         sg.RButton('Dump Selected'),
         sg.RButton('Dump IP.BIN'),
         sg.RButton('Dump sorttxt'),
         sg.RButton('Dump All'),
         sg.Quit()],
        [sg.Text(status, size=(90, 2), key='statusBar')],
    ]
    window = sg.Window(
        'gditools3gui {}'.format(__version__), # window title
        return_keyboard_events = False,     # (better set to False for performance)
        use_default_focus      = False,
        icon                   = icon,
    ).Layout(layout)
    return window


def asciiView(textField, fileData, previewLimit=None):
    if previewLimit:
          previewData = fileData[:previewLimit]
    else: previewData = fileData
    if len(previewData) < len(fileData):
        previewData += '\n\n[showing only {:,} bytes]'.format(previewLimit).encode()
    textField.Update(previewData)


def hexView(textField, fileData, previewLimit=None, width=16):
    rows  = []
    bytesToDisplay = min(previewLimit or len(fileData), len(fileData))
    for addr in range(0, bytesToDisplay, width):
        data = fileData[addr:addr+width]
        hex_ = []
        asc  = []
        for j in range(min(width, len(data))):
            hex_.append("{:02X}".format(data[j]))
            asc.append(chr(data[j]) if 33 <= data[j] <= 126 else ".")
        hex_ = " ".join(hex_)
        asc  = "".join(asc)
        row  = "{:06X}| {:47} {}".format(addr, hex_, asc)
        rows.append(row)
    if previewLimit and bytesToDisplay == previewLimit:
        rows.append('\n[showing only {:,} bytes]'.format(previewLimit))
    textField.Update("\n".join(rows))


def play(fileName):
    player   = options.get("mediaPlayerPath")
    fileExt  = fileName.partition(".")[2].lower()
    fileData = b''
    
    # Do we have the player path correctly set?
    if not player:
        setStatus("Please set the path to media player (ffplay, vlc, ...) before playing a file.")
    elif not os.path.exists(player):
        setStatus("Could not find media player at {}".format(player))
    else:
        # Validate file type
        if (fileExt not in audioExt and 
            fileExt not in videoExt):
                setStatus("Sorry, but I'm not sure I can play .{} files.".format(fileExt))
                return
        # Save file
        setStatus("Dumping {}, please wait...".format(fileName))
        try:
            fileData    = gdi.get_file(fileName)
            tmpFileName = "$$$"+fileName.split("/")[-1]
            with open(tmpFileName, "wb") as fh:
                fh.write(fileData)
        except Exception as e:
            setStatus("Exception reading {}: {}".format(fileName, e))
            return

        # Play file
        setStatus("Playing {}".format(fileName))
        subprocess.run([player, tmpFileName])
        os.remove(tmpFileName)
        setStatus("")


def filePreview(fileName, window, values):
    textField  = window.FindElement(PREVIEW_TEXT)
    imageField = window.FindElement("previewImage")
    fileExt    = fileName.partition(".")[2].lower()
    fileData   = b''

    # Reading long files for previewing can make the GUI sluggish.
    # Read only what we need to preview!
    if fileExt in asciiExt or fileExt in imgExt:
          limit = None         # read full file if it is text or image
    else: limit = previewLimit # limit reading for all other file types

    setStatus("Previewing {}".format(fileName))
    try:
        fileData = gdi.get_file(fileName, length=limit) 
    except Exception as e:
        setStatus("Exception reading {}: {}".format(fileName, e))
        return

    # Which preview mode should we use?
    hexMode = True
    if values["previewModeAuto"]:
        if fileExt in asciiExt:
            hexMode = False
    elif values["previewModeAscii"]:
        hexMode = False
    
    # Preview text in ASCII or hex view mode
    if not hexMode:
          asciiView(textField, fileData, previewLimit=asciiPreviewLimit)
    else:   hexView(textField, fileData, previewLimit=hexPreviewLimit, width=16)
    
    # Preview image
    if fileExt in imgExt:
        # Convert image to GIF or PNG if its format is not supported by Tk
        if fileExt in set(["jpg", "pvr"]):
            # TO-DO: DO CONVERSION HERE!
            pass
        previewData = base64.encodebytes(fileData)
        imageField.Update(data=previewData, size=imgSize)
    else:
        imageField.Update(data=emptyGIF, size=imgSize)
    
    # Could also preview video & audio files, including GUI controls.
    # Feel free to implement it! :D


def popUp(msg, sound="SystemAsterisk"):
    if winsound and sound:
        winsound.PlaySound(sound, winsound.SND_ASYNC)
    setStatus(msg)
    sg.Popup(msg, icon = icon)


def dumpSelected(gdi, selected, outputPath, doPopup=True):
    if len(selected) == 0:
        setStatus("Please select one or more files to dump.")
    else:
        if len(selected) == 1:
              setStatus("Dumping {} to\n{}".format(selected[0], outputPath))
        else: setStatus("Dumping {} files to\n{}".format(len(selected), outputPath))

        for fn in selected:
            gdi.dump_file(fn, target=outputPath)
        if doPopup:
            if len(selected) == 1:
                  msg = "Dumped {} to\n{}".format(selected[0], outputPath)
            else: msg = "Dumped {} files to\n{}".format(len(selected), outputPath)
            popUp(msg)


def dumpIP_BIN(gdi, outputPath, doPopup=True):
    if not gdi:
        setStatus("Please open a disc image to dump its boot sector.")
    else:
        setStatus("Dumping IP.BIN, please wait...")
        fn = os.path.join(outputPath, "ip.bin")
        gdi.dump_bootsector(filename=fn)
        if doPopup:
            msg = "Dumped {}".format(fn)
            popUp(msg)


def dump_sorttxt(gdi, outputPath, doPopup=True):
    if not gdi:
        setStatus("Please open a disc image to dump a list of all files.")
    else:
        setStatus("Dumping list of files, please wait...")
        fn = os.path.join(outputPath, "sorttxt.txt")
        gdi.dump_sorttxt(fn, prefix="")
        if doPopup:
            msg = "Dumped {}".format(fn)
            popUp(msg)


def dumpAll(gdi, outputPath):
    if not gdi:
        setStatus("Please open a disc image before trying to dump all files.")
    else:
        setStatus("Dumping all files, please wait...")
        #dumpIP_BIN  (gdi, outputPath, doPopup=False)
        #dump_sorttxt(gdi, outputPath, doPopup=False)
        gdi.dump_all_files(target=outputPath)
        msg = "Dumped all files!"
        popUp(msg)



def set_mediaPlayer_path():
    # When you select a path in this file browser 
    # the main windows stops receiving events?
    pass
    #event, (fname,) = sg.Window('Select media player path').Layout(
    #    [
    #        [sg.Text('Please select media player path (ffplay, vlc, ...) for audio and video previews')],      
    #        [sg.In(), sg.FileBrowse()],
    #        [sg.CloseButton('Open'), sg.CloseButton('Cancel')]
    #    ]).Read()


def help():
    sg.Popup(
        'Help',
        'Use this tool to browse, preview and extract files from SEGA Gigabyte Disc (GD-ROM) dumps in gdi format.',
        'Select a "Disc Image" to browse its contents.',
        'Select the "Output Path" for file dumping.',
        'Select the full path to the "Media Player" of your choice (e.g., ffplay, vlc, ...) to play a selected video or audio file (such as .ADX).',
        '[Play Selected] plays selected file with media player.',
        '[Dump Selected] dumps selected file(s).',
        '[Dump IP.BIN] dumps image boot sector.',
        '[Dump sorttxt] dumps "sorttxt.txt", listing files as ordered in the image.',
       #'[Dump All] dumps all files in the disc image, plus IP.BIN and sorttxt.',
        '[Dump All] dumps all files in the disc image (except for IP.BIN & sorttxt).',
        '[Quit] closes the program.',
        icon = icon
    )


def limitations():
    sg.Popup(
        "Limitations",
        "This program is more a proof of concept than a full realization of my ideas.",
        "Curently it doesn't support previewing PVR, JPG and other image formats.",
        "It also can't open AFS packaged files.",
        "All this and more can be implemented in future versions.",
        "Feel free to fork the code and provide your contributions! :D",
        icon = icon
    )


def about():
    sg.Popup(
        'About',
        'This is a simple tool to browse, preview and extract files from SEGA Gigabyte Disc (GD-ROM) dumps in gdi format.',
        'gditools3gui v. {}, by Ricardo Mendonça Ferreira\n(inspired by "gditools.py GUI", from SiZiOUS).'.format(__version__),
        'gditools3 v. {}, by Ricardo Mendonça Ferreira\n(a Python 3 port from gditools by FamilyGuy).'.format(gditools3.__version__),
        'Python GUI framework by PySimpleGUI.',
        icon = icon
    )


if __name__ == "__main__":

    # Load options from file (if it exists)
    options = Options("gditools3gui.json")

    # Populate "tree" field with list of files in the GDI (or empty TreeData object)
    gdi, treedata, fileList = openGDI(options.get("gdiPath", ""))
    window = createWindow(treedata, img=emptyGIF)

    while True:
        event, values = window.Read()
        if event =='Quit' or event =='Exit' or event is None:      
            break
        # Save some form values into persistent options file
        for key in ("gdiPath", "outputPath", "mediaPlayerPath"):
            options.set(key, values[key])
            #window.FindElement(key).Update(values[key]) # workaround: re-set values cleared after .Read()
        if event == "gdiPath":
            # GDI file name has changed, so let's open it!
            gdi, treedata, fileList = openGDI(options.get("gdiPath", ""))
            setStatus("Loaded file {}".format(options.get("gdiPath", "")))
            window.FindElement("tree").Update(treedata)
        elif event == "outputPath":
            pass
        elif event == "mediaPlayerPath":
            pass
        elif event == "tree" or event == "hexView" or event.startswith("previewMode"):
            # 0, 1 or more files were selected in the tree,
            # or previewMode was toggled.
            selected = values["tree"]
            if len(selected) < 1:
                setStatus("")
            elif len(selected) > 1:
                setStatus("{} files selected. You can dump them or select a single file for preview.".format(len(selected)))
            else:
                fn = selected[0]
                if fn not in fileList:
                      setStatus("")
                else: filePreview(fn, window, values)
        elif event == "Play Selected":
            selected = values["tree"]
            if len(selected) != 1:
                  setStatus("Please select only one file to play.")
            else: play(selected[0])
        elif event == "Dump Selected":
            selected = values["tree"]
            # Could have selected file(s), folder(s) or both!
            # TO-DO: expand folders into files first!
            dumpSelected(gdi, selected, options.get("outputPath"))
        elif event == "Dump All"             : dumpAll(gdi, options.get("outputPath"))
        elif event == "Dump IP.BIN"          : dumpIP_BIN(gdi, options.get("outputPath"))
        elif event == "Dump sorttxt"         : dump_sorttxt(gdi, options.get("outputPath"))
        elif event == "Set media player path": set_mediaPlayer_path()
        elif event == "Help"                 : help()
        elif event == "Limitations"          : limitations()
        elif event == "About"                : about()
        else:
            #print("Event :", event)
            #print("Values:", values)
            pass

    options.save()
