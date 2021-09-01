import os
from printer import *


class Cache:

	def __init__(self):
		self.filename = '.cache'
		self.projects = []
		self.currentProj = ''
		self.dir = '.'
		self.code = []
		
	def getCode(self):
		return self.code

	def init(self, directory):
		self.dir = directory
		self.unzip()

		for p in os.listdir(self.dir):
			if os.path.isdir(self.dir+'/'+p):
				self.projects.append(p)

				if not self.hasCache(p):
					Pr().open('caching %s' % p)
					self.clear()
					self.build(self.dir+'/'+p+'/')
					Pr().close(self.save(p))
				else:
					print('%s already cached' % p)

	def clear(self):
		self.currentProj = ''
		self.code = []

	def getProjects(self):
		return self.projects

	def getcode(self):
		return self.code

	def save(self,proj):
		try:
			fd = open('%s/%s/%s' % (self.dir,proj,self.filename), 'w')
			fd.write('\n'.join(self.code))
			fd.close()
			return True
		except:
			return False

	def delete(self,proj):
		os.unlink('%s/%s/%s' % (self.dir,proj,self.filename))

	def load(self,proj):
		Pr().open('loading cache of %s' % proj)
		self.code = []
		try:
			fd = open('%s/%s/%s' % (self.dir,proj,self.filename))
			tick = 0
			for l in fd.readlines(): #TODO: progress bar?
				'''
				sys.stdout.write('%d\r' % tick)
				sys.stdout.flush()
				tick+=1
				'''
				self.code.append(l.strip())
			fd.close()
			Pr().close(True)
		except Exception, e:
			print e
			Pr().close(False)
		
	def hasCache(self,proj):
		try:
			os.stat(self.dir+'/'+proj+'/'+self.filename)
			return True
		except:
			return False

	def build(self,d):
		for f in os.listdir(d):
			if os.path.isdir(d+f):
				self.build(d+f+'/')
			else:
				try:
					if '.php' in f:
						self.code.append('-begin-')
						fd = open(d+f)
						for l in fd.readlines():
							self.code.append(l.strip())
						fd.close()
						self.code.append('-eof-')
				except:
					pass

	def unzip(self):
		for f in os.listdir(self.dir):
			if '.zip' in f:
				Pr().open('unpacking %s' % f)
				try:
					os.system('cd %s && unzip %s' % (self.dir,f))
					os.unlink(self.dir+'/'+f)
					Pr().close(True)
				except:
					Pr().close(False)
				
	def existsCache(self):
		try:
			os.stat(self.filename)
			return True
		except:
			return False

	def existsAnyZip(self):
		for f in os.listdir(self.dir):
			if '.zip' in f:
				return True
		return False
	
	
	
