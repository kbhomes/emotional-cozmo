from . import system

import operator
import random
import cozmo as cozmosdk
from timeit import default_timer as timeit

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

    def activate(self):
        pass

    def deactivate(self):
        pass

    def update(self, elapsed):
        """ Updates activation level based on emotions, drives, and releasers """
        raise NotImplementedError()


class SearchForStimulusBehavior(Behavior):
    """ Behavior that tries to search for stimuli if the absence-of-desired-stimulus-releaser
        is active (looking for a toy with the solo-drive or a face with the social-drive) """
    name = 'search-for-stimulus-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system)

        self.search_behavior = None

    def activate(self):
        """ Determine the type of stimulus that should be looked for """
        self.robot = self.behavior_system.robot
        self.cozmo = self.robot.cozmo

        active_drive = self.robot.drive_system.active_drive

        if active_drive.name == 'solo-drive':
            # Look for a toy/block
            self.search_behavior = self.cozmo.start_behavior(cozmosdk.behavior.BehaviorTypes.LookAroundInPlace)
        elif active_drive.name == 'social-drive':
            # Look for a face
            self.search_behavior = self.cozmo.start_behavior(cozmosdk.behavior.BehaviorTypes.FindFaces)

    def deactivate(self):
        """ Deactivate the search behavior if it's active """
        if self.search_behavior:
            self.search_behavior.stop()

    def update(self, elapsed):
        """ Activates if the absence-of-desired-stimulus-releaser is active """
        delta = 10 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('absence-of-desired-stimulus-releaser')
        sorrow = self.behavior_system.robot.emotion_system.emotion_sorrow

        if rel.is_active() and self.behavior_system.robot.emotion_system.active_emotion == sorrow:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = 0


class RejectStimulusBehavior(Behavior):
    """ Behavior that tries to avoid a stimulus that it has been shown """
    name = 'reject-stimulus-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system)

        self.angry_anim = None
        self.neutral_anim = None
        self.look_action = None

    def activate(self):
        """ Show an upset expression """
        self.robot = self.behavior_system.robot
        self.cozmo = self.robot.cozmo

        # Play the animation
        try:
            self.angry_anim = self.cozmo.play_anim_trigger(cozmosdk.anim.Triggers.DriveStartAngry)
            self.angry_anim.on_completed(lambda evt, **kwargs: self._angry_anim_completed(evt))
        except:
            pass

    def _angry_anim_completed(self, evt):
        try:
            self.neutral_anim = self.cozmo.play_anim_trigger(cozmosdk.anim.Triggers.NeutralFace)
            self.neutral_anim.on_completed(lambda evt, **kwargs: self._neutral_anim_completed(evt))
        except:
            pass

    def _neutral_anim_completed(self, evt):
        try:
            self.look_action = self.cozmo.set_head_angle(cozmosdk.util.degrees(0))
        except:
            pass

    def deactivate(self):
        if self.angry_anim and self.angry_anim.is_running:
            self.angry_anim.abort()

        if self.neutral_anim and self.neutral_anim.is_running:
            self.angry_anim.abort()

        if self.look_action and self.look_action.is_running:
            self.look_action.abort()

    def update(self, elapsed):
        """ Activates if the undesired-stimulus-releaser is active """
        delta = 18 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('undesired-stimulus-releaser')
        sorry = self.behavior_system.robot.emotion_system.emotion_sorrow

        if rel.is_active() and self.behavior_system.robot.emotion_system.active_emotion == sorry:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class EscapeStimulusBehavior(Behavior):
    """ Behavior that tries to escape a stimulus that it has been shown """
    name = 'escape-stimulus-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system)

        self.scared_anim = None
        self.drive_away_action = None
        self.turn_away_action = None

    def activate(self):
        self.robot = self.behavior_system.robot
        self.cozmo = self.robot.cozmo

        try:
            self.scared_anim = self.cozmo.play_anim_trigger(cozmosdk.anim.Triggers.DriveStartAngry)
            self.scared_anim.on_completed(lambda evt, **kwargs: self._scared_animation_completed(evt))
        except:
            pass

    def _scared_animation_completed(self, evt):
        try:
            self.drive_away_action = self.cozmo.drive_straight(cozmosdk.util.distance_inches(-2), cozmosdk.util.speed_mmps(100), should_play_anim=False)
            self.drive_away_action.on_completed(lambda evt, **kwargs: self._drive_away_action_completed(evt))
        except:
            pass

    def _drive_away_action_completed(self, evt):
        try:
            self.turn_away_action = self.cozmo.turn_in_place(cozmosdk.util.degrees(-90))
        except:
            pass

    def deactivate(self):
        if self.scared_anim and self.scared_anim.is_running:
            self.scared_anim.abort()

        if self.drive_away_action and self.drive_away_action.is_running:
            self.drive_away_action.abort()

        if self.turn_away_action and self.turn_away_action.is_running:
            self.turn_away_action.abort()

    def update(self, elapsed):
        """ Activates if the threatening-stimulus-releaser is active and the fear emotion is active """
        delta = 35 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('threatening-stimulus-releaser')
        fear = self.behavior_system.robot.emotion_system.emotion_fear

        # TODO: incorporate fear emotion
        if rel.is_active() and self.behavior_system.robot.emotion_system.active_emotion == fear:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class PlayWithToyBehavior(Behavior):
    """ Behavior that tries to engage and play with a toy stimulus """
    name = 'play-with-toy-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system)

        self.happy_anim = None
        self.roll_block_behavior = None

    def activate(self):
        """ Roll the block over """
        self.robot = self.behavior_system.robot
        self.cozmo = self.robot.cozmo

        # Begin the behavior to roll the block over
        try:
            self.happy_anim = self.cozmo.play_anim_trigger(cozmosdk.anim.Triggers.AcknowledgeFaceNamed)
            self.happy_anim.on_completed(lambda evt, **kwargs: self._happy_animation_completed(evt))
        except:
            pass

    def _happy_animation_completed(self, evt):
        self.roll_block_behavior = self.cozmo.start_behavior(cozmosdk.behavior.BehaviorTypes.RollBlock)

    def deactivate(self):
        """ Deactivate the behaviors if they are active """
        if self.happy_anim and self.happy_anim.is_running:
            self.happy_anim.abort()

        if self.roll_block_behavior and self.roll_block_behavior.is_active:
            self.roll_block_behavior.stop()

    def update(self, elapsed):
        """ Activates if the desired-stimulus-releaser is active and the solo-drive is active and the joy-emotion is active """
        delta = 10 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        solo = self.behavior_system.robot.drive_system.solo_drive
        joy = self.behavior_system.robot.emotion_system.emotion_joy

        if rel.is_active() and self.behavior_system.robot.drive_system.active_drive == solo and self.behavior_system.robot.emotion_system.active_emotion == joy:
            self.activation_level = self.activation_level + delta
        else:
            self.activation_level = max(0, self.activation_level - delta)


