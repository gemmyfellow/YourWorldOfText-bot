
# YourWorldOfText bot

This python script uses websockets to connect to a map on [https://yourworldoftext.com](https://yourworldoftext.com) and paste text at a given position.

## Installation
First create a virtual environment
```
python -m venv venv
```

Then activate it:

For Unix
```
source venv/bin/activate
```

For Windows:
```
venv/bin/Activate.ps1
```

Once activate install the ```websockets``` module

```
pip install websockets
```

## Usage

Create a textfile with ASCII art.

Here is a good site for this: [https://lachlanarthur.github.io/Braille-ASCII-Art/](https://lachlanarthur.github.io/Braille-ASCII-Art/)

Make sure you run script in a virtual environment. Then execute ```troll.py``` to continuosly write the ASCII art on the canvas. 

It is a bit slow. This script is meant to be run continously to keep the ASCII art posted.

```
usage: python main.py [-h] -f FILE -pPOS [-m MAP]

options:
  -h, --help            show this help message and exit.
  -f FILE, --file FILE  The path to the textfile to insert onto the map.
  -pPOS, --posPOS     The absolute position of text on the map, where POS is given as "y,x".
  -m MAP, --map MAP     the id of the map to paste this on. If none is given the goes to main map.
```

### Example usage

```
python main.py -f text.txt -p9,-7 -m testmap123 
```

