class Releaser(object):
    """ Represents a releaser process in the perception system """
    name = 'releaser'

    def __init__(self, perception_system):
        self.perception_system = perception_system

        self.activation_level = 0
        self.activation_threshold = 100
        self.affect = None

    def is_active(self):
        return self.activation_level >= self.activation_threshold
    
    def update(self, elapsed):
        """ Computes the activation level and affect for the releaser """
        raise NotImplementedError()


class AbsenceOfDesiredStimulusReleaser(Releaser):
    """ Releaser for looking for an appropriate stimulus and not seeing it, using:

    [ ] Drive:
          - `solo-drive` is looking for a toy stimulus
          - `social-drive` is looking for a face stimulus

    [ ] Behavior:
    
    """
    name = 'absence-of-desired-stimulus-releaser'

    def update(self, elapsed):
        drive = self.perception_system.robot.drive_system.active_drive
        stimulus = None

        # Don't operate on the rest-drive
        if drive.name == 'rest-drive':
            return

        # Find the first appropriate stimulus for this type
        for id, stim in self.perception_system.stimuli.items():
            if drive.name == 'solo-drive':
                if stim.type == 'toy-stimulus':
                    stimulus = stim
                    break
            elif drive.name == 'social-drive':
                if stim.type == 'face-stimulus':
                    stimulus = stim
                    break

        if not (stimulus and stimulus.detected):
            self.activation_level = 5 * stim.disappearance_duration
        else:
            self.activation_level = 0


class DesiredStimulusReleaser(Releaser):
    """ Releaser for looking for an appropriate stimulus and detecting it, using:

    [ ] Drive:
          - `solo-drive` is looking for a toy stimulus
          - `social-drive` is looking for a face stimulus

    [ ] Behavior:
    
    """
    name = 'desired-stimulus-releaser'

    def update(self, elapsed):
        drive = self.perception_system.robot.drive_system.active_drive
        stimulus = None

        # Don't operate on the rest-drive
        if drive.name == 'rest-drive':
            return

        # Find the first appropriate stimulus for this type
        for id, stim in self.perception_system.stimuli.items():
            if drive.name == 'solo-drive':
                if stim.type == 'toy-stimulus':
                    stimulus = stim
                    break
            elif drive.name == 'social-drive':
                if stim.type == 'face-stimulus':
                    stimulus = stim
                    break

        if stimulus and stimulus.detected:
            self.activation_level = 5 * stim.detection_duration
        else:
            self.activation_level = 0


class OverwhelmedDriveReleaser(Releaser):
    """ Releaser for detecting if the active drive is overstimulated """
    name = 'overwhelmed-drive-releaser'

    def update(self, elapsed):
        drive = self.perception_system.robot.drive_system.active_drive
        
        if drive.is_overwhelmed():
            overwhelmed_amount = drive.range_overwhelmed[1] - drive.drive_level
            overwhelmed_span = drive.range_overwhelmed[1] - drive.range_overwhelmed[0]
            self.activation_level = self.activation_threshold + (overwhelmed_amount/overwhelmed_span)*10
        else:
            self.activation_level = 0


class UnderwhelmedDriveReleaser(Releaser):
    """ Releaser for detecting if the active drive is understimulated """
    name = 'underwhelmed-drive-releaser'

    def update(self, elapsed):
        drive = self.perception_system.robot.drive_system.active_drive
        
        if drive.is_underwhelmed():
            underwhelmed_amount = drive.drive_level - drive.range_underwhelmed[0]
            underwhelmed_span = drive.range_underwhelmed[1] - drive.range_underwhelmed[0]
            self.activation_level = self.activation_threshold + (underwhelmed_amount/underwhelmed_span)*10
        else:
            self.activation_level = 0