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
            releaser.DesiredStimulusReleaser(self),
            releaser.UnderwhelmedDriveReleaser(self),
            releaser.OverwhelmedDriveReleaser(self),
        ]

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