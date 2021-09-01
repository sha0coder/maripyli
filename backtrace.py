# PRIVATE!!!
# (C) By @sha0coder

from async import *

'''
	Current Limitations:
		- poor visualization, need colors at least on danger, monitored vars, and inputs
		- respect parameters order, for follwing the vars when tracing function calls
		- do not follow includes
		- do not support oop (maybe adding -> to regexp of vars)
		- a couple of bugs
		- should add more dangers
		- should add more inputs (all interesting server items)
		- should consider the php sanitization functions
		- should precompute length of eng.code
		- two functions with same name
		- multiple inputs in one line, only cosider the first
		- review all return True/False
'''

MAX_RECURSION = 600

color = {
        'clean'   : '\033[0m',  # Clear color
        'clear'   : '\033[2K',  # Clear line
        'bold'      : ['\033[1m',  '\033[22m'],
        'italic'    : ['\033[3m',  '\033[23m'],
        'underline' : ['\033[4m',  '\033[24m'],
        'inverse'   : ['\033[7m',  '\033[27m'],

        #grayscale
        'white'     : ['\033[37m', '\033[39m'],
        'grey'      : ['\033[90m', '\033[39m'],
        'black'     : ['\033[30m', '\033[39m'],

        #colors
        'blue'      : ['\033[34m', '\033[39m'],
        'cyan'      : ['\033[36m', '\033[39m'],
        'green'     : ['\033[32m', '\033[39m'],
        'magenta'   : ['\033[35m', '\033[39m'],
        'red'       : ['\033[31m', '\033[39m'],
        'yellow'    : ['\033[33m', '\033[39m']
}

