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
        self.range_homeostatic = [self.range_overwhelmed[1], self.range_underwhelmed[0]]

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

    def update(self, elapsed):
        self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))
        pass


class SoloDrive(Drive):
    """ The drive that motivates the system to play with toys 
    
    If this drive is active, and the desired-stimulus-releaser is active, then
    the drive_level will decrease (towards overwhelmed). Otherwise, it will increase.
    """
    name = 'solo-drive'
   
    def __init__(self, drive_system):
        super().__init__(drive_system)

    def update(self, elapsed):
        rel = self.drive_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        is_active = (self.drive_system.active_drive == self)

        if rel.is_active() and is_active:
            self.drive_level = min(self.drive_max, self.drive_level - (0.5 * elapsed))
        else:
            self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))


class SocialDrive(Drive):
    """ The drive that motivates the system to play with people """
    name = 'social-drive'
   
    def __init__(self, drive_system):
        super().__init__(drive_system)

    def update(self, elapsed):
        rel = self.drive_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        is_active = (self.drive_system.active_drive == self)

        if rel.is_active() and is_active:
            self.drive_level = min(self.drive_max, self.drive_level - (0.5 * elapsed))
        else:
            self.drive_level = min(self.drive_max, self.drive_level + (0.5 * elapsed))


class DriveSystem(system.System):
    """ System that manages the state of the robot's drives """
    
    def __init__(self, robot):
        super().__init__(robot)

        self.rest_drive = RestDrive(self)
        self.solo_drive = SoloDrive(self)
        self.social_drive = SocialDrive(self)
        self.drives = [self.rest_drive, self.solo_drive, self.social_drive]

        self.rest_drive.drive_level = -100      # Overwhelmed
        self.solo_drive.drive_level = 20       # Homeostatic
        self.social_drive.drive_level = 35      # Underwhelmed

        self.active_drive = self.social_drive


    def drive_intensity(self, drive):
        # Ignore an overwhelmed rest-drive
        if drive == self.rest_drive and drive.is_overwhelmed():
            return 0
        else:
            return abs(drive.drive_level)


    def update(self, elapsed):
        # Update the various drives
        for drive in self.drives:
            drive.update(elapsed)

        # If the active drive is not within the homeostatic range, then keep it active
        if not self.active_drive.is_homeostatic():
            return

        # Re-compute the most intense drive (ignoring overwhelmed rest-drive)
        most_intense = max(self.drives, key=lambda drive: self.drive_intensity(drive))

        # If the most intense drive is homeostatic, then do nothing
        if most_intense.is_homeostatic():
            return

        if self.active_drive != most_intense:
            self.emit('active-drive-changed', self.active_drive, most_intense)
            self.active_drive = most_intense