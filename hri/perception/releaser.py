class Releaser(object):
    """ Represents a releaser process in the perception system """
    name = 'releaser'

    def __init__(self, perception_system):
        self.perception_system = perception_system

        self.activation_level = 0
        self.activation_threshold = 100
        self.affect = None

        self.active_duration = 0

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
            self.activation_level = self.activation_threshold + 5 * stimulus.disappearance_duration
        else:
            self.activation_level = 0

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (-500 - (self.active_duration*5), -500 - (self.active_duration*5), -500 - (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None


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
            self.activation_level = self.activation_threshold + 5 * stimulus.detection_duration
        else:
            self.activation_level = 0

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (1000 + (self.active_duration*5), 1000 + (self.active_duration*5), 500 + (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None


class UndesiredStimulusReleaser(Releaser):
    """ Releaser for not detecting the stimulus we want, but getting another one

    [ ] Drive:
          - `solo-drive` is looking for a toy stimulus
          - `social-drive` is looking for a face stimulus

    [ ] Behavior:
    
    """
    name = 'undesired-stimulus-releaser'

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

        # If the stimulus this drive expects was detected, then we will not activate
        if stimulus and stimulus.detected:
            self.activation_level = 0
        else:
            # If the expected stimulus didn't exist, but at least one was found, activate
            stimulus = next(iter([stimulus for id, stimulus in self.perception_system.stimuli.items() if stimulus.detected] or []), None)

            if stimulus:
                self.activation_level = self.activation_threshold + 5 * stimulus.detection_duration
            else:
                self.activation_level = 0

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (-250 - (self.active_duration*5), -1000 - (self.active_duration*5), -500 - (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None


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

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (1000 + (self.active_duration*5), -500 - (self.active_duration*5), -500 - (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None


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

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (-1000 - (self.active_duration*5), -500 - (self.active_duration*5), -500 - (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None


class ThreateningStimulusReleaser(Releaser):
    """ Releaser for detecting a threatening stimulus

    [ ] Stimulus:
        - A `face-stimulus` moving with a speed faster than 300 mm/s
        - A `toy-stimulus` moving with a speed faster than 100 mm/s
    
    """
    name = 'threatening-stimulus-releaser'

    def update(self, elapsed):
        stimulus = None

        # Find the first stimulus that is above threshold
        for id, stim in self.perception_system.stimuli.items():
            if stim.detected and stim.type == 'toy-stimulus' and (stim.average_speed or 0) > 100:
                stimulus = stim
                break
            elif stim.detected and stim.type == 'face-stimulus' and (stim.average_speed or 0) > 300:
                stimulus = stim
                break

        # If a stimulus is above threshold
        if stimulus and stimulus.detected:
            mult = 40

            if self.activation_level < 100:
                mult = 40
            elif self.activation_level < 130:
                mult = 20
            else:
                mult = 5

            self.activation_level += mult * elapsed
        else:
            self.activation_level = max(0, self.activation_level - 40*elapsed)

        if self.is_active():
            self.active_duration += 0 #elapsed
            self.affect = (1000 + (self.active_duration*5), -1000 - (self.active_duration*5), -1000 - (self.active_duration*5))
        else:
            self.active_duration = 0
            self.affect = None