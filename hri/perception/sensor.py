import random
import math

from . import stimulus

class Vision(object):
    """ Interacts with the vision sensor and records stimuli """

    def __init__(self, perception_system):
        self.perception_system = perception_system

        self.face_disappearance_timeout = 3 # seconds
        self.toy_disappearance_timeout = 3 # seconds

        # For testing!
        self.test_face_target = random.randint(-100, 100)
        self.test_face_current = 0
        self.test_toy_target = random.randint(-100, 100)
        self.test_toy_current = 0

    def update(self, elapsed):
        robot = self.perception_system.robot
        cozmo = robot.cozmo

        # If the robot sees any faces, mark 'face-1' as detected:
        first_face = next(cozmo.world.visible_faces, None)
        if first_face:
            self.face_disappearance_timeout = 3
            self.perception_system.stimuli['face-1'].detect(first_face, elapsed)
        else:
            self.face_disappearance_timeout -= elapsed
            if self.face_disappearance_timeout <= 0:
                self.perception_system.stimuli['face-1'].disappear()

        # If the robot sees any blocks, mark 'face-1' as detected:
        first_block = next(cozmo.world.visible_objects, None)
        if first_block:
            self.toy_disappearance_timeout = 3
            self.perception_system.stimuli['toy-1'].detect(first_block, elapsed)
        else:
            self.toy_disappearance_timeout -= elapsed
            if self.toy_disappearance_timeout <= 0:
                self.perception_system.stimuli['toy-1'].disappear()

        pass

    def test_update(self, elapsed):
        """ Generate random detections and disappearances for a stimulus """
        if self.test_face_current == self.test_face_target:
            self.test_face_target = random.randint(-100, 100)

        if self.test_toy_current == self.test_toy_target:
            self.test_toy_target = random.randint(-100, 100)

        delta_face = min(math.floor(random.randint(0, 40) * elapsed), abs(self.test_face_target - self.test_face_current))
        delta_toy = min(math.floor(random.randint(0, 40) * elapsed), abs(self.test_toy_target - self.test_toy_current))
        
        if self.test_face_current < self.test_face_target:
            self.test_face_current += delta_face
        else:
            self.test_face_current -= delta_face
        
        if self.test_toy_current < self.test_toy_target:
            self.test_toy_current += delta_toy
        else:
            self.test_toy_current -= delta_toy

        # Generate events based upon this smooth randomness
        if self.test_face_current > 0:
            self.perception_system.stimuli['face-1'].detect()
        else:
            self.perception_system.stimuli['face-1'].disappear()

        if self.test_toy_current > 0:
            self.perception_system.stimuli['toy-1'].detect()
        else:
            self.perception_system.stimuli['toy-1'].disappear()