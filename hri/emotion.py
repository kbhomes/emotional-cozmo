from . import system
import operator

class Emotion(object):
    """ Class that represents an emotion's elicitor and activation process """
    name = None

    def __init__(self, emotion_system):
        self.emotion_system = emotion_system

        self.net_affect = (0, 0, 0)
        self.elicitation_level = 0
        self.activation_level = 0

        self.activation_bias = 0
        self.activation_persistence = 0
        self.activation_decay = 0

        self.threshold_expression = 60
        self.threshold_behavior = 100

    def should_cause_expression(self):
        return self.activation_level >= self.threshold_expression

    def should_cause_behavior(self):
        return self.activation_level >= self.threshold_behavior

    def reset_activation_terms(self):
        """ Reset the temporally-bound activation terms """
        raise NotImplementedError()

    def update(self, elapsed):
        """ Combines all releasers into an elicitation and activation level """
        pass


class JoyEmotion(Emotion):
    """ The joy emotion (for example, when a desired stimulus is present) """
    name = 'joy-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0


class SorrowEmotion(Emotion):
    """ The sorrow emotion (for example, when a desired stimulus is absent for a while) """
    name = 'sorrow-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0


class FearEmotion(Emotion):
    """ The joy emotion (for example, when a threatening stimulus is present) """
    name = 'fear-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0


class EmotionSystem(system.System):
    """ System that manages the emotional state of the robot """
    
    def __init__(self, robot):
        super().__init__(robot)

        self.emotion_joy = JoyEmotion(self)
        self.emotion_sorrow = SorrowEmotion(self)
        self.emotion_fear = FearEmotion(self)
        self.emotions = [self.emotion_joy, self.emotion_sorrow, self.emotion_fear]
        self.active_emotion = None

    def update(self, elapsed):
        """ Update all emotion elicitors and processes, and arbitrate their activation """
        
        for em in self.emotions:
            em.update(elapsed)

        new_active = max(self.emotions, key=operator.attrgetter('activation_level'))

        if not new_active.should_cause_expression():
            new_active = None

        if new_active is not self.active_emotion:
            self.emit('active-emotion-changed', self.active_emotion, new_active)
            self.active_emotion = new_active