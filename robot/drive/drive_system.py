from .. import Robot, System

class DriveSystem(System):
    """ System that manages the state of the robot's drives """
    
    def __init__(self, robot: Robot):
        super().__init__(robot)