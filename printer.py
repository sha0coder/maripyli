import sys

class Pr:

	def open(self, msg):
		sys.stdout.write('* %s ... ' % msg)
		sys.stdout.flush()

	def close(self, success):
		if success:
			print('[Ok]')
		else:
			print('[!!]')



