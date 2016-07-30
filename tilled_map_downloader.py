#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Autor: Antoine "0x010C" Lamielle
#Date: 17 July 2016
#License: GNU GPL v3

from __future__ import print_function
import sys
import os
from PIL import Image
import requests
import shutil
import threading
from subprocess import call

#Parameters
base_url = ""
zoom_level = 0
min_x = 0
max_x = 0
min_y = 0
max_y = 0
directory = './'
tile_width = 256  #TODO: Get this value automaticaly
tile_height = 256
nb_threads = 4
nb_total_tiles = 0

#Threading vars
lock = threading.Lock()
tiles_generator = None

class TilesGenerator():
    def __init__(self):
        self.daemon = True
        self.x = min_x-1
        self.y = min_y
        self.zoom_level = zoom_level
        self.index = 0
    
    def get_next(self):
        while True:
            if self.zoom_level == None:
                break
            elif self.x < max_x:
                self.x = self.x+1
                self.index = self.index+1
                print('\b'*(len(str(nb_total_tiles))*2+27)+"[{0}/{1}] Download".format(self.index, nb_total_tiles), end="")
                sys.stdout.flush()
            elif self.y < max_y:
                self.y = self.y+1
                self.x = min_x
                self.index = self.index+1
                print('\b'*(len(str(nb_total_tiles))*2+27)+"[{0}/{1}] Download".format(self.index, nb_total_tiles), end="")
                sys.stdout.flush()
            else:
                self.x = None
                self.y = None
                self.zoom_level = None
                break
            
            if not os.path.exists(directory+str(self.zoom_level)+"/"+str(self.y)+"/"+str(self.x)+".jpg"):
                break
        
        return (self.index, self.x, self.y, self.zoom_level)

class TilesDownloader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__stop__ = False
    def run(self):
        global tiles_generator
        while not self.__stop__:
            with lock:
                (i, x, y, zoom_level) = tiles_generator.get_next()
            if zoom_level == None:
                break
			
            get_tile(x, y, zoom_level)
    def stop(self):
        self.__stop__ = True

def get_tile(x, y, zoom_level):
    url = base_url.replace("___zoom___", str(zoom_level)).replace("___y___", str(y)).replace("___x___", str(x))
    response = requests.get(url, stream=True)
    with open(directory+str(zoom_level)+'/'+str(y)+'/'+str(x)+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def get_all_tiles():
    global tiles_generator
    i = 0
    directory_zl = directory + str(zoom_level) + "/"
    if not os.path.exists(directory_zl):
        os.makedirs(directory_zl)
    for y in xrange(min_y, max_y+1):
        directory_zl_y = directory_zl + str(y) + "/"
        if not os.path.exists(directory_zl_y):
            os.makedirs(directory_zl_y)
    
    tiles_generator = TilesGenerator()
    
    threads = []
    for i in xrange(0,nb_threads):
        threads.append(TilesDownloader())
        threads[i].start()
    
    try:
        for i in xrange(0,nb_threads):
            threads[i].join()
    except KeyboardInterrupt:
        print("STOPPING")
        sys.stdout.flush()
        for i in xrange(0,nb_threads):
            threads[i].stop()
            threads[i].join()
    print('')
        



#Combine all the tiles in one single map
def combine():
    j=0
    combine_y = "montage -mode concatenate -tile 1x"+str(max_y-min_y+1)+" "
    for y in xrange(min_y, max_y+1):
        j = j+1
        combine_x = "montage -mode concatenate -tile "+str(max_x-min_x+1)+"x1 "
        print('\b'*(len(str(max_y-min_y+1))*2+22)+"[{0}/{1}] Pre-concatenation".format(j, max_y-min_y+1), end="")
        for x in xrange(min_x, max_x+1):
            combine_x += directory+str(zoom_level)+'/'+str(y)+'/'+str(x)+'.jpg '
        combine_x += directory+str(zoom_level)+'/'+str(y)+'.png'
        sys.stdout.flush()
        call(combine_x, shell=True)
        combine_y += directory+str(zoom_level)+'/'+str(y)+'.png '
    print('\n[0/1] Concatenation', end="")
    sys.stdout.flush()
    combine_y += directory+'out.png'
    call(combine_y, shell=True)
    print('\b'*19+"[1/1] Concatenation")
    sys.stdout.flush()


def normalize():
    j=0
    for y in xrange(min_y, max_y+1):
        for x in xrange(min_x, max_x+1):
            j=j+1
            print('\b'*(len(str(nb_total_tiles))*2+22)+"[{0}/{1}] Normalize".format(j, nb_total_tiles), end="")
            sys.stdout.flush()
            try:
                i = Image.open(directory+str(zoom_level)+'/'+str(y)+'/'+str(x)+'.jpg')
                del i
            except IOError:
                i = Image.new('RGB', (tile_width, tile_height), (255,0,0))
                i.save(directory+str(zoom_level)+'/'+str(y)+'/'+str(x)+'.jpg')
    print('')


def get_params():
    global base_url, zoom_level, min_x, max_x, min_y, max_y, directory, tile_width, tile_height, nb_threads, nb_total_tiles
    
    if "--url" in sys.argv:
        index = sys.argv.index("--url")
        if len(sys.argv) < index:
            bad_params()
        base_url = sys.argv[index+1].decode("utf-8")
    else:
        bad_params()
    
    if "-z" in sys.argv:
        index = sys.argv.index("-z")
        if len(sys.argv) < index:
            bad_params()
        zoom_level = int(sys.argv[index+1].decode("utf-8"))
    else:
        bad_params()
    
    if "-x" in sys.argv:
        index = sys.argv.index("-x")
        if len(sys.argv) < index+1:
            bad_params()
        min_x = int(sys.argv[index+1].decode("utf-8"))
        max_x = int(sys.argv[index+2].decode("utf-8"))
    else:
        bad_params()
    
    if "-y" in sys.argv:
        index = sys.argv.index("-y")
        if len(sys.argv) < index+1:
            bad_params()
        min_y = int(sys.argv[index+1].decode("utf-8"))
        max_y = int(sys.argv[index+2].decode("utf-8"))
    else:
        bad_params()
    
    if "-d" in sys.argv:
        index = sys.argv.index("-d")
        if len(sys.argv) < index+1:
            bad_params()
        directory = sys.argv[index+1].decode("utf-8")
        #Add the trailing '/' if not present
        if directory[-1] != '/':
            directory = directory+'/'
    
    if "-t" in sys.argv:
        index = sys.argv.index("-t")
        if len(sys.argv) < index+1:
            bad_params()
        nb_threads = int(sys.argv[index+1].decode("utf-8"))
    
    nb_total_tiles = (max_x-min_x+1)*(max_y-min_y+1)

get_params()
get_all_tiles()
normalize()
combine()
