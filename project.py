import hri

robot = hri.robot.Robot()

try:
    while True:
        pass
except KeyboardInterrupt:
    robot.stop()