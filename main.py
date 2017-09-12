import Rhino as rh
import rhinoscriptsyntax as rs
import math
import Rhino.Geometry as rg



from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

# Path to Downloaded Github Directory
new_path = r'c:\Users\Chris\Documents\blast_python'

import sys, os
if new_path not in sys.path: sys.path.append(new_path)

import datatypes
reload(datatypes)
from datatypes import line

import pathAlgorithms
import voxelize
reload(pathAlgorithms)
reload(voxelize)



# Size of Voxel
if cube and box:
	size = [dim_x, dim_x, dim_x]
if not cube and box:
	size = [dim_x, dim_y, dim_z]





# Makes a cube if none is provided
if voxel is None and cube:
	center = [0,0,0]
	voxel  = []
	
	s = [0.5*size[0], 0.5*size[1], 0.5*size[2]]
	t1 = rg.Point3d(-1*s[0],-1*s[1], 1*s[2])
	t2 = rg.Point3d(-1*s[0], 1*s[1], 1*s[2])
	t3 = rg.Point3d( 1*s[0], 1*s[1], 1*s[2])
	t4 = rg.Point3d( 1*s[0],-1*s[1], 1*s[2])
	
	b1 = rg.Point3d(-1*s[0],-1*s[1],-1*s[2])
	b2 = rg.Point3d(-1*s[0], 1*s[1],-1*s[2])
	b3 = rg.Point3d( 1*s[0], 1*s[1],-1*s[2])
	b4 = rg.Point3d( 1*s[0],-1*s[1],-1*s[2])
	
	
		
	#verticle lines
	voxel.append(rg.LineCurve(b1, t1))
	voxel.append(rg.LineCurve(b2, t2))
	voxel.append(rg.LineCurve(b3, t3))
	voxel.append(rg.LineCurve(b4, t4))
		
	#upper
	voxel.append(rg.LineCurve(t1, t2))
	voxel.append(rg.LineCurve(t2, t3))
	voxel.append(rg.LineCurve(t3, t4))
	voxel.append(rg.LineCurve(t4, t1))
		
	#lower
	voxel.append(rg.LineCurve(b1, b2))
	voxel.append(rg.LineCurve(b2, b3))
	voxel.append(rg.LineCurve(b3, b4))
	voxel.append(rg.LineCurve(b4, b1))
		
		
center  = voxelize.find_center_of_voxel(voxel)
allVoxels, centers  = voxelize.box(brep, size, center=center, voxel=voxel)
vertical, horizontal = pathAlgorithms.removeBottoms(allVoxels, rmBottoms)

v = vertical.values()
h = horizontal.values()

m = []

for i,k in enumerate(h):
    if i != -2:
        for l in k:
            m.append(l.line)
for k in v:
    for l in k:
        m.append(l.line)
        pass
a = m 

points = pathAlgorithms.infill(horizontal)
b = points
