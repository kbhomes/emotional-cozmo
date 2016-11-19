from . import system

class Releaser(object):
    """ Represents a releaser process in the perception system """

    def __init__(self, perception_system):
        self.perception_system = perception_system

        self.activation_level = 0
        self.activation_threshold = 100
        self.affect = None
    
    def update(self, elapsed):
        """ Computes the activation level and affect for the releaser """
        raise NotImplementedError()
