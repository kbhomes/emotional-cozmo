import robot.drive

class Robot(object):
    """ Robot class composed of all systems representing the robot's state """

    def __init__(self):
        self.drive_system = drive.DriveSystem()