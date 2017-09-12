import Rhino as rh
import rhinoscriptsyntax as rs
import math
import Rhino.Geometry as rg


from System import Object
from datatypes import line

def find_center_of_voxel(polylines, center=None):
	# Parameters: ([list of polyline], [cX, cY, cZ]) 
	#
	# Output: [cX, cY, cZ]
	# 
	#
	# Description:
	#  If the center of the voxel is not known, it will take all the extreme points of the voxel
	# and find the center from that
	if center is not None:
		return center
	
	num_lines = len(polylines)
	coords = [[[] for x in range(num_lines * 2)] for dim in range(3)] # x , y , z
	
	
	for l,polyline in enumerate(polylines):
		coords[0][l] = polyline.PointAtStart[0]
		coords[1][l] = polyline.PointAtStart[1]
		coords[2][l] = polyline.PointAtStart[2]
		
		coords[0][l+num_lines] = polyline.PointAtEnd[0]
		coords[1][l+num_lines] = polyline.PointAtEnd[1]
		coords[2][l+num_lines] = polyline.PointAtEnd[2]
	
	
	b_x = max(coords[0]) + min(coords[0])
	b_y = max(coords[1]) + min(coords[1])
	b_z = max(coords[2]) + min(coords[2])
	
	center = [b_x / 2.0, b_y / 2.0, b_z / 2.0]
	return center


	
def box(brep, size, voxel, center=[0,0,0]):
	# Parameters:
	#    Input  - Brep object, [xdim, ydim, zdim], Point3d but the code will calculate it, [list of curves]
	#    Output - tuple of datatypes.line for every curve
	#
	# Description:
	# 
	# Find the Min and Max of Brep 
	# Then Look at size of the box 
	# Create a grid of the center points of the box
	# Test each box to see if they are in the brep, if they are not, delete them
	# Find all corner points, create the lines 
	# return the list of lines
	
	

		
	# Moves reference voxel to be centered around 0,0,0
	# This will make the translation for each of the voxels easier
	for n,polyline in enumerate(voxel):
		polyline.Translate(-1*center[0], -1*center[1], -1*center[2])    #  translation
	
	dim = 3
	tolerance = 1e-2
	# List of max and min points
	bound  = brep.GetBoundingBox(True)
	num_boxes = [[] for n in range(dim)]
	
	for n in range(dim):
		num_boxes[n] = int((bound.Max[n] - bound.Min[n]) / size[n]) + 2 
		# + 2 for integers rounding down. Once in this int, 2nd time in for loop
		# when populating the center point grid. Add more if you don't feel the 
		# centers are expanding a large enough area around your brep 
	
	# Lay boxes in a grid
	
	total_boxes = num_boxes[0] * num_boxes[1] * num_boxes[2]
	

	if total_boxes > 1000: 
		# This text will appear on the rhino command area where you can enter the information 
		# Mainly this is a safety check, if this amount of voxels is selected, your computer will
		# more than likely end up crashing.
		warn=raw_input("Warning: Number of Voxels will exceed 1000, recommend picking a larger voxel. If you wish to continue, enter 'yes'")
		if warn == "yes": pass
		# else: raise ValueError
	
	
	
	# Populate the box with smaller boxes
	centerBrep = [(bound.Max[0] + bound.Min[0]) / 2., (bound.Max[1] + bound.Min[1]) / 2., (bound.Max[2] + bound.Min[2]) / 2.]
	center_points = []
	for x in range(-num_boxes[0] / 2 , num_boxes[0] / 2, 1):
		for y in range(-num_boxes[1] / 2, num_boxes[1], 1):
			for z in range(-num_boxes[2] / 2, num_boxes[2] / 2, 1):
				# shift to point
				x_coord = centerBrep[0] + x * size[0]
				y_coord = centerBrep[1] + y * size[1]
				z_coord = centerBrep[2] + z * size[2]
				
				point = rg.Point3d(x_coord, y_coord, z_coord)
				if brep.IsPointInside(point, 0.01, True):  # 0.01 is the tolerance
					center_points.append(point)
	

	 
	all_lines = [[] for n in range(len(voxel) * len(center_points))]
	# Now add all of the lines
	
	counter = 0
	for pt in center_points:
		for polyline in voxel:
			newLine = polyline.Duplicate()
			newLine.Translate(rg.Vector3d(pt))
			all_lines[counter] = line(lineCurve=newLine)
			counter += 1
	

	
	#Remove Duplicate Lines
	# iterates through dictionary, if a point is close enough, then iterate through that point
	#    When iterating through that point, look at endings of all other lines at that point
	#	 IF there is a match, then do nothing 
	# 	 No match, add that line to the entry
	# If there is no inital point close enough to the point being compared, then add it to dictionary
	
	
	unique = {}

	for i, l in enumerate(all_lines):
		if l.startHash not in unique:
			unique[l.startHash] = [l]
		else:
			sameStart = unique[l.startHash]
			matched = False
			
			for s in sameStart:
				if l.endHash == s.endHash:
					offset = 0
					for p in range(3):
						offset += l.start[p] - s.start[p]  + l.end[p] - s.end[p]
					
					if offset < tolerance:
						# breaks 2nd for loop
						# if matched line is found, no need to continue
						matched = True
						break
			
			if matched is False:
				unique[l.startHash].append(l)
	# Now we have a dictionary of all the unique lines! We will return a basic list of 
	# the class called "line"
	vals = unique.values()
	flat = []
	
	# flattening 2d list
	for v in vals:
		for l in v:
			flat.append(l)
			
	return flat, center_points
	
	
	
	
	
		
	
