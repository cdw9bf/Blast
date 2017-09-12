import Rhino as rh
import rhinoscriptsyntax as rs
import math
import Rhino.Geometry as rg

from System import Object
from datatypes import line


# Vertex Class:
# Creates a datastructure for ease of access for the given information
# 
class vertex:
	def __init__(self, point3D, index=0):
		self.vertex         = point3D
		self.connection     = [] 
		self.index          = index
		self.numConnections = 0
		self.connectionsOrg = []
		
		self.X              = point3D.X
		self.Y              = point3D.Y
		self.Z              = point3D.Z
	
	def addVertex(self, ind):
		self.connection.append(ind)
		self.connectionsOrg.append(ind)
		self.numConnections += 1
	
	def resetConnections(self):
		# resets the connections incase of disaster
		self.connection = list(self.connectionsOrg)




def removeBottoms(lines, rmBottoms=True):
	# Parameters: lines - 1d list of all lines in current voxel list, 
	# the lines all must be of class line in datatypes
	#
	# Output: Dictionary, Dictionary 
	#         Following format {'key': [value, value2, value3]}
	# 
	# Finds horizontal and verticle lines, then sorts them based on Z height 
	#  if option is selected (highly recommend), it will remove the bottom
	#  horizontal layer so that the robot will stick into the foam but not 
	#  drag through it. If there is a different material avaliable to print 
	#  on which doesn't require sticking into something, then it may be 
	#  perferable to leave the bottom layer intack. 
	horizontal = {}
	vertical = {}
	for l in lines:
		l.isFlat()
		l.genZHash()
	
		if l.flat:
			if l.zHash not in horizontal:
				horizontal[l.zHash] = [l]
			else:
				horizontal[l.zHash].append(l)
		else:
			if l.zHash not in vertical:
				vertical[l.zHash]   = [l] 
			else:
				vertical[l.zHash].append(l)
	zValues = horizontal.keys()
	zValues.sort()
	
	# deletes lowest flat layer
	if rmBottoms:
		del horizontal[zValues[0]]
	
	return vertical, horizontal


def verticalSort(vertical, side):
	# to be filled in 
	return vertical


	
	
	
def _getUniquePoints(list):
	# Parameters [list] of lines in the datatypes.line class
	#
	# Output: [list] of all unique endpoints on the layer in 
	#          pathAlgorithms.vertex class 
	#
	# This Algorithm sorts the points by start and end hash 
	# then linking the points together if they are in the index. 
	# Example: Line has v1 and v2 as the ending points. The vertex
	# v1 will have v2 in its vert Indexes and vice versa. Thus it 
	# exhibits linked list type personalities.
	
	
	points = {}
	# find all unique points
	i = 0
	for p in list :
		if p.startHash not in points:
			points[p.startHash] = vertex(point3D=p.start, index=i)
			i += 1
		if p.endHash not in points:
			points[p.endHash]   = vertex(point3D=p.end,   index=i)
			i += 1
		p.vertIndexes = [points[p.startHash].index, points[p.endHash].index]
		# adds connection between two of the vertices by linking their indexes
		points[p.startHash].addVertex(points[p.endHash].index)
		points[p.endHash].addVertex(points[p.startHash].index)
	
	
	# This is a very important step. It makes the index given to the points 
	# match the order they are in the list. This is a CRITICAL assumption 
	# made later in the code that this step is correct. 
	ps = points.values()
	uniquePoints = [[] for x in range(len(ps))]
	for m in ps:
		uniquePoints[m.index] = m	
	return uniquePoints

	
def _getMinXAndYCorner(currentPoints, uniquePoints, retCorners=True):
	# Parameters: [list] of pathAlgorithms.vertex class
	#
	# Output: Single instance of pathAlgorithms.vertex class
	#
	# First it finds the minimum x coordinate and all corners on that and
	# then finds point with minimum y coordinate from that sublist. It identifies
	# possible corner points by the fact that they will only be linked to two other
	# vertexes.
	
	corners = {}
	for x in range(len(currentPoints)):
		if currentPoints[x].numConnections == 2:
			h = int(currentPoints[x].vertex.X)
			if h not in corners:
				corners[h] = [[currentPoints[x].vertex.Y, currentPoints[x].index]]
			else:
				corners[h].append([currentPoints[x].vertex.Y, currentPoints[x].index])
	key = corners.keys()
	key.sort()
	low = corners[key[0]]
	low.sort()
	# low[0][1] is the index in 'sorted' of the 
 	startPoint = uniquePoints[low[0][1]]
	
	cornerInds = [] 
	if retCorners:
		vals = corners.values()
		for v in vals:
			for cornerPoint in v:
				cornerInds.append(cornerPoint[1])
		
	
	return startPoint, cornerInds

	
