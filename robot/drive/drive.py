class Drive(object):
    """ Represents a homeostatic drive or motivation for the robot """

    def __init__(self, drive_system):
        self.drive_system = drive_system
        self.robot = drive_system.robot

        self.drive_min = -100
        self.drive_max = 100
        self.drive_level = 0
        
        self.range_overwhelmed = [self.drive_min, -30]
        self.range_homeostatic = [self.range_overwhelmed[1], self.range_underwhelmed[1]]
        self.range_underwhelmed = [30, self.drive_max]

        # TODO: Set properly once Affect class is introduced
        self.affect = None

    def update(self, elapsed: float):
        # TODO: Implement properly, calculating the drive
        pass