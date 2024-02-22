RotateAtoms.py rotates select atoms around a given axis which is aligned with the z-axis.

usage: RotateAtoms [-h] [-f FILE] [-i INDICES [INDICES ...]] [-p POINT POINT] [-a ANGLE] [-o OUTPUTTYPE]
Example: ./RotateAtoms.py -f CuIO4.cif -i 4 13 24 -p 0.5 0.5 -a 180  

This program takes a structure file, a list of atom indices (1-indexed), the x and y fractional coords of an axis of rotation (aligned with the z-axis)
and an angle of rotation in degrees, and rotates the selected atoms around that axis and returns a rotated .cif file.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Filepath to structure file.
  -i INDICES [INDICES ...], --indices INDICES [INDICES ...]
                        List of atom indices (1-indexed) separated by spaces.
  -p POINT POINT, --point POINT POINT
                        x and y fractional coordinates of the axis of rotation. Coordinates must be passed in separated by spaces
  -a ANGLE, --angle ANGLE
                        Angle of rotation in degrees.
  -o OUTPUTTYPE, --outputType OUTPUTTYPE
                        Output file type - POSCAR or cif. .cif is the default file type.

Hope this helps!
