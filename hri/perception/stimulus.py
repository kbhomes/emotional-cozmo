from . import system

from collections import deque
from timeit import default_timer as timeit
import math

class Stimulus(object):
    """ Represents a perceivable stimulus """
    type = 'stimulus'

    def __init__(self, perception_system, id):
        self.perception_system = perception_system

        self.id = id
        self.detected = False
        self.detected_object = None
        self.last_detected_poses = deque(maxlen=10)
        self.last_detected_elapsed = deque(maxlen=9)
        self.average_speed = None
        
        self.last_detection = None
        self.detection_duration = 0

        self.last_disappearance = None
        self.disappearance_duration = 0

    def compute_distance(self, posA, posB):
        return math.sqrt((posB.x - posA.x)**2 + (posB.y - posA.y)**2 + (posB.y - posA.y)**2)

    def compute_average_speed(self):
        total_distance = 0
        total_time = 0

        # Wait until the poses are filled out
        if len(self.last_detected_poses) != self.last_detected_poses.maxlen:
            return None

        for i in range(self.last_detected_elapsed.maxlen):
            total_distance += self.compute_distance(self.last_detected_poses[i].position, self.last_detected_poses[i+1].position)
            total_time += self.last_detected_elapsed[i]

        return total_distance / total_time

    def detect(self, detected_object, elapsed):
        """ Update the detection attributes """
        self.detected_object = detected_object
        self.last_detected_poses.append(detected_object.pose)
        self.last_detected_elapsed.append(elapsed)
        self.average_speed = self.compute_average_speed()

        if not self.detected:
            self.detected = True
            self.last_detection = timeit()
            self.detection_duration = 0
            self.perception_system.emit('stimulus-detected', self)

    def disappear(self):
        """ Update the disappearance attributes """
        if self.detected:
            self.detected = False
            self.last_disappearance = timeit()
            self.disappearance_duration = 0
            self.detected_object = None
            self.last_detected_poses.clear()
            self.last_detected_elapsed.clear()
            self.average_speed = None
            self.perception_system.emit('stimulus-disappeared', self)

    def update(self, elapsed):
        """ Update the timing attributes """
        if self.detected:
            self.detection_duration += elapsed
        else:
            self.disappearance_duration += elapsed

class FaceStimulus(Stimulus):
    type = 'face-stimulus'

class ToyStimulus(Stimulus):
    type = 'toy-stimulus'