# TilledMapDownloader
TilledMapDownloader is a python script that download and put together some given tiles of a web map.

### Usage
It takes the following parameters :
* `--url "my.url"` _(required)_  
used to define the url pattern to get the tiles. There are 2 placeholders that should be included in the url:
  1. `___x___` to mark the location of x in the query
  2. `___y___` to mark the location of y in the query
* `-x m M` _(required)_  
the minimum `m` and maximum `M` x coordinates of the tiles to download
* `-y m M` _(required)_  
the minimum `m` and maximum `M` y coordinates of the tiles to download
* `-d path/to/use/` _(optional)_  
change the working and output directory (default is the current directory)
* `-t N` _(optional)_  
set the number `N` of threads to use (default is 4)

###Example
    python tilled_map_downloader.py --url http://a.tile.openstreetmap.fr/osmfr/15/___x___/___y___.png -x 17050 17071 -y 11347 11370 -t 8
This command will download and assemble a map from OpenStreetMap with a zoom level of 15, starting at the uper-left corner of coordinates (17050;11347) and ending at the bottom right corner (17071;11370) using 8 threads.
