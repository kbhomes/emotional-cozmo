import pyee

class System(pyee.EventEmitter):
    """ A system object that has access to its robot """

    def __init__(self, robot):
        super().__init__()
        
        self.robot = robot

    def update(self, elapsed):
        pass
