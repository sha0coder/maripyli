#!/usr/bin/env python

'''
	maripyli php code analyzer by sha0


	sql,rfi  needs backtracking ...
	lfi manual study
	eval issues: bad detection
	unserialize: apartado propio, testear vuln, conectar con sumidero

	backtracking: solo ver los ifs/whiles/fors (sitios donde haya condicion) y lineas que tengan la var o vars asignadas (y si entra en una funcion?)

	finales del backgracking:
	        la variable monitorizada llega a una asignacion de un literal

	cambio de objeto de seguimento:
	        cambio de variable por variable
	        cambio de variable por funcion
'''

import sys
from cache import *
from printer import *
from phpEngine import *
from backtrace import *


class Maripyli:

	def __init__(self):
		self.cache = Cache()
		self.php = PHPEngine()
		self.php.init()
		self.btraces = []
		self._dbg = False
		
	def debug(self):
		self._dbg = True
		
	def usage(self):
		print('%s [directory]' % sys.argv[0])
		sys.exit(1)
		
	def traceDanger(self,i,fn,var,inp,proj):
		if inp:
			print '/!\ Danger:  %s' % self.php.getLine(i)  # danger conectado con un input directamente
			return
		if not var:
			return # theorically case unreachable
		
		btrace = BackTrace()
		btrace.setProject(proj)
		btrace.setDebug(self._dbg)
		btrace.setVar(var)
		btrace.setEngine(self.php)
		btrace.setLine(i)
		btrace.start()
		self.btraces.append(btrace)

	def checkProject(self,proj):
		print('Checking %s ...' % proj)
		self.btraces = []
		self.cache.load(proj)
		self.php.setCode(self.cache.code)
		#self.php.debug()
		
		for i in self.php.walk():
			(fn,var,inp) = self.php.checkLineDangerN(i)
			if fn:
				self.traceDanger(i,fn,var,inp,proj)
		
		print('Waiting BackTraces ...')  
		for btrace in self.btraces:
			btrace.wait()
		print('BackTraces finished.')


	def check(self,path):
		for proj in self.cache.getProjects():
			self.cache.delete(proj)
			
		self.cache.init(path)
		
		for proj in self.cache.getProjects():
			self.checkProject(proj)
			



if __name__ == '__main__':

	maripyli = Maripyli()
	#maripyli.check('/home/sha0/lab/0day/wp/')
	
	
	if len(sys.argv) < 2:
		maripyli.usage()

	if len(sys.argv) == 3:
		mode = sys.argv[2]
		if mode == '-v': 
			maripyli.debug()
		
	maripyli.check(sys.argv[1])
	
	
