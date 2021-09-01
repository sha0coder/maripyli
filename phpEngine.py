
from engine import *

class PHPEngine(Engine):
	
	def init(self): 
		self.setLang('php')
		self.setInput('(\$_(GET|POST|SERVER|FILE|FILES|COOKIE|REQUEST)\[["\'][a-zA-Z_0-9]+["\']\])')
		self.setInput2('(\$(HTTP_RAW_POST_DATA|http_response_header|argc|argv)[^a-zA-Z_0-9])')
		self.setVar('\$[a-zA-Z_0-9>-]+')  #TODO: arrays
		
		self.setFunctionDef('function +([^ \(]+) *\(')
		
		self.setClass('class  *')
		self.setDangers('eval,assert,ReflectionFunction,create_function,system,passthru,exec,shell_exec,mysql_query,popen,apache_setenv,closelog,openlog,pclose,file_get_contents,file_put_contents,fopen,bzopen,gzopen,chmod,chown,pcntl_exec,proc_nice,pfsockopen,posix_mkfifo,proc_open,syslog,url_exec,include,include_once,require,require_once,ini_restored,unserialize,file_exists,preg_replace,preg_match,`,phpinfo,getcwd,posix_getlogin,putenv,ini,fsockopen,ftp_get,ftp_nb_get,ftp_put,show_source,call_user_func_array,runkit_function_rename,call_user_func,pcntl_signal,pcntl_alarm,register_tick_function,register_shutdown_function,dl,debugger_on,openlog,apache_note,apache_setenv')
		# http://stackoverflow.com/questions/3115559/exploitable-php-functions
		self.r_inlineComments = re.compile('\/\/.*')
		self.r_multilineComments = re.compile('\/\*.*\*\/')
		self.r_multiline2Comments = re.compile('\/\*.*')
		
	def removeComments(self,line):
		line = self.r_inlineComments.sub('',line)
		line = self.r_multilineComments.sub('',line)
		if '*/' not in line:
			line = self.r_multiline2Comments.sub('',line)
		return line
		
	def removeHeaderAndTail(self):
		for i in self.walk():
			if self.code[i] == '<?php':
				self.code[i] = '-begin-'
			elif self.code[i] == '?>':
				self.code[i] = '-eof-'

			
#### TEST ####

def changeFunction_Test(php):
	assert(php.isChangeFunction('$a = aa(bb(cc(dd(1,2),3),4),5)','$a') == ['aa','bb','cc','dd'])
	assert(php.isChangeFunction('$a = test($b)','$a') == ['test'])
	assert(php.isChangeFunction('$a = test($b)','$a') == ['test'])
	print('changeFunction test ok!!')

def changeInput_Test(php):
	assert(php.isChangeInput('$a = $_GET["sdf"]','$a') 			== '$_GET["sdf"]')
	assert(php.isChangeInput("$a33 = $_POST['sdf']",'$a33') 	== "$_POST['sdf']")
	assert(php.isChangeInput('$a = $_B','$a')    				== None)	
	print('changeInput test ok!')

def changeVar_Test(php):
	assert(php.isChangeVar('if ($a==$b) {', '$a') 			== None)
	assert(php.isChangeVar('$a = "b"','$a') 				== None)
	assert(php.isChangeVar('$a=$b;','$a')					== ['$b'])
	assert(php.isChangeVar('$a = $b . $c','$a')				== ['$b','$c'])
	assert(php.isChangeVar('$a = substr($b,1,2)','$a') 		== ['$b'])
	assert(php.isChangeVar('$a = $_GET["sdf"]','$a') 		== None)
	print('ChangeVar test ok!')


def checkLine_Test(php):
	assert(php.checkLine('system($a23);') 					== ('system','$a23',None))
	assert(php.checkLine('system($_GET["asdf"]);') 			== ('system',None,'$_GET["asdf"]'))
	assert(php.checkLine("system ($_GET['asdf']);") 		== ('system',None,"$_GET['asdf']"))
	assert(php.checkLine("system (  $_FILE['a']  );") 		== ('system',None,"$_FILE['a']"))
	assert(php.checkLine("system('sdf'.$a23);") 			== ('system','$a23',None))
	assert(php.checkLine("system('sdfa23');") 				== (None,None,None))
	assert(php.checkLine("system($a23.'asdf');") 			== ('system','$a23',None))
	assert(php.checkLine("system('sdf' . $a23 . 'asdf');") 	== ('system','$a23',None))
	assert(php.checkLine("system ($a23.'asdf');") 			== ('system','$a23',None))
	assert(php.checkLine("syste($a);") 						== (None,None,None))
	assert(php.checkLine('system("c");') 					== (None,None,None))
	assert(php.checkLine("system('a','b');") 				== (None,None,None)) 
	print('checkLine test ok!')


if __name__ == '__main__':
	php = PHPEngine()
	php.init()
	checkLine_Test(php)
	changeVar_Test(php)
	changeInput_Test(php)
	changeFunction_Test(php)






