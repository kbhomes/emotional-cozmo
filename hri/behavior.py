from . import system

import operator

class Behavior(object):
    """ Represents a behavior that the robot should enact """
    name = None

    def __init__(self, behavior_system):
        self.behavior_system = behavior_system

        self.activation_level = 0
        self.activation_threshold = 100
        self.is_active = False
        self.last_activated = None
        self.activation_duration = 0

    def update(self, elapsed):
        """ Updates activation level based on emotions, drives, and releasers """
        raise NotImplementedError()


class RejectStimulusBehavior(Behavior):
    """ Behavior that tries to avoid a stimulus that it has been shown """
    name = 'reject-stimulus-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system);

    def update(self, elapsed):
        """ Activates if the undesired-stimulus-releaser is active """
        delta = 5 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('undesired-stimulus-releaser')

        if rel.is_active():
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class EscapeStimulusBehavior(Behavior):
    """ Behavior that tries to escape a stimulus that it has been shown """
    name = 'escape-stimulus-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system);

    def update(self, elapsed):
        """ Activates if the undesired-stimulus-releaser is active and the fear emotion is active """
        delta = 8 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('undesired-stimulus-releaser')
        fear = self.behavior_system.robot.emotion_system.emotion_fear

        if rel.is_active() and self.behavior_system.robot.emotion_system.active_emotion == fear:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class PlayWithToyBehavior(Behavior):
    """ Behavior that tries to engage and play with a toy stimulus """
    name = 'play-with-toy-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system);

    def update(self, elapsed):
        """ Activates if the desired-stimulus-releaser is active and the solo-drive is active """
        delta = 8 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        solo = self.behavior_system.robot.drive_system.solo_drive

        if rel.is_active() and self.behavior_system.robot.drive_system.active_drive == solo:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class EngageWithFaceBehavior(Behavior):
    """ Behavior that tries to engage with a face stimulus """
    name = 'engage-with-face-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system);

    def update(self, elapsed):
        """ Activates if the desired-stimulus-releaser is active and the social-drive is active """
        delta = 8 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        social = self.behavior_system.robot.drive_system.social_drive

        if rel.is_active() and self.behavior_system.robot.drive_system.active_drive == social:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class RestBehavior(Behavior):
    """ Behavior where robot tries to rest """
    name = 'rest-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system);

    def update(self, elapsed):
        """ Activates if the rest-drive is active """
        delta = 8 * elapsed
        rest = self.behavior_system.robot.drive_system.rest_drive

        if self.behavior_system.robot.drive_system.active_drive == rest:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class BehaviorSystem(system.System):
    """ Represents the behavior system of the robot """

    def __init__(self, robot):
        super().__init__(robot)

        self.behaviors = [
            RejectStimulusBehavior(self),
            EscapeStimulusBehavior(self),
            PlayWithToyBehavior(self),
            EngageWithFaceBehavior(self),
            RestBehavior(self),
        ]
        self.active_behavior = None

    def update(self, elapsed):
        """ Update all behaviors """
        
        for behavior in self.behaviors:
            behavior.update(elapsed)

        new_active = max(self.behaviors, key=operator.attrgetter('activation_level'))

        if new_active.activation_level < new_active.activation_threshold:
            new_active = None

        if new_active is not self.active_behavior:
            if self.active_behavior:
                self.active_behavior.is_active = False
            
            if new_active:
                new_active.is_active = True

            self.emit('active-behavior-changed', self.active_behavior, new_active)
            self.active_behavior = new_active