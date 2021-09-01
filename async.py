from threading import Thread

class Async(Thread):
    def __init__(self,data=None):
        self.data = data
        Thread.__init__(self)
        self.daemon = True
        self.isRunning = False


    def stop(self):
        self.isRunning = False;
        
    def wait(self):
        try:
            while self.isRunning and self.isAlive():
                self.join(10)
        except KeyboardInterrupt:
            self.stop()
