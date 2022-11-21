# Autotracker Remastered
Autotracker Remastered is a Python 2.7 script to randomly generate Impulse Tracker format songs based on a predetermined set of WAV samples and various musical parameters.

Based upon autotracker-bottomup by Ben "GreaseMonkey" Russell.
https://github.com/wibblymat/ld24/blob/master/autotracker.py

Heavily modified, split into separate code files, removed the sample generation and just saved them to WAV files.  Added config.txt to allow different bands to be set up, the band will be selected randomly.  The one labeled Default includes the samples that were generated in the original script.

Much of the code that writes the binary file was left unchanged.  This is a little tedious to convert to Python 3.x so I haven't bothered.

The name generator was heavily expanded and modified for many more interesting combinations.

## Requirements
Python 2.7

## Installation
It's a set of scripts.  Run autotracker.py in your favorite IDE or console.  Watch the song appear in the songs directory.  Load it into OpenMPT. https://openmpt.org/  Or Psycle. https://sourceforge.net/projects/psycle/    Edit it to your heart's content.  Enjoy.

## Configuration
The config.txt file contains a path for each of the samples that will be used when randomly generating a song.
Each item is parsed as JSON.  It is divided into sections so that you can generate songs with different "bands" of instruments.  Multiple files on each line means it will randomly pick one of them to use for the song, allowing the songs to vary slightly each time.  To add a new band, just copy the section labeled Default, append it to the file, and change the name and sample paths.

## Usage
```
C:\Python27\python.exe autotracker.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Yes, I know it's still Python 2.7, feel free to make a Python 3.10+ version.

## Wish List
Lots of things.

## License
The Unlicense

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
