from .. import system
from . import stimulus
from . import sensor

class PerceptionSystem(system.System):
    """ The perception system of the robot, containing sensors, stimuli, and releasers """

    def __init__(self, robot):
        super().__init__(robot)

        # Create a stimulus mapping
        self.stimuli = dict()

        # Initialize our sensors
        self.vision = sensor.Vision(self)

    def update(self, elapsed):
        # Update each stimulus
        for id, stim in self.stimuli.items():
            stim.update(elapsed)

        # Update the sensors
        self.vision.update(elapsed)