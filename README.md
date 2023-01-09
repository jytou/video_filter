# Description

A simple project to read a video, apply some real-time filters, and save the resulting video. 

The main frame can be started by launching python VideoFilter.py

# Requirements

Python 3.7+ is required, along with PyQt5+. OpenCV 2+ must be installed and active.
See requirements.txt

# Image filters

Image filters can be added by creating new files in the subdirectory “filters”.
Filenames must exactly match the filter names so that they can be recognized dynamically by the app at loading time.

Those classes must match the template Filter class defined in filter.py.

# TODO list

This project is very basic, a few ideas of things that could easily be added or enhanced:

- add more filters,
- better handling of bogus files in the “filters” directory,
- enable subdirectories in the “filters” directory (need to change the loader for that),
- save current filters into a config file that can be loaded again later,
- open app with the same filters as when it was last closed,
- better handling of screen size (currently fixed size),
- show the current parameter values for the different filters,
- move the filters up and down with up/down buttons to change the order in which they are applied,
- disable filters rather than needing to remove them,
- more options in the configuration of filters,
- deal with grayscale videos (currently only deals with color),
- add some video controls and embed them in the video frame,
- handle different video resolutions,
- there is a great deal of missing exception handling,
- add some mechanism to throttle the framerate or skip frames if the computer cannot cope with real-time filtering.

Here are also a couple of ideas to accelerate the saving of the video:
- use a different video encoder,
- parallelize the processing of frames with the existing code:
- - one process decodes the frames and sends them to a queue (with an index),
- - n processes pick frames from the queue and do the decoding,
- - another process picks the frames and waits for the next index to be available to make sure we are encoding in correct frame order
- go for a mix of opencl and opencv to do the heavy lifting on the GPU (see for instance [this blog](https://www.danielplayfaircal.com/blogging/2021/03/05/transforming-compressed-video-on-the-gpu-using-opencv.html))
