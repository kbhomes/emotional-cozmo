from . import system
import operator

class Emotion(object):
    """ Class that represents an emotion's elicitor and activation process """
    name = None

    def __init__(self, emotion_system):
        self.emotion_system = emotion_system

        self.net_affect = (None, None, None)
        self.elicitation_level = 0
        self.activation_level = 0

        self.activation_bias = 0
        self.activation_persistence = 0
        self.activation_decay = 0
        self.activation_max = 200

        self.threshold_expression = 60
        self.threshold_behavior = 100

    def should_cause_expression(self):
        return self.activation_level >= self.threshold_expression

    def should_cause_behavior(self):
        return self.activation_level >= self.threshold_behavior

    def reset_activation_terms(self):
        """ Reset the temporally-bound activation terms """
        raise NotImplementedError()

    def filter_affect(self, affect):
        """ Returns the adjusted affect if it passes this emotion's filter """
        raise NotImplementedError()

    def compute_net_affect(self):
        """ Compute the net affect of this emotion process """
        filtered_affects = [self.filter_affect(rel.affect) for rel in self.emotion_system.robot.perception_system.releasers if rel.is_active()]
        filtered_affects = [(
            min(max(affect[0], -1250), 1250) if affect[0] else None,
            min(max(affect[1], -1250), 1250) if affect[1] else None,
            min(max(affect[2], -1250), 1250) if affect[2] else None,
        ) for affect in filtered_affects]

        arousal_count = 0
        arousal_value = 0
        valence_count = 0
        valence_value = 0
        stance_count = 0
        stance_value = 0

        for affect in filtered_affects:
            if affect[0]:
                arousal_count += 1
                arousal_value += affect[0]

            if affect[1]:
                valence_count += 1
                valence_value += affect[1]

            if affect[2]:
                stance_count += 1
                stance_value += affect[2]

        if arousal_count: arousal_value /= arousal_count
        if valence_count: valence_value /= valence_count
        if stance_count: stance_value /= stance_count
        self.net_affect = (arousal_value, valence_value, stance_value)

    def compute_elicitation_level(self):
        """ Compute the elicitation level based on the net affect """
        raise NotImplementedError()

    def compute_activation_level(self):
        """ Compute the activation level of this emotion process """
        # If the net affect has any None components, then it cannot be activated
        if not all(self.net_affect):
            # If we are already activated, let it decay naturally
            if self.activation_level >= self.threshold_expression:
                self.activation_level -= self.activation_decay
            else:
                self.activation_level = 0
        else:
            self.activation_level = max(0, min(abs(self.elicitation_level) + self.activation_bias + self.activation_persistence - self.activation_decay, self.activation_max))

    def update(self, elapsed):
        """ Combines all releasers into an elicitation and activation level """
        self.compute_net_affect()
        self.compute_elicitation_level()
        self.compute_activation_level()

        if self.activation_level > self.threshold_expression:
            self.activation_decay += elapsed / 10
        else:
            self.reset_activation_terms()

class JoyEmotion(Emotion):
    """ The joy emotion (for example, when a desired stimulus is present) """
    name = 'joy-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def reset_activation_terms(self):
        """ Reset the temporally-bound activation terms """
        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def filter_affect(self, affect):
        """ The joy-emotion deals with higher arousal, higher valence, and higher stance """
        return (
            affect[0] if affect[0] > 250 else None,
            affect[1] if affect[1] > 250 else None,
            affect[2] if affect[2] > 250 else None, 
        )

    def compute_elicitation_level(self):
        self.elicitation_level = sum([abs(v) for v in self.net_affect]) / 30


class SorrowEmotion(Emotion):
    """ The sorrow emotion (for example, when a desired stimulus is absent for a while) """
    name = 'sorrow-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def reset_activation_terms(self):
        """ Reset the temporally-bound activation terms """
        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def filter_affect(self, affect):
        """ The sorrow-emotion deals with non-high arousal, lower valence, and lower stance """
        return (
            affect[0] if affect[0] < 250 else None,
            affect[1] if affect[1] < -250 else None,
            affect[2] if affect[2] < -250 else None, 
        )

    def compute_elicitation_level(self):
        self.elicitation_level = sum([abs(v) for v in self.net_affect]) / 50


class FearEmotion(Emotion):
    """ The joy emotion (for example, when a threatening stimulus is present) """
    name = 'fear-emotion'

    def __init__(self, emotion_system):
        super().__init__(emotion_system)

        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def reset_activation_terms(self):
        """ Reset the temporally-bound activation terms """
        self.activation_bias = 20
        self.activation_persistence = 10
        self.activation_decay = 0

    def filter_affect(self, affect):
        """ The sorrow-emotion deals with higher arousal, lower valence, and lower stance """
        return (
            affect[0] if affect[0] > 250 else None,
            affect[1] if affect[1] < -250 else None,
            affect[2] if affect[2] < - 250 else None, 
        )

    def compute_elicitation_level(self):
        if not any([rel for rel in self.emotion_system.robot.perception_system.releasers if rel.is_active() and rel.name == 'threatening-stimulus-releaser']):
            self.net_affect = (None, None, None)
            self.elicitation_level = 0
        else:
            self.elicitation_level = sum([abs(v) for v in self.net_affect]) / 50


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