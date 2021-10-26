# Mitsuba2 Parsers

This folder incluse the necessary parsers to copy and create additional information for
training a NN with the generated Mitsuba images.

This may be useful to save the normals, copy some images and create additional data for other algorithms.
Note that in this case this was used to train an algorithm on PVnet, so the output information was tailored
to fit its requirements. Still, it is intended that this code remains useful for general purpose.

For a detailed generation for PVNet, some pre-processing algorithms specifically for that architecture were created 
in the PVnet repo of this author. Please refer to that one for more advanced features.

## Camera Parser
This parser is the most important, as it is used during the rendering process of Mitsuba to read the poses.
Thus, this parser has no "main" function and cannot be executed with a command window.

The main purpose of this parser is to read the transformation matrix in BOP format exported
by BlenderProc and transform then into transformation matrices for the Mitsuba format. It can
read pictures one by one or export all the matrices at once.

## Masks Parser
This parser reads the annotation masks from a coco file and creates the matching mask
for those images. This parser can be directly executed after changing the input and output files.

## Normals Parser
Really similar to the normals one, however, this parser reads the data from hdf5 files 
from Blender Proc. Appart from the input and output, this parser can be modified to read
any additional information generated with blender proc, like depth images.

## TXT Parser
This last parser will create two txt files, one with the cameras intrinsic parameters, and
one with the objects diameter (as read in Blender for that object). Additionally, it will 
create 3x4 transformation matrices for all the poses and store then in .npy files.

This parser can be executed separately if only one of the files needs to be generated. 