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
tile_width = 256  #TODO: Get this value automaticaly
tile_height = 256

#Threading vars
lock = threading.Lock()

class TilesGenerator():
    def __init__(self, min_x, max_x, min_y, max_y, tiles_directory, status_callback):
        self.daemon = True
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.tiles_directory = tiles_directory
        self.status_callback = status_callback

        self.nb_total_tiles = (max_x-min_x+1)*(max_y-min_y+1)

        self.x = self.min_x-1
        self.y = min_y
        self.index = 0

    def get_next(self):
        while True:
            if self.x == None or self.y == None:
                break
            elif self.x < self.max_x:
                self.x = self.x+1
                self.index = self.index+1
                self.status_callback((0.6*self.index/self.nb_total_tiles), "Téléchargement des tuiles {0}/{1}".format(self.index, self.nb_total_tiles))
                print('\b'*(len(str(self.nb_total_tiles))*2+27)+"[{0}/{1}] Download".format(self.index, self.nb_total_tiles), end="")
                sys.stdout.flush()
            elif self.y < self.max_y:
                self.y = self.y+1
                self.x = self.min_x
                self.index = self.index+1
                self.status_callback((0.6*self.index/self.nb_total_tiles), "Téléchargement des tuiles {0}/{1}".format(self.index, self.nb_total_tiles))
                print('\b'*(len(str(self.nb_total_tiles))*2+27)+"[{0}/{1}] Download".format(self.index, self.nb_total_tiles), end="")
                sys.stdout.flush()
            else:
                self.x = None
                self.y = None
                break

            if not os.path.exists(os.path.join(self.tiles_directory, str(self.y), str(self.x)+".png")):
                break

        return (self.index, self.x, self.y)

class TilesDownloader(threading.Thread):
    def __init__(self, tiles_generator, base_url, tiles_directory):
        threading.Thread.__init__(self)
        self.__stop__ = False

        self.tiles_generator = tiles_generator
        self.base_url = base_url
        self.tiles_directory = tiles_directory

    def run(self):
        while not self.__stop__:
            with lock:
                (i, x, y) = self.tiles_generator.get_next()
            if x == None or y == None:
                break

            url = self.base_url.replace("___y___", str(y)).replace("___x___", str(x))
            response = requests.get(url, stream=True)
            with open(os.path.join(self.tiles_directory, str(y), str(x)+'.png'), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

    def stop(self):
        self.__stop__ = True

class Worker():
    def __init__(self, min_x, max_x, min_y, max_y, base_url, tmp_directory, file_path, status_callback, nb_threads=4):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.base_url = base_url
        self.tmp_directory = tmp_directory
        self.file_path = file_path
        self.nb_threads = nb_threads
        self.status_callback = status_callback

        self.nb_total_tiles = (max_x-min_x+1)*(max_y-min_y+1)
        self.tiles_generator = TilesGenerator(min_x, max_x, min_y, max_y, tmp_directory, status_callback)

        self.get_all_tiles()
        self.normalize()
        self.combine()

    def get_all_tiles(self):
        i = 0
        for y in range(self.min_y, self.max_y+1):
            tmp_directory_y = os.path.join(self.tmp_directory, str(y))
            if not os.path.exists(tmp_directory_y):
                os.makedirs(tmp_directory_y)

        threads = []
        for i in range(0, self.nb_threads):
            threads.append(TilesDownloader(self.tiles_generator, self.base_url, self.tmp_directory))
            threads[i].start()

        try:
            for i in range(0, self.nb_threads):
                threads[i].join()
        except KeyboardInterrupt:
            self.status_callback(0, 'Processus interompu.')
            sys.stdout.flush()
            for i in range(0, self.nb_threads):
                threads[i].stop()
                threads[i].join()
        print('')



    def normalize(self):
        j=0
        for y in range(self.min_y, self.max_y+1):
            for x in range(self.min_x, self.max_x+1):
                j=j+1
                self.status_callback(0.6+(0.1*j/self.nb_total_tiles), "Vérification des tuiles {0}/{1}".format(j, self.nb_total_tiles))
                print('\b'*(len(str(self.nb_total_tiles))*2+22)+"[{0}/{1}] Normalize".format(j, self.nb_total_tiles), end="")
                sys.stdout.flush()
                try:
                    i = Image.open(os.path.join(self.tmp_directory, str(y), str(x)+'.png'))
                    del i
                except IOError:
                    i = Image.new('RGB', (tile_width, tile_height), (255,0,0))
                    i.save(os.path.join(self.tmp_directory, str(y), str(x)+'.png'))
        print('')



    #Combine all the tiles in one single map
    def combine(self):
        x_composites = []
        for y in range(self.min_y, self.max_y+1):
            self.status_callback(0.7+(0.2*(y-self.min_y+1)/self.max_y-self.min_y+1), "Assemblage préliminaire {0}/{1}".format(y-self.min_y+1, self.max_y-self.min_y+1))
            print('\b'*(len(str(self.max_y-self.min_y+1))*2+22)+"[{0}/{1}] Pre-concatenation".format(y-self.min_y+1, self.max_y-self.min_y+1), end="")
            sys.stdout.flush()
            x_images_path = []
            for x in range(self.min_x, self.max_x+1):
                x_images_path += [os.path.join(self.tmp_directory, str(y), str(x)+'.png')]
            images = list(map(Image.open, x_images_path))
            
            width = 0
            height = 0
            for i in images:
                width += i.size[0]
                height = max(height, i.size[1])
            x_composites += [Image.new("RGBA", (width, height))]

            x = 0
            for image in images:
                x_composites[-1].paste(image, (x, 0))
                x += image.size[0]
                image.close()

        self.status_callback(0.95, "Assemblage final")
        print('\n[0/1] Concatenation', end="")
        sys.stdout.flush()
        width = max(i.size[0] for i in x_composites)
        height = sum(i.size[1] for i in x_composites)
        result = Image.new("RGBA", (width, height))

        y = 0
        for x_composite in x_composites:
            result.paste(x_composite, (0, y))
            y += x_composite.size[1]
            x_composite.close()

        result.save(self.file_path)
        self.status_callback(1, "Fini")
        print('\b'*19+"[1/1] Concatenation")
        sys.stdout.flush()


