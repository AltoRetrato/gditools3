                                ___ __              __    
                     ____ _____/ (_) /_____  ____  / /____
                    / __ `/ __  / / __/ __ \/ __ \/ / ___/
                   / /_/ / /_/ / / /_/ /_/ / /_/ / (__  ) 
                   \__, /\__,_/_/\__/\____/\____/_/____/  
                  /____/

    gditools3, a Python library to extract files, sorttxt.txt and 
    bootsector (IP.BIN) from SEGA Gigabyte Disc (GD-ROM) dumps in 
    gdi format.

    The goals is to make it efficient, readable and multi-platform.

    As of 2018.20.15, it's tested & working on Win10 on Python 2.7.4
    and 3.4.1 on x86_64 processors.

    The performance is typically limited by the usage of a platter HDD.
    When using a SSD, the CPU can be the bottleneck if it's an old one
    or if it's used in power-saving mode. 3-tracks gdi can be extracted
    in less than 2 seconds with the right configuration (~1GiB of data).

    To get the most recent version, visit:
    https://github.com/AltoRetrato/gditools3

    or using git: 
    git clone https://github.com/AltoRetrato/gditools3.git

    This project was forked from
    https://sourceforge.net/projects/dcisotools/
    
    bin2iso.py and gdifix.py (creating a single .iso from a gdi dump)
    are provided in the 'addons' folder. They can be used as is or be
    used to see how to incorporate gditools3.py in another project.

    See the Legal Stuff section at the end of this readme for the infos
    on licensing and using this project in another one.

    Enjoy!    

    Ricardo Mendonça Ferreira.

    Many thanks to FamilyGuy for sharing his original work!

    Thanks to SiZiOUS for testing the code, providing support
    and for the original GUI program.

     ___                _                        __    
    / _ \___ ___ ___ __(_)______ __ _  ___ ___  / /____
___/ , _/ -_) _ `/ // / / __/ -_)  ' \/ -_) _ \/ __(_-<________________________
  /_/|_|\__/\_, /\_,_/_/_/  \__/_/_/_/\__/_//_/\__/___/
             /_/
			 
   - Python 2.7.x or Python 3.4.x.
   - On Windows you have to add the python folder to your path manually (or 
     choose the option when installing).

     __  __                 
    / / / /__ ___ ____ ____ 
___/ /_/ (_-</ _ `/ _ `/ -_)___________________________________________________
   \____/___/\_,_/\_, /\__/ 
                 /___/      
    python gditools3.py -i input_gdi [options]

      -h, --help             Display this help
      -l, --list             List all files in the filesystem and exit
      -o [outdir]            Output directory. Default: gdi folder
      -s [filename]          Create a sorttxt file with custom name
                               (It uses *data-folder* as prefix)
      -b [ipname]            Dump the ip.bin with custom name
      -e [filename]          Dump a single file from the filesystem
      --extract-all          Dump all the files in the *data-folder*
      --data-folder [name]   *data-folder* subfolder. Default: data
                               (__volume_label__ --> Use ISO9660 volume label)
      --sort-spacer [num]    Sorttxt entries are sperated by num
      --silent               Minimal verbosity mode
      [no option]            Display gdi infos if not silent

     __  __                    ____                     __      
    / / / /__ ___ ____ ____   / __/_ _____ ___ _  ___  / /__ ___
___/ /_/ (_-</ _ `/ _ `/ -_)_/ _/ \ \ / _ `/  ' \/ _ \/ / -_|_-<_______________
   \____/___/\_,_/\_, /\__/ /___//_\_\\_,_/_/_/_/ .__/_/\__/___/
                 /___/                         /_/              
			  
  0- Listing all files in the gdi:
        gditools3.py -i /folder/disc.gdi --list

  1- Displaying gdi infos:
        gditools3.py -i /folder/disc.gdi

  2- Dumping bootsector/initial program/ip.bin:
        gditools3.py -i /folder/disc.gdi -b ip.bin

  3- Generating a sorttxt file:
        gditools3.py -i /folder/disc.gdi -s sorttxt.txt

  4- Generating a sorttxt file with a different "data" folder (see example 9):
        gditools3.py -i /folder/disc.gdi -s sorttxt.txt --data-folder MyDump

  5- Extracting a single file:
        gditools3.py -i /folder/disc.gdi -e 1st_read.bin

  6- Specifying a different output folder:
       (default one is the gdi folder)
        gditools3.py -i /folder/disc.gdi -e 1st_read.bin -o /OtherFolder

  7- Extracting all the files from the gdi:
        gditools3.py -i /folder/disc.gdi --extract-all

  8- Specifying a different subfolder name:
       (default one is "data")
        gditools3.py -i /folder/disc.gdi --extract-all --data-folder MyFolder

  9- Using the iso9660 filesystem volume label as the subfolder name:
        gditools3.py -i /folder/disc.gdi --extract-all --data-folder __volume_label__

 10- Doing most of the above at once:
        gditools3.py -i /folder/disc.gdi -s sorttxt.txt -b ip.bin 
                    -o /OtherFolder --data-folder __volume_label__  --extract-all

     __  __    _             __  __         _______  ______
    / / / /__ (_)__  ___ _  / /_/ /  ___   / ___/ / / /  _/
___/ /_/ (_-</ / _ \/ _ `/ / __/ _ \/ -_) / (_ / /_/ // /______________________
   \____/___/_/_//_/\_, /  \__/_//_/\__/  \___/\____/___/  
                   /___/                                   
				   
    A new, pure Python GUI version is in the works.

      __                 __  ______       ______
     / /  ___ ___ ____ _/ / / __/ /___ __/ _/ _/
___ / /__/ -_) _ `/ _ `/ / _\ \/ __/ // / _/ _/________________________________
   /____/\__/\_, /\_,_/_/ /___/\__/\_,_/_//_/   
            /___/                               

    gditools3.py, provided addons and the GUI are licensed under the GNU
    General Public License (version 3), a copy of which is provided
    in the licences folder: GNU_GPL_v3.txt
    
    Original iso9660.py by Barney Gale : github.com/barneygale/iso9660
    iso9660.py is licensed under a BSD license, a copy of which is 
    provided in the licences folder: iso9660_license.txt

_____________________________________________________________________/ eof /___
