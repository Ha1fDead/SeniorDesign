

class User:

	def __init__(self, dbObj):
		self.Id = dbObj[0]
		self.lockerId = dbObj[1]

