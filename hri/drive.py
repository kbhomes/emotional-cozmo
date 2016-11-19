from . import system

import operator

class Drive(object):
    """ Represents a homeostatic drive or motivation for the robot """
    name = None

    def __init__(self, drive_system):
        self.drive_system = drive_system
        self.robot = drive_system.robot

        self.drive_min = -100
        self.drive_max = 100
        self.drive_level = 0
        
        self.range_overwhelmed = [self.drive_min, -30]
        self.range_underwhelmed = [30, self.drive_max]
        self.range_homeostatic = [self.range_overwhelmed[1], self.range_underwhelmed[1]]

        # TODO: Set properly once Affect class is introduced
        self.affect = None

    def is_overwhelmed(self):
        return self.range_overwhelmed[0] <= self.drive_level <= self.range_overwhelmed[1]

    def is_underwhelmed(self):
        return self.range_underwhelmed[0] <= self.drive_level <= self.range_underwhelmed[1]

    def is_homeostatic(self):
        return self.range_homeostatic[0] <= self.drive_level <= self.range_homeostatic[1]

    def update(self, elapsed):
        # TODO: Implement properly, calculating the drive
        pass


class RestDrive(Drive):
    """ The drive that motivates the system to get rest """
    name = 'rest-drive'
   
    def __init__(self, drive_system):
        super().__init__(drive_system)
        self.drive_level = self.drive_min

    def update(self, elapsed):
        self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))
        pass


class SoloDrive(Drive):
    """ The drive that motivates the system to play with toys """
    name = 'solo-drive'
   
    def __init__(self, drive_system):
        super().__init__(drive_system)
        self.drive_level = -10

    def update(self, elapsed):
        self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))


class SocialDrive(Drive):
    """ The drive that motivates the system to play with people """
    name = 'social-drive'
   
    def __init__(self, drive_system):
        super().__init__(drive_system)
        self.drive_level = 0

    def update(self, elapsed):
        self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))


class DriveSystem(system.System):
    """ System that manages the state of the robot's drives """
    
    def __init__(self, robot):
        super().__init__(robot)

        self.rest_drive = RestDrive(self)
        self.solo_drive = SoloDrive(self)
        self.social_drive = SocialDrive(self)
        self.drives = [self.rest_drive, self.solo_drive, self.social_drive]

        self.active_drive = self.social_drive

    def update(self, elapsed):
        # Update the various drives
        for drive in self.drives:
            drive.update(elapsed)

        # Re-compute the active drive
        new_active = max(self.drives, key=operator.attrgetter('drive_level'))

        if self.active_drive is not new_active:
            self.emit('active-drive-changed', self.active_drive, new_active)
            self.active_drive = new_active