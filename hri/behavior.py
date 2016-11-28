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


class BehaviorSystem(system.System):
    """ Represents the behavior system of the robot """

    def __init__(self, robot):
        super().__init__(robot)

        self.behaviors = [
            RejectStimulusBehavior(self)
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
            self.active_behavior.is_active = False
            new_active.is_active = True

            self.emit('active-behavior-changed', self.active_behavior, new_active)
            self.active_behavior = new_active