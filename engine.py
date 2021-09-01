import re
'''
	posible optimizations:
		- avoid N wrapping
'''
class Engine:

	def __init__(self):
		self.sz = 0
		self.code = []
		self.functions = []
		self.lang = ''
		self._debug = False
		self.r_fnCall = re.compile('([a-zA-Z0-9_]+) *\(')
		self.r_assign = re.compile('[^=]=[^=]')

	def debug(self):
		self._debug = True
		
	def setLang(self,lang):
		self.lang = lang
		
	def getSZ(self):
		return self.sz
	
	def getLine(self,i):
		if i<self.sz and i>=0: 
			return self.code[i]
		return ''
	
	def walk(self):
		return range(0, self.sz)

	def setCode(self,code):
		self.code = code
		print('removing comments...')
		self.removeAllComments()
		self.sz = len(self.code)
		
		print('removing headers')
		self.removeHeaderAndTail()
		self.sz = len(self.code)
		
		print('identifying functions')
		self.identifyFunctions()
		self.sz = len(self.code)
		

	def getCode(self):
		return self.code
	
	def identifyFunctions(self):
		pass
	
	def removeAllComments(self):
		newCode=[]
		for l in self.code:
			nl = self.removeComments(l)
			if nl != '':
				newCode.append(nl)
		self.code = newCode

	def setVar(self,pattern):
		self.r_var = re.compile(pattern)
		
	def setFunctionDef(self,pattern):
		self.r_fnDef = re.compile(pattern)
		
	def setClass(self,pattern):
		self.r_class = re.compile(pattern)
		
	def setInput(self,pattern):
		self.r_in = re.compile(pattern)
	
	def setInput2(self,pattern):
		self.r_in2 = re.compile(pattern)

	def setDangers(self,dangers):
		self.r_getDangerParams = re.compile('('+dangers.replace(',','|')+') *\(([^)]+)\)') 

	def getDangerParams(self,line):
		return self.r_getDangerParams.findall(line)

	def getVar(self,line):
		v = self.r_var.findall(line)
		if len(v)>0:
			if self.getInput(v[0]):
				return None
			return v[0]
		return None
	
	def getVarsN(self,l):
		return self.getVars(self.code[l])
	
	def getVars(self,line):
		vrs = self.r_var.findall(line)
		vrs2 = []
		for v in vrs:
			if self.uglyVarFix(v):
				vrs2.append(v)
		if len(vrs2) == 0:
			return None
		return vrs2
	
	def uglyVarFix(self,var): #LANGUAGE DEPENDENT
		if var == '$_GET':
			return False
		if var == '$_POST':
			return False
		if var == '$_SERVER':
			return False
		if var == '$_FILE':
			return False
		return True
		
	
	#deprecated
	def getInput(self,line):
		i = self.r_in.findall(line)
		if len(i)==1:
			if len(i[0])==2:
				return i[0][0]
		i = self.r_in2.findall(line)
		if len(i)==1:
			if len(i[0])==2:
				return i[0][0]
		return None

	def getInputsN(self,l):
		return self.getInputs(self.code[l])

	def getInputs(self,line):
		#TODO: por ahora solo lee un input, si hay varios leerlos.
		i = self.r_in.findall(line)
		if len(i)==1:
			if len(i[0])==2:
				return [i[0][0]]
		i = self.r_in2.findall(line)
		if len(i)==1:
			if len(i[0])==2:
				return [i[0][0]]
		return None


	def isTopN(self,i):
		return self.isTop(self.code[i])
	
	def isTop(self,line):
		if line == '-begin-':
			return True
		return False
	
	
	def isFunctionDefN(self,l):
		fn = self.r_fnDef.findall(self.code[l])
		if fn:
			return fn[0]
		return None
	
	
	def getFunctionParamsN(self,fn,l):
		f = re.findall(fn+' *\(([^\)]+)\)',self.code[l])
		if not f:
			return []
		return f[0].split(',')
	
	def isClassN(self,i):
		return self.isClass(self.code[i])
	
	def isClass(self,line):
		cls = self.r_class.findall(line)
		if cls:
			return cls
		return None
	
	def getAssignation(self, line, var):
		eq = line.split('=')
		if len(eq) != 2:
			return None
		if var not in eq[0]:
			return None
		return eq

	
	def isChangeVarN(self,i,var):
		return self.isChangeVar(self.code[i], var)
	
	def isChangeVar(self,line,var): #3
		eq = self.getAssignation(line, var)
		if not eq:
			return None
		return self.getVars(eq[1])
	
	
	def isChangeInputN(self,i,var):
		return self.isChangeInput(self.code[i], var) 
	
	def isChangeInput(self,line,var): #2
		eq = self.getAssignation(line, var)
		if not eq:
			return None
		return self.getInputs(line)
	
	def isChangeFunctionN(self,i,var):
		return self.isChangeFunction(self.code[i], var)
	
	def isChangeFunction(self,line,var): #1
		eq = self.getAssignation(line, var)
		if not eq:
			return None
		if '(' not in eq[1]:
			return None
		fns = self.r_fnCall.findall(eq[1])
		if len(fns)<0:
			return None
		return fns
	
	
	def getVarsOnReturnByFunctionName(self,fn): #dont use this, implement this  on backtrace
		l = self.getReturnLineByFunctionName(fn)
		if not l:
			return None
		
		return self.getVars(self.code[l])
		
	
	def getReturnLineByFunctionName(self,fn): #dependiente de php
		startFn = self.getLineByFunctionName(fn)
		if not startFn:
			return None
		for l in range(startFn,self.sz):
			if 'return' in self.code[l]:
				return l
		return None
	
	def getLineByFunctionName(self,fn): #dependiente de php
		for l in range(0,self.sz):
			if fn in self.code[l] and 'function' in self.code[l]:
				return l
		return None
		
	def locateFunctionCalls(self,fn):
		calls=[]
		for l in range(0,self.sz):
			if fn in self.code[l] and 'function' not in self.code[l]:
				calls.append(l)
		return calls
			
	
	def isChangeClassN(self,i,var):
		return self.isChangeClass(self.code[i], var)
	
	def isChangeClass(self,line,var):  #needed?
		eq = self.isAssignation(line, var)
		if not eq:
			return None
		return None

	def isAssignationN(self,l):
		return self.isAssignation(self.code[l])

	def isAssignation(self,line):
		if self.r_assign.findall(line):
			return True
		return False
	
	def checkLineDangerN(self,i):
		return self.checkLineDanger(self.code[i])
	
	def checkLineDanger(self,line): #
		'''
			If there is a danger function in the line, it gets all the params of the function.
			Then it looks for variables and inputs in this params. 
		'''
		if self._debug:
			print(line)
			
		p = self.getDangerParams(line)
		if len(p)==1:
			(fn,parm) = p[0]
			var = None
			inp = self.getInput(parm)
			if not inp:
				var = self.getVar(parm)
				if not var:
					fn = None
			return (fn,var,inp)
		return (None,None,None)
	

