import websockets
from websockets.sync.client import connect
import json
import time
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file" , help="The path to the textfile to insert." )
parser.add_argument("-p","--pos", help="The absolute position of text on the map, given as y,x.")
parser.add_argument("-m","--map" , help= "the id of the map to paste this on. If none is given the goes to main map.")
args = parser.parse_args(sys.argv[1:])


def chunk(iterable, size):
    if not iterable or size <= 0:
        return []
    i = 0
    while i < len(iterable):
        j = i + size
        yield iterable[i:j]
        i = j
 


if not args.file:
    print( "no file found.", file=sys.stderr)
    exit(1)

file_path = args.file

if not args.pos:
    print( "no position given.", file=sys.stderr)
    exit(1)

pos = list(map(int,args.pos.split(",")))


map_id = args.map

def read_file_as_lines(file_path):
    '''Read a text file into linex excluding the newline.'''
    with open(file_path) as file:
        return [ line.replace("\n","") for line in file.readlines()]
    


def write_lines_at_pos(pos, lines, socket):
    '''Use websocket to write all the given lines at a position in a map.'''
    for line_index in range(len(lines)):
        line = lines[line_index]
        # make a websocket send request for each line
        chunks = chunk(line,100)
        x = 0
        for line_chunk in chunks:
            writes = []
            for i in range(len(line_chunk)):
                write = Write(line_chunk[i],[pos[0]+line_index, pos[1]+x+i])
                writes.append(write)
            x += len(line_chunk)
            # create request
            write_req = WriteRequest(writes)
            # send
            message_write = json.dumps(write_req.to_dict())
            socket.send(message_write)
            time.sleep(3)

# the request id in a request doesnt seem to be super important, but i have it anyway
req_id = 1


class Request:
    '''Parent class for any websocket request'''
    def __init__(self, kind ):
        self.kind = kind
        global req_id
        req_id += 1

    def to_dict(self):
        return {"kind": self.kind, "request_id": req_id}


class Write:
    '''An object representing a Write operation of a single character at a position'''
    # the write id must be included in socket request, but it seems it can be any integer
    global_write_id = 0
    
    def __init__(self, val , pos):
        self.val = val
        self.timestamp = int(time.time()) * 1000
        # Tile pos is the tile where the character is inserted
        self.tile_pos = [pos[0]//TILE_HEIGHT, pos[1]//TILE_WIDTH]
        # Char pos is the position relative to the tile where a character is inserted
        self.char_pos = [pos[0]%TILE_HEIGHT, pos[1]%TILE_WIDTH]
        Write.global_write_id += 1
        self.write_id  = Write.global_write_id
    
    def to_list(self):
        return [*self.tile_pos, *self.char_pos,self.timestamp,self.val,self.write_id]
    
class WriteRequest(Request):
    '''A  representation of websocket request to write a series of @Write objects to the grid '''
    
    
    def __init__(self, writes):
        super().__init__("write")
        self.writes = writes

    def to_dict(self):
        output = super().to_dict()
        output.update({"edits": [write.to_list() for write in self.writes]})
        return output
    
    

url = f"wss://www.yourworldoftext.com{  f'/{map_id}' if map_id else  ''}/ws/"

TILE_HEIGHT = 8
TILE_WIDTH = 16

def loop_write_lines_at_pos(pos, lines):
    '''Keep Attempting to write lines at a position on a grid'''
    while True:
        try:
            with connect(url) as socket:
                write_lines_at_pos(pos, lines, socket)
                print(f"Inserted {len(lines)} lines at {pos}.")
                return 
        except Exception as e:
            # ensures any error encountered are handled and attempt can be tried again
            print(f"Exception occurred for worker operating at {pos}: {e}")

def main():
    lines = read_file_as_lines(file_path)
    while True:
        futures = []
        line_no = 0
        executor = ThreadPoolExecutor()
        
        for chunk_of_lines in chunk(lines,3):
            future = executor.submit(loop_write_lines_at_pos,[pos[0]+line_no,pos[1]], chunk_of_lines)
            futures.append(future)
            line_no += len(chunk_of_lines)
        
        # waits for all threads to finish before looping again 
        wait(futures, return_when= ALL_COMPLETED)
        
    
if __name__ == "__main__":
    main() 