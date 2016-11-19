import hri

from urwid import *

class RobotView(object):
    
    def __init__(self):
        self.palette = [
            ('title', DARK_RED + ',bold', LIGHT_GRAY),
            ('section_title', LIGHT_GREEN + ',bold', DARK_GRAY),
            
            ('line', LIGHT_GRAY, DARK_GRAY),

            ('active', LIGHT_GREEN, DARK_GRAY),
            ('detected', LIGHT_GREEN, DARK_GRAY),
            ('undetected', DARK_RED, DARK_GRAY),

            ('bg', WHITE, DARK_GRAY)
        ]

        self.header = AttrMap(Text(('title', 'Cozmo'), align=CENTER), 'title')

        self.drives_pile = Pile([])
        self.drives_frame = Frame(self.drives_pile, Text(('section_title', 'Drives'), align=CENTER))

        self.stimuli_id_pile = Pile([])
        self.stimuli_duration_pile = Pile([])
        self.stimuli_columns = Columns([
            self.stimuli_id_pile,
            self.stimuli_duration_pile
        ])
        self.stimuli_frame = Frame(self.stimuli_columns, Text(('section_title', 'Stimuli'), align=CENTER))

        self.body = Columns([
            self.drives_frame,
            ('fixed', 1, AttrWrap(SolidFill(u'\u2502'), 'line')), 
            self.stimuli_frame
        ])
        self.body = AttrMap(self.body, 'bg')

        self.view = Frame(self.body, self.header)

        # Update all views
        self.update_all(None, None)

    def update_drives(self):
        self.drives_pile.contents.clear()

        for drive in robot.drive_system.drives:
            if robot.drive_system.active_drive is drive:
                markup = [('active', '[*] ' + drive.name)]
            else:
                markup = ['    ' + drive.name]

            self.drives_pile.contents.append((Text(markup), ('pack', None)))

    def update_stimuli(self):
        self.stimuli_id_pile.contents.clear()
        self.stimuli_duration_pile.contents.clear()

        for id, stim in robot.perception_system.stimuli.items():
            id_markup = []
            duration_markup = []

            if stim.detected:
                id_markup = [('active', '[*] ' + stim.id)]
                duration_markup = [('detected', ' {:6.1f}s'.format(stim.detection_duration))]
            else:
                id_markup = ['    ' + stim.id]
                duration_markup = [('undetected', '({:6.1f}s)'.format(stim.disappearance_duration))]

            self.stimuli_id_pile.contents.append((Text(id_markup), ('pack', None)))
            self.stimuli_duration_pile.contents.append((Text(duration_markup), ('pack', None)))
            

    def update_all(self, loop, data):
        self.update_drives()
        self.update_stimuli()

        if loop:
            loop.set_alarm_in(0.5, self.update_all)

    def main(self):
        self.loop = MainLoop(self.view, self.palette, unhandled_input=self.unhandled_input)
        self.loop.set_alarm_in(0.5, self.update_all)
        self.loop.run()

    def unhandled_input(self, key):
        if key in ('q', 'Q'):
            robot.stop()
            raise ExitMainLoop()

robot = hri.robot.Robot()
RobotView().main()