def __sortOrder(x):
	if abs(x-360) < 0.01:
		return -10000
	else:
		return x
	
	
def _nextPoint(angle, direction):
	# Input [[float, vertexClass, [float, float], char]
	# [[angle in degrees, vertex of nextPoint, nextPoint normed vector from current point]] ->
	#  [angle, next vertex, [vX,vY]]
	#
	#
	# Output: [float, vertexClass, [float, float]]
	#  [[same format as above]]
	#
	# This is the critical part that determines the next stride. 
	#  1. Find smallest angle
	#  2. If that is 270, check for 360 
	#      NOTE: Should never be 180, if 180 is even an option, something has gone wrong
	err = 0.01
	if direction == "R":
		order = [90, 270]
		angle.sort()
	elif direction == "L":
		order = [270, 90]
		angle.sort(key=lambda x: __sortOrder(x[0]))
		angle = angle[::-1]
	else:
		return ValueError("Invalid Direction, must either be L or R")
	
	angle = [a for a in angle if abs(a[0]-180) > err] 
	if len(angle) == 0:
		raise ValueError("_perimeter function failed unexpectedly. Check for weird corner conditions.")

	

	if abs(angle[0][0] - order[0]) < err:
		return angle[0]
	
	elif abs(angle[0][0] - order[1]) < err:
		diff = [(360 - angle[x][0]) < err for x in range(len(angle))]
		if True in diff:
			ind = diff.index(True)
			return angle[ind]
		else:
			return angle[0]
	else:
		#if abs(angle[1][0] - 90) < err and abs(angle[0][0] - 180) < err:
		#	print "weird condition", angle
		#	return angle[1]
		#else:
		raise ValueError("_nextPoint function has failed")
	
	
	
	

 
def _norm(v):
	# Input: 2D list [vX, vY]
	#
	# Output: 2D list [vnormX, vnormY]
	#
	# Description: Normalize a 2d vector
	
	l = _length(v)
	vNorm = [v[0]/l, v[1]/l]
	return vNorm
 
 
 
def _angle(v1, v2):
	# specifically for right turns 
	
	# full formula below
	#cosx= (v1[0]*v2[0]+v1[1]*v2[1])/(length(v1)*length(v2))
	
	# abbreviated 
	cosx= (v1[0]*v2[0] + v1[1]*v2[1]) # / 1 since length is normalized
	rad = math.acos(cosx)
	deg = rad * 180/math.pi
	det = v1[0]*v2[1] - v1[1]*v2[0]
	if det < 0:
		return deg
	else:
		return 360-deg
 
def _length(v):
    return math.sqrt(v[0]**2+v[1]**2)

 
	
def _perimeter(uniquePoints, startPoint, order, direction, v1=[1,0]):
	c = 0
	isLoop = False 
	
	# Rules:
	#     - Counter Clockwise
	#     - Never go straight if there is an option to go 90 right
	#     - Only do 270 if it is your only option
	#     - Going Straight takes precendent over 270
	#  Once back at initial point, end while loop. Probably will put into own 
	#  definition so you don't have one for right and left handedness. 
	
	# currentPoint is a vertex class object
	currentPoint = startPoint
	previousPointIndex = startPoint.index
	currentOrder = [startPoint.index]

	while not isLoop: 
		angles = []
		c+=1 
		
		# This value might have to be raised if dealing with huge voxel structure
		if c > 1000:
			raise ValueError("Stuck in infinite loop, aborting.")
		
		# find all next possible canidates points in the connection list
		possibleNextPoints = [uniquePoints[ind] for ind in currentPoint.connection]

		# find angle between current point vect and other vectors
		#
		# v1 is old vector 
		# v2 is new vector
		#
		angle = []
		for p in possibleNextPoints:
			v2 = [p.X - currentPoint.X, p.Y - currentPoint.Y]
			v2 = _norm(v2)
			angle.append([_angle(v1, v2),p,v2])
		nextPoint = _nextPoint(angle,direction)
		# set previous vector to new vector
		currentOrder.append(nextPoint[1].index)
		v1 = nextPoint[2]
		
		# now set index 
		previousPointIndex = currentPoint.index
			
		#now remove each point from the list
		currentPoint.connection.remove(nextPoint[1].index)
		nextPoint[1].connection.remove(currentPoint.index)
		
		if nextPoint[1].index == startPoint.index:
			isLoop = True
			break
			
		currentPoint = nextPoint[1]	
	order.append(currentOrder)
	return