class BackTrace(Async):

	#remarcar:  wp_unslash
		
	def setDebug(self,debug):
		self._dbg = debug
		
	def setProject(self,proj):
		self.proj = proj	
	
	def setEngine(self,eng):
		self.eng = eng

	def setVar(self,var):
		self.var = var
		
	def setLine(self,l):
		self.line = l
		
	def anyOnAny(self,arr1,arr2):
		for a1 in arr1:
			if a1 in arr2:
				return a1
		return None
		
	def traceVars(self,l,varss,recursion):
		eng = self.eng
		if recursion > MAX_RECURSION:
			print('to much recursion...')
			return True
		
		while self.isRunning:	
			l -= 1
			if l<0:
				return False #??
			line = eng.getLine(l)
			if self._dbg:
				print('==>%s' % line)
			
			for var in varss:
				
				if var in line:
					self.log('%s: \t%s' % (var,line))
					if eng.isAssignationN(l):
						
						variables = eng.isChangeVarN(l,var)
						if variables:
							#remove assigned variable
							varss.remove(var)
							
							#add only new non repeated vars
							for vrs in variables:
								if vrs not in varss and vrs not in '$this':
									varss.append(vrs)
							
							self.log('monitor vars:\t%s' % ','.join(varss))
							#continue
						
						inp = eng.isChangeInputN(l,var)
						if inp:
							'''
								The best exit of the laberinth
							'''
							self.logVector(','.join(inp))
							self.displayLog()
							return True
							
						
							
							
						fns = eng.isChangeFunctionN(l,var) #TODO: multiple functions
						if fns:
							if len(fns)==1:
								#self.log('changefunction: %s' % fns)
								ln = eng.getReturnLineByFunctionName(fns[0])
								if ln:
									retVars = eng.getVarsN(ln)
									if retVars:
										self.log('entrando en '+fns[0])
										shouldEnd = self.traceVars(ln, retVars, recursion+1)
										if shouldEnd:
											return True
										self.log('saliendo de '+fns[0])
										'''
											If returned, we have to add to the vars to trace the param of the function
										
										try: 
											params = line.split('(')[1]
											variables = eng.getVars(params)
											varss.remove(var)
											varss += variables
										except:
											pass
											
										print(line)
										print(line)
										'''
							
							else:
								self.log('multiple funcion inside each other not supported by now.')
								if self._dbg:
									self.displayLog()
								return True
					
					else:
						
						x = eng.isFunctionDefN(l)
						if x:
							if recursion>0:
								'''
									A child trace, reach the function definition, and
									the function definition has the variable,
									then should return and continue the flow.
								'''
								return False
							else:
								'''
									TODO:
									We must trace all calls to this function, becouse
									any of the trace vars ar in the parameters.
									
									This case is for ifs, php funcitons, etc.
								'''
								#self.log('must trace all function calls')
								return True
						
						self.log('opera con las variables sin asignarlas: %s' % line)
						continue
					
					
				else:
					#TODO: continuar el backtrace en estas situaciones:
					
					x = eng.isTopN(l) 
					if x:
						if recursion>0:
							return False
						else:
							self.log('TODO: follow tracing on inclussions')
							if self._dbg:
								self.displayLog()
							self.stop()
							return True
					
					x = eng.isClassN(l)
					if x: 
						if recursion>0:
							return False
						else:
							self.log('the vulnerbility is in the class %s' % x)
							self.log('TODO: follow all this class usages.')
							if self._dbg:
								self.displayLog()
							self.stop()
							return True
					
					fn = eng.isFunctionDefN(l)
					if fn:
						if recursion>0:
							'''
								We reached the function definition and no trace vars are on arguments.
								this child should return here.
							'''
							self.log('nothing interesting on '+fn)
							return False
						else:
							'''
								We reached the function definition and no trace vars are on arguments.
								trace should finish here.
							'''
							params = eng.getFunctionParamsN(fn,l)
							for p in params:
								if p in varss:
									self.log('follow %s function calls and its calling parameters, here we can loss accuracy because do not guarantee the param position' % fn)
									
									'''
										The btracer is inside a function definition, who has params, 
										by now no care about parameter possitions, TODO: take care of it.
										we will btace all the params of all the callers... here we loss accuracy.  
									'''
									
									calls = eng.locateFunctionCalls(fn)
									for call in calls:
										prms = eng.getFunctionParamsN(fn,call)
										if len(prms)>0:
											if eng.getInputsN(call):
												self.logVector(line)
												self.displayLog()
												self.stop()
												return True
											else:
												self.log(color['green'][0]+'<tracing caller>'+color['clean'])
												self.traceVars(call, prms, recursion+1)
												self.log(color['green'][0]+'</tracing caller>'+color['clean'])
									
									#TODO: trace all fn's
									if self._dbg:
										self.displayLog()
									return True 
								
							self.log('It seems no way to reach the vulnerability, which is in %s' % x)
							if self._dbg:
								self.displayLog()
							self.stop()
							return True


	def clearLog(self):
		self.trace=[]
		self.log(color['green'][0]+' <btrace %s>' % self.proj+color['clean'])
		
	def displayLog(self):
		self.log(color['green'][0]+' </btrace>'+color['clean'])
		print("\n(B)"+"\n(B)".join(self.trace)+"\n")
	
	def logVector(self,msg):
		rmsg = color['red'][0]+' /!\ /!\ Attack Vectors: '+msg+color['clean']
		self.trace.append(rmsg)
		
	def logDanger(self,msg):
		rmsg = color['red'][0]+' /!\ /!\ Danger: '+msg+color['clean']
		self.trace.append(rmsg)
		
	
	def log(self,msg):
		if 'btrace>' in msg:
			self.trace.append(color['green'][0]+msg+color['clean'])
		else:
			self.trace.append(' '+msg)

	def run(self):
		self.isRunning = True
		self.clearLog()
		
		l = self.line
		var = self.var
		
		self.logDanger(self.eng.getLine(l))
		
		if self.eng.getInputsN(l):
			self.logVector(self.eng.getLine(l))
			self.displayLog()
			self.stop()
			return
		
		self.traceVars(l, [var], 0) # -1 for checking the danger line too
				
				
				
				
				
