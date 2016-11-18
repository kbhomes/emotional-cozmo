from . import drive

import threading
import sys
from timeit import default_timer as timeit

class Robot(object):
    """ Robot class composed of all systems representing the robot's state """

    def __init__(self):
        self.last_update = timeit()

        # Set up the drives
        self.drive_system = drive.DriveSystem(self)
        self.drive_system.on('active-drive-changed', self.on_active_drive_changed)

        # Set up the update loop
        self.update_event = threading.Event()
        self.update_thread = threading.Thread(target=self.robot_thread)
        self.update_thread.start()

    def on_active_drive_changed(self, previous_drive, new_drive):
        print('Drive changed from `{}` to `{}'.format(previous_drive.name, new_drive.name))

    def stop(self):
        self.update_event.set()

    def robot_thread(self):
        while not self.update_event.wait(0.1):
            now = timeit()
            elapsed = now - self.last_update
            self.last_update = now

            # Update the systems
            self.drive_system.update(elapsed)