class EngageWithFaceBehavior(Behavior):
    """ Behavior that tries to engage with a face stimulus """
    name = 'engage-with-face-behavior'

    def __init__(self, behavior_system):
        super().__init__(behavior_system)
        
        self.phrases = ['Hello', 'Hi', 'Hi there', 'Hey']
        self.happy_anim = None
        self.phrase_action = None

    def activate(self):
        """ Look up at the face, show a happy expression, and say hello """
        self.robot = self.behavior_system.robot
        self.cozmo = self.robot.cozmo

        self._start_loop()

    def _start_loop(self):
        # Play the animation
        if not self.is_active:
            return

        try:
            self.happy_anim = self.cozmo.play_anim_trigger(cozmosdk.anim.Triggers.AcknowledgeFaceNamed)
            self.happy_anim.on_completed(lambda evt, **kwargs: self._happy_anim_completed(evt))
        except:
            pass

    def _happy_anim_completed(self, evt):
        phrase = random.choice(self.phrases)

        # Say a phrase
        try:
            self.phrase_action = self.cozmo.say_text(phrase)
            self.phrase_action.on_completed(lambda evt, **kwargs: self._phrase_action_completed(evt))
        except:
            pass

    def _phrase_action_completed(self, evt):
        self._start_loop()

    def deactivate(self):
        if self.happy_anim and self.happy_anim.is_running:
            self.happy_anim.abort()

        if self.phrase_action and self.phrase_action.is_running:
            self.phrase_action.abort()

    def update(self, elapsed):
        """ Activates if the desired-stimulus-releaser is active and the social-drive is active """
        delta = 10 * elapsed
        rel = self.behavior_system.robot.perception_system.get_releaser('desired-stimulus-releaser')
        social = self.behavior_system.robot.drive_system.social_drive
        joy = self.behavior_system.robot.emotion_system.emotion_joy

        if rel.is_active() and self.behavior_system.robot.drive_system.active_drive == social and self.behavior_system.robot.emotion_system.active_emotion == joy:
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
            SearchForStimulusBehavior(self),
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
            if behavior.is_active:
                behavior.activation_duration += elapsed

        new_active = max(self.behaviors, key=operator.attrgetter('activation_level'))

        if new_active.activation_level < new_active.activation_threshold:
            new_active = None

        if new_active is not self.active_behavior:
            if self.active_behavior:
                self.active_behavior.is_active = False
                self.active_behavior.deactivate()

            self.emit('active-behavior-changed', self.active_behavior, new_active)
            self.active_behavior = new_active

            # Activate the new behavior
            if self.active_behavior:
                self.active_behavior.is_active = True
                self.active_behavior.last_activated = timeit()
                self.active_behavior.activation_duration = 0
                self.active_behavior.activate()