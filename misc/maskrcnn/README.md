# Roof detection proof-of-concept using Mask-RCNN

This was a quick test of adapting Matterport's Mask-RCNN code for detecting
roofs (building outlines) in satellite imagery.

## Usage

First clone the repository from here

    git clone https://github.com/matterport/Mask_RCNN
    cd Mask_RCNN/

This script was tested on commit `41e7c596ebb83b05a4154bb0ac7a28e0b9afd017`
so to make sure it works, checkout:

    git checkout 41e7c596ebb83b05a4154bb0ac7a28e0b9afd017

Create a directory on samples/ for storing this script, and then copy it:

    mkdir samples/buildings
    cp buildings.py samples/buildings/

Check buildings.py for instructions on how to train and detect.

You will also need to download [CrowdAI Mapping Challenge
datasets](https://www.crowdai.org/challenges/mapping-challenge/dataset_files).

## License

Based on Nuclei example from Waleed Abdulla.
Licensed under the MIT License (see `Mask_RCNN` LICENSE for details)
