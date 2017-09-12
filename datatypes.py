import Rhino as rh
import rhinoscriptsyntax as rs 
import math
import Rhino.Geometry as rg




		
class line: 
	# Use the rhino point syntax 
	def __init__(self, start_pt = None, end_pt = None, lineCurve = None):
		# switches start and end if the start point is further from the origin than the end point
		if lineCurve is not None:
			start_vec = sum([lineCurve.PointAtStart[n]**2 for n in range(3)])
			end_vec   = sum([lineCurve.PointAtEnd[n]**2   for n in range(3)])
			
			if (start_vec > end_vec):
				# Switch start and ending
				lineCurve.Reverse()

			
			self.start = rg.Point3d(lineCurve.PointAtStart)
			self.end   = rg.Point3d(lineCurve.PointAtEnd)
			self.line  = lineCurve
			
			
			
		else:
			start_vec  = start_pt.X**2+start_pt.Y**2+start_pt.Z**2
			end_vec    = end_pt.X**2  + end_pt.Y**2 + end_pt.Z**2
		
			if (start_vec > end_vec):
				## Flip start and end point without flipping the curve
				temp     = end_pt
				end_pt   = start_pt
				start_pt = temp
				
			self.start = start_pt
			self.end   = end_pt
			self.line  = rg.LineCurve(self.start, self.end)
		
		
		
		
		self.angle       = None
		self.flat        = False
		self.zHash       = None
		self.vertIndexes = None
		
		self.startHash  = None
		self.startSigns = None 
		self.endHash    = None
		self.endSigns   = None
		
		self._hash()
		
		
		
	def _hash(self):
		self.startHash = self._makeString(self.start)
		self.endHash   = self._makeString(self.end)
		
		#self.startSigns = self._sign(self.start)
		#self.endSigns   = self._sign(self.end)
	
	def _makeString(self, point):
		_hash = ""
		for n in range(3):
			if point[n] < 0:
				_hash += "-"
			_hash += str(int(abs(point[n]))) # takes abs, removes decimal, piles all into one int
		return _hash
	
	def _sign(self, point):
		_signs = []
		for n in range(3):
			if point[n] < 0:
				_signs.append(-1)
			else:
				_signs.append(1)
	
	
	def angle2Plane(self, plane="xy"):
			if plane == "xy":
				pl = [1,1,0]
			elif plane == "xz":
				pl = [1,0,1]
			elif plane == "yz":
				pl = [0,1,1]
			else:
				print ("Wrong input, assuming default value")
				pl = [1,1,0]
			
			v = [pl[n] * self.end[n] for n in range(3)]
			## Formula cos**-1 (a dot b / ||a|| * ||b||)
			adotb =  sum([self.end[n]*v[n] for n in range(3)])
			mag   = math.sqrt(sum([self.end[n]**2 for n in range(3)])) * math.sqrt(sum([v[n]**2 for n in range(3)]))
			#angle = 
	
	def isFlat(self):
		if abs(self.start.Z - self.end.Z) < 1:
			self.flat = True
			
	def genZHash(self):
		if self.flat:
			self.zHash = int(self.start.Z)
			
		elif self.start.Z < self.end.Z:
			self.zHash = int(self.start.Z)
		else:
			self.line.Reverse()
			
			# switch start and end 
			# Now all lines are pointing upwards
			t          = self.end
			self.end   = self.start
			self.start = t
			
			self._hash()
			