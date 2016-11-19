from . import system

from timeit import default_timer as timeit

class Stimulus(object):
    """ Represents a perceivable stimulus """
    type = 'stimulus'

    def __init__(self, perception_system, id):
        self.perception_system = perception_system

        self.id = id
        self.detected = False
        
        self.last_detection = None
        self.detection_duration = 0

        self.last_disappearance = None
        self.disappearance_duration = 0

    def detect(self):
        """ Update the detection attributes """
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