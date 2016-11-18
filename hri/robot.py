from . import drive

import threading
import sys
from timeit import default_timer as timeit

class Robot(object):
    """ Robot class composed of all systems representing the robot's state """

    def __init__(self):
        self.drive_system = drive.DriveSystem(self)
        self.last_update = timeit()

        self.update_event = threading.Event()
        self.update_thread = threading.Thread(target=self.robot_thread)
        self.update_thread.start()

    def stop(self):
        self.update_event.set()

    def robot_thread(self):
        while not self.update_event.wait(0.1):
            now = timeit()
            elapsed = now - self.last_update
            self.last_update = now

            # Update the systems
            self.drive_system.update(elapsed)

            # Output
            print('Tick (after {} seconds)'.format(elapsed))
            sys.stdout.flush()
        
