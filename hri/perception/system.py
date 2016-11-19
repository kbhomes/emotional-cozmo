from .. import system
from . import stimulus
from . import releaser
from . import sensor

class PerceptionSystem(system.System):
    """ The perception system of the robot, containing sensors, stimuli, and releasers """

    def __init__(self, robot):
        super().__init__(robot)

        # Create a stimulus mapping
        self.stimuli = {
            'face-1': stimulus.FaceStimulus(self, 'face-1'),
            'toy-1': stimulus.ToyStimulus(self, 'toy-1'),
        }

        # Create a list of releasers
        self.releasers = [
            releaser.AbsenceOfDesiredStimulusReleaser(self),
            releaser.DesiredStimulusReleaser(self)
        ]
        self.active_releaser = self.releasers[0]

        # Initialize our sensors
        self.vision = sensor.Vision(self)

    def update(self, elapsed):
        # Update each stimulus
        for id, stim in self.stimuli.items():
            stim.update(elapsed)

        # Update each releaser
        for rel in self.releasers:
            rel.update(elapsed)

        # Update the sensors
        self.vision.update(elapsed)

        # Re-compute the active releaser
        new_active = max(self.releasers, key=lambda rel: rel.activation_level/rel.activation_threshold)
        if self.active_releaser is not new_active:
            self.emit('active-releaser-changed', self.active_releaser, new_active)
            self.active_releaser = new_active