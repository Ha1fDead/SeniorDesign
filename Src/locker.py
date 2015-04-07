import DAL

class Locker:

	def __init__(self, dbObj):
		self.Id = dbObj[0]
		self.Username = dbObj[1]
		self.Password = dbObj[2]
		self.Battery = dbObj[3]