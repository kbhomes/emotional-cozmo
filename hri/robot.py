from . import drive
from . import perception
from . import emotion
from . import behavior

import cozmo as cozmosdk
import threading
import sys
import logging
import asyncio
from timeit import default_timer as timeit

class Robot(object):
    """ Robot class composed of all systems representing the robot's state """

    def __init__(self, logger):
        self.logger = logger
        self.last_update = timeit()

        # Set up the drives
        self.drive_system = drive.DriveSystem(self)
        self.drive_system.on('active-drive-changed', self.on_active_drive_changed)

        self.perception_system = perception.PerceptionSystem(self)
        self.perception_system.on('stimulus-detected', self.on_stimulus_detected)
        self.perception_system.on('stimulus-disappeared', self.on_stimulus_disappeared)

        self.emotion_system = emotion.EmotionSystem(self)
        self.emotion_system.on('active-emotion-changed', self.on_active_emotion_changed)

        self.behavior_system = behavior.BehaviorSystem(self)

        # Set up the update loop
        self.connected_event = threading.Event()
        self.update_event = threading.Event()
        self.update_thread = threading.Thread(target=self.robot_thread)

    def on_active_drive_changed(self, previous_drive, new_drive):
        self.logger.info('Drive changed from {} to {}'.format(previous_drive.name, new_drive.name))

    def on_stimulus_detected(self, stimulus):
        self.logger.info('Stimulus detected: {} (was not detected for {:.1f}s)'.format(stimulus.id, stimulus.disappearance_duration))

    def on_stimulus_disappeared(self, stimulus):
        self.logger.info('Stimulus disappeared: {} (was detected for {:.1f}s)'.format(stimulus.id, stimulus.detection_duration))

    def on_active_emotion_changed(self, previous_emotion, new_emotion):
        previous_id = previous_emotion.name if previous_emotion else '(none)'
        new_id = new_emotion.name if new_emotion else '(none)'
        self.logger.info('Emotion changed from {} to {}'.format(previous_id, new_id))

    def start(self, use_cozmo = False):
        self.use_cozmo = use_cozmo
        self.update_thread.start()

    def stop(self):
        self.update_event.set()

    def robot_connected(self, conn):
        if conn:
            self.cozmo = conn.wait_for_robot()

        while not self.update_event.wait(0.05):
            now = timeit()
            elapsed = now - self.last_update
            self.last_update = now

            # Update the systems
            self.drive_system.update(elapsed)
            self.perception_system.update(elapsed)
            self.emotion_system.update(elapsed)
            self.behavior_system.update(elapsed)

    def robot_thread(self):
        if self.use_cozmo:
            cozmosdk.setup_basic_logging()
            cozmosdk.connect(lambda conn: self.robot_connected(conn))
        else:
            self.robot_connected(None)