def isPointInside(x,y,poly):
	# Params: float, float, [[float,float],...]
	# x - x coord of point being tested
	# y - y coord of point being tested
	# poly - list of x and y of every vertex point
	# 
	# returns: True or False 
	#
	n = len(poly)
	inside = False
	p1x,p1y = poly[0]
	for i in range(n+1):
		p2x,p2y = poly[i % n]
		if (y > min(p1y,p2y)) and (y <= max(p1y,p2y)) and (x <= max(p1x,p2x)):
			if p1y != p2y:
				xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
			if p1x == p2x or x <= xinters:
				inside = not inside
		p1x,p1y = p2x,p2y 
	return inside
	
	
	
def infill(horizontal):
	# Parameters:  dict{}
	#  Dictionaries sorted via z height, each level contains list of lines
	#  
	# Output: sorted list of lists (in dict format?)
	#
	# This algorithm will go from the starting corner closest to the robot and then
	# find the left most point each time. It will outline the structure first then 
	# proceed to left turns. 
	#
	# Since the start point is a corner at both min x and y, it is safe to assume the
	# corner is " |_ ", so to proceed counter clockwise, we can start with the vector   
	# that is || (parallel) to the vector [1,0,0]. 
	# 
	# NOTE: This will only be true in the cube or rectangle case 
	# 
	
	layers = horizontal.values()
	i = 0
	
	
	orderedPoints = []
	for l in layers:
		order = []
		uniquePoints = _getUniquePoints(l)
		startPoint, cornerInds  = _getMinXAndYCorner(currentPoints=uniquePoints,uniquePoints=uniquePoints)
		direction = "R"
		v1 = [1,0]
		
		c=0
		# Perimeters 
		while len(cornerInds) != 0:
			c += 1
			if c > 1000:
				raise ValueError("Infinite Loop, aborting")

			_perimeter(uniquePoints, startPoint, order, direction, v1)
			
			if len(order[-1]) == 5:
				v1 = [v1[x]*-1 for x in range(len(v1))]
				for uInd in order[-1]:
					uniquePoints[uInd].resetConnections()
				print (" loop upper")
				continue 
			else:
				v1 = [1,0]
			
			# Finds all corner points not used in perimeter
			# If no more corner points, break
			good = []
			for i,c in enumerate(cornerInds):
				if c in order[-1]:
					continue
				else:
					good.append(i)
			cornerInds = [cornerInds[g] for g in good]
			if len(cornerInds) == 0:
				break
			
			# get new min x and min y, will stop corner from being inside yet to form perimeter
			nPoints = [uniquePoints[x] for x in cornerInds]
			p, _ = _getMinXAndYCorner(currentPoints=nPoints, uniquePoints=uniquePoints, retCorners=False)  # _ is a dummy variable
			
		    # Check if corner point is inside permeter or not
			#  If it is not, then do another clockwise right loop
			#  If it is, then do a  clockwise left loop
			
			for o in order:
				poly = [[uniquePoints[i].X, uniquePoints[i].Y] for i in o]
				isIn = isPointInside(p.X, p.Y, poly)
				if isIn:
					startPoint = p
					direction = 'L'
					break
				else:
					startPoint = p
					directoin = 'R'

		
		straightHoles = [i.index for i in uniquePoints if i.numConnections == len(i.connection) == 3]
		c=0
		v1 = [1,0]
		
		while len(straightHoles) != 0:
			c+=1
			if c>1000:
				raise ValueError("Infinite loop. Aborting.")
			startPoint = uniquePoints[straightHoles[0]]
			_perimeter(uniquePoints, startPoint, order, "L", v1=v1)
			if len(order[-1]) == 5:
				v1 = [-1,0]
				for uInd in order[-1]:
					uniquePoints[uInd].resetConnections()
				print (" loop lower ")
				continue 
			else:
				v1 = [1,0]
			
			
			
			good = []
			for i,c in enumerate(straightHoles):
				if c in order[-1]:
					continue
				else:
					good.append(i)
			straightHoles = [straightHoles[g] for g in good]
		
		# central body 
		# What infill is desired:
		# right handed, straight, continuous? 
		
		# currently only contains right handed ones
		#rightHand(uniquePoints, order)
		
		
		# unrolls all points for display, not for use in grasshopper other than display purposes.
		for o in order:
			for i in o:
				orderedPoints.append(uniquePoints[i].vertex)
			
	return orderedPoints
		



def rightHand(uniquePoints, order):
	# same as left hand but going the opposite direction
	#
	#
	#
	# work in progress
	"""
	points = [uP for uP in uniquePoints if len(uP.connection) > 0]
	while len(points) > 0:
		startPoint, _ = _getMinXAndYCorner(currentPoints=points, uniquePoints=uniquePoints, retCorners=False)
	"""
	return



















