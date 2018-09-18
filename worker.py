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
from threading import Lock
from PyQt5 import QtCore
from subprocess import call

#Parameters
tile_width = 256  #TODO: Get this value automaticaly
tile_height = 256

#Threading vars
lock = Lock()

class TilesGenerator():
    def __init__(self, min_x, max_x, min_y, max_y, tiles_directory):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.tiles_directory = tiles_directory

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
                sys.stdout.flush()
            elif self.y < self.max_y:
                self.y = self.y+1
                self.x = self.min_x
                sys.stdout.flush()
            else:
                self.x = None
                self.y = None
                break

            if not os.path.exists(os.path.join(self.tiles_directory, str(self.y), str(self.x)+".png")):
                break

        return (self.x, self.y)

    def finished(self):
        self.index = self.index+1
        return (self.index, self.nb_total_tiles)


class TilesDownloader(QtCore.QThread):
    progress = QtCore.pyqtSignal(float, str)


    def __init__(self, tiles_generator, base_url, tiles_directory):
        QtCore.QThread.__init__(self)
        self.__stop__ = False

        self.tiles_generator = tiles_generator
        self.base_url = base_url
        self.tiles_directory = tiles_directory

    def run(self):
        while not self.__stop__:
            # Ask which tiles this thread should download now
            with lock:
                (x, y) = self.tiles_generator.get_next()
            if x == None or y == None:
                break

            # Forge the URL
            url = self.base_url.replace("___y___", str(y)).replace("___x___", str(x))

            # Download the image
            response = requests.get(url, stream=True)

            # Save it
            with open(os.path.join(self.tiles_directory, str(y), str(x)+'.png'), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

            # Check its integrity
            try:
                i = Image.open(os.path.join(self.tiles_directory, str(y), str(x)+'.png'))
                del i
            except IOError:
                i = Image.new('RGB', (tile_width, tile_height), (255,0,0))
                i.save(os.path.join(self.tiles_directory, str(y), str(x)+'.png'))

            # Update the UI
            with lock:
                (index, total) = self.tiles_generator.finished()
            self.progress.emit((0.8*index/total), "Téléchargement des tuiles {0}/{1}".format(index, total))
            print('\b'*(len(str(total))*2+27)+"[{0}/{1}] Download".format(index, total), end="")

    def stop(self):
        self.__stop__ = True




class TilesMerger(QtCore.QThread):
    progress = QtCore.pyqtSignal(float, str)


    #Combine all the tiles in one single map
    def __init__(self, min_x, max_x, min_y, max_y, tiles_directory, file_path):
        QtCore.QThread.__init__(self)

        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.tiles_directory = tiles_directory
        self.file_path = file_path


    def run(self):
        x_composites = []
        print('')
        for y in range(self.min_y, self.max_y+1):
            self.progress.emit(0.8+(0.15*(y-self.min_y+1)/self.max_y-self.min_y+1), "Assemblage préliminaire {0}/{1}".format(y-self.min_y+1, self.max_y-self.min_y+1))
            print('\b'*(len(str(self.max_y-self.min_y+1))*2+22)+"[{0}/{1}] Pre-concatenation".format(y-self.min_y+1, self.max_y-self.min_y+1), end="")
            sys.stdout.flush()
            x_images_path = []
            for x in range(self.min_x, self.max_x+1):
                x_images_path += [os.path.join(self.tiles_directory, str(y), str(x)+'.png')]
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

        self.progress.emit(0.95, "Assemblage final")
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
        self.progress.emit(1, "Fini")
        print('\b'*19+"[1/1] Concatenation")
        sys.stdout.flush()


