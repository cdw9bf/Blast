import Rhino as rh
import rhinoscriptsyntax as rs 
import math
import Rhino.Geometry as rg



class point:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y 
		self.z = z 
	
	def export(self):
		return rs.AddPoint(self.x, self.y, self.z)
	
	def setcoord(self, coord, dim="x"):
		if dim == "x":
			self.x = coord
		if dim == "y":
			self.y = coord
		if dim == "z":
			self.z = coord
		


		
class line: 
	# Use the object class here, not the rhino point syntax 
	def __init__(self, start_pt, end_pt):
		self.start = start_pt
		self.end   = end_pt
	
	def switch(self):
		tmp = self.start
		self.start = self.end
		self.end = tmp
	
	def export(self):
		return rs.AddLine(self.start.export(), self.end.export())