from . import drive
from . import perception

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

        self.perception_system = perception.PerceptionSystem(self)
        self.perception_system.on('stimulus-detected', self.on_stimulus_detected)
        self.perception_system.on('stimulus-disappeared', self.on_stimulus_disappeared)

        # Set up the update loop
        self.update_event = threading.Event()
        self.update_thread = threading.Thread(target=self.robot_thread)
        self.update_thread.start()

    def on_active_drive_changed(self, previous_drive, new_drive):
        pass
        # print('Drive changed from `{}` to `{}'.format(previous_drive.name, new_drive.name))

    def on_stimulus_detected(self, stimulus):
        pass
        # print('Stimulus detected: {} (was not detected for {}s)'.format(stimulus.id, stimulus.disappearance_duration))

    def on_stimulus_disappeared(self, stimulus):
        pass
        # print('Stimulus disappeared: {} (was detected for {}s)'.format(stimulus.id, stimulus.detection_duration))

    def stop(self):
        self.update_event.set()

    def robot_thread(self):
        while not self.update_event.wait(0.1):
            now = timeit()
            elapsed = now - self.last_update
            self.last_update = now

            # Update the systems
            self.drive_system.update(elapsed)
            self.perception_system.update(elapsed)