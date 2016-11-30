import hri
import math
import logging
from urwid import *

class RobotView(logging.StreamHandler):
    
    def __init__(self, logger):
        super().__init__()

        self.palette = [
            ('title', DARK_RED + ', bold', LIGHT_GRAY),
            ('section_title', LIGHT_GREEN + ', bold', DARK_GRAY),
            
            ('line', LIGHT_GRAY, DARK_GRAY),
            ('default', WHITE, DARK_GRAY),

            ('active', LIGHT_GREEN, DARK_GRAY),
            ('not-active', WHITE, DARK_GRAY),
            ('detected', LIGHT_GREEN, DARK_GRAY),
            ('undetected', DARK_RED, DARK_GRAY),

            ('overwhelmed', LIGHT_RED, DARK_GRAY),
            ('underwhelmed', LIGHT_BLUE, DARK_GRAY),
            ('homeostatic', LIGHT_GREEN, DARK_GRAY),

            ('INFO', WHITE, DARK_GRAY),
            ('DEBUG', LIGHT_BLUE, DARK_GRAY),
            ('ERROR', LIGHT_RED, DARK_GRAY),

            ('bg', WHITE, DARK_GRAY)
        ]

        self.header = AttrMap(Text(('title', '\nCozmo\n'), align=CENTER), 'title')

        self.drives_name_pile = Pile([])
        self.drives_level_pile = Pile([])
        self.drives_columns = Columns([self.drives_name_pile, self.drives_level_pile])
        self.drives_frame = Frame(self.drives_columns, Text(('section_title', '\nDrives\n'), align=CENTER))

        self.stimuli_id_pile = Pile([])
        self.stimuli_duration_pile = Pile([])
        self.stimuli_columns = Columns([self.stimuli_id_pile, self.stimuli_duration_pile])
        self.stimuli_frame = Frame(self.stimuli_columns, Text(('section_title', '\nStimuli\n'), align=CENTER))

        self.emotions_name_pile = Pile([])
        self.emotions_level_pile = Pile([])
        self.emotions_affect_pile = Pile([])
        self.emotions_columns = Columns([self.emotions_name_pile, self.emotions_level_pile, self.emotions_affect_pile])
        self.emotions_frame = Frame(self.emotions_columns, Text(('section_title', '\nEmotions\n'), align=CENTER))

        self.releasers_id_pile = Pile([])
        self.releasers_level_pile = Pile([])
        self.releasers_affect_pile = Pile([])
        self.releasers_columns = Columns([
            ('weight', 3, self.releasers_id_pile), 
            ('weight', 1, self.releasers_level_pile), 
            ('weight', 2, self.releasers_affect_pile)
        ])
        self.releasers_frame = Frame(self.releasers_columns, Text(('section_title', '\nReleasers\n'), align=CENTER))

        self.behaviors_name_pile = Pile([])
        self.behaviors_level_pile = Pile([])
        self.behaviors_columns = Columns([self.behaviors_name_pile, self.behaviors_level_pile])
        self.behaviors_frame = Frame(self.behaviors_columns, Text(('section_title', '\nBehaviors\n'), align=CENTER))

        self.console_list_walker = SimpleFocusListWalker([])
        self.console_list_box = ListBox(self.console_list_walker)
        self.console_frame = Frame(self.console_list_box, Text(('section_title', '\nConsole\n'), align=CENTER))

        self.top_columns = Columns([
            ('weight', 1, self.drives_frame), 
            ('fixed', 1, AttrWrap(SolidFill(u'\u2502'), 'line')), 
            ('weight', 2, self.stimuli_frame),
            ('fixed', 1, AttrWrap(SolidFill(u'\u2502'), 'line')), 
            ('weight', 2, self.emotions_frame),
        ])
        self.middle_columns = Columns([
            ('weight', 1, self.releasers_frame),
            ('fixed', 1, AttrWrap(SolidFill(u'\u2502'), 'line')), 
            ('weight', 1, self.behaviors_frame),
        ])
        self.bottom_columns = Columns([
            ('weight', 1, self.console_frame),
        ])

        self.body = Pile([
            ('weight', 1, self.top_columns),
            ('fixed', 1, AttrWrap(SolidFill(u'\u2500'), 'line')), 
            ('weight', 2, self.middle_columns),
            ('fixed', 1, AttrWrap(SolidFill(u'\u2500'), 'line')), 
            ('weight', 2, self.bottom_columns),
        ])
        self.body = AttrMap(self.body, 'bg')

        self.view = Frame(self.body, self.header)

        # Update all views
        self.update_all(None, None)

        self.setLevel(logging.DEBUG)
        self.setFormatter(logging.Formatter('%(relativeSeconds)6d: %(message)s'))
        self.logger = logger
        self.logger.addHandler(self)

    def update_drives(self):
        self.drives_name_pile.contents.clear()
        self.drives_level_pile.contents.clear()

        for drive in robot.drive_system.drives:
            name_markup = []
            level_markup = []

            status = 'overwhelmed' if drive.is_overwhelmed() else (
                     'underwhelmed' if drive.is_underwhelmed() else (
                     'homeostatic' if drive.is_homeostatic() else (
                     '')))

            if robot.drive_system.active_drive is drive:
                name_markup = [('active', '[*] ' + drive.name)]
                level_markup = [(status, str(math.floor(drive.drive_level)))]
            else:
                name_markup = ['    ' + drive.name]
                level_markup = [(status, str(math.floor(drive.drive_level)))]

            self.drives_name_pile.contents.append((Text(name_markup), ('pack', None)))
            self.drives_level_pile.contents.append((Text(level_markup), ('pack', None)))

    def update_stimuli(self):
        self.stimuli_id_pile.contents.clear()
        self.stimuli_duration_pile.contents.clear()

        for id, stim in robot.perception_system.stimuli.items():
            id_markup = []
            duration_markup = []

            if stim.detected:
                id_markup = [('active', '[*] ' + stim.id)]
                duration_markup = [('detected', ' {:8.1f}s'.format(stim.detection_duration))]
            else:
                id_markup = ['    ' + stim.id]
                duration_markup = [('undetected', '({:8.1f}s)'.format(stim.disappearance_duration))]

            self.stimuli_id_pile.contents.append((Text(id_markup), ('pack', None)))
            self.stimuli_duration_pile.contents.append((Text(duration_markup), ('pack', None)))

    def update_emotions(self):
        self.emotions_name_pile.contents.clear()
        self.emotions_level_pile.contents.clear()
        self.emotions_affect_pile.contents.clear()

        for em in robot.emotion_system.emotions:
            name_markup = []
            level_markup = []
            affect_markup = []

            if em is robot.emotion_system.active_emotion:
                name_markup = [('active', '[*] ' + em.name)]
                level_markup = [('active', '{:6.1f}'.format(em.activation_level))]
                affect_markup = [('active', str(em.net_affect))]
            else:
                name_markup = ['    ' + em.name]
                level_markup = [('not-active', '{:6.1f}'.format(em.activation_level))]
                affect_markup = [('not-active', str(em.net_affect))]

            self.emotions_name_pile.contents.append((Text(name_markup), ('pack', None)))
            self.emotions_level_pile.contents.append((Text(level_markup), ('pack', None)))
            self.emotions_affect_pile.contents.append((Text(affect_markup), ('pack', None)))

    def update_releasers(self):
        self.releasers_id_pile.contents.clear()
        self.releasers_level_pile.contents.clear()
        self.releasers_affect_pile.contents.clear()

        for rel in robot.perception_system.releasers:
            id_markup = []
            level_markup = []
            affect_markup = []

            if rel.is_active():
                id_markup = [('active', '[*] ' + rel.name)]
                level_markup = [('active', ' {:6.1f} / {:3d}'.format(rel.activation_level, rel.activation_threshold))]
                affect_markup = [('active', str(rel.affect))]
            else:
                id_markup = ['    ' + rel.name]
                level_markup = [('not-active', ' {:6.1f} / {:3d}'.format(rel.activation_level, rel.activation_threshold))]
                affect_markup = [('not-active', '')]

            self.releasers_id_pile.contents.append((Text(id_markup), ('pack', None)))
            self.releasers_level_pile.contents.append((Text(level_markup), ('pack', None)))
            self.releasers_affect_pile.contents.append((Text(affect_markup), ('pack', None)))

    def update_behaviors(self):
        self.behaviors_name_pile.contents.clear()
        self.behaviors_level_pile.contents.clear()

        for beh in robot.behavior_system.behaviors:
            name_markup = []
            level_markup = []

            if beh.is_active:
                name_markup = [('active', '[*] ' + beh.name)]
                level_markup = [('active', ' {:6.1f} / {:3d}'.format(beh.activation_level, beh.activation_threshold))]
            else:
                name_markup = ['    ' + beh.name]
                level_markup = [('not-active', ' {:6.1f} / {:3d}'.format(beh.activation_level, beh.activation_threshold))]

            self.behaviors_name_pile.contents.append((Text(name_markup), ('pack', None)))
            self.behaviors_level_pile.contents.append((Text(level_markup), ('pack', None)))
            

    def update_all(self, loop, data):
        self.update_drives()
        self.update_stimuli()
        self.update_emotions()
        self.update_releasers()
        self.update_behaviors()

        if loop:
            loop.set_alarm_in(0.5, self.update_all)

    def emit(self, record):
        try:
            record.relativeSeconds = record.relativeCreated / 1000
            msg = self.format(record)
            self.console_list_walker.append(Text((record.levelname, msg)))

            num_items = len(self.console_list_walker) - 1
            if self.console_list_walker.focus == (num_items - 1):
                self.console_list_walker.focus = num_items

        except Exception:
            self.handleError(record)

    def main(self):
        self.loop = MainLoop(self.view, self.palette, unhandled_input=self.unhandled_input)
        self.loop.set_alarm_in(0.5, self.update_all)
        self.loop.run()

    def unhandled_input(self, key):
        # Simulate the toy stimulus
        stim = None

        if key in ('t', 'T'):
            stim = robot.perception_system.stimuli['toy-1']
        if key in ('f', 'F'):
            stim = robot.perception_system.stimuli['face-1']

        if stim:
            if stim.detected:
                stim.disappear()
            else:
                stim.detect()

        # Quit
        if key in ('q', 'Q'):
            robot.stop()
            raise ExitMainLoop()

logger = logging.getLogger('robot')
logger.setLevel(logging.DEBUG)
robot = hri.robot.Robot(logger)
robot.start()

RobotView(logger).main()