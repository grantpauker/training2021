from enum import Enum

import numpy as np
from utils import lazytalonfx, units
from controls import pidf


def findOutput(desired_angle, current_angle):
    # fancy math to determine output
    output = 1
    return output


class Turret:

    # required devices
    turret_motor: lazytalonfx.LazyTalonFX

    KP = 1
    KI = 0
    KD = 0
    KF = 0

    class _Mode(Enum):
        Idle = 0
        Heading = 1

    def __init__(self):
        self.mode = self._Mode.Idle
        self.desired_output = 0
        self.desired_heading = 0
        self.pidf = pidf.PIDF(self.KP, self.KI, self.KD, self.KF)

    def setup(self):
        pass

    def on_enable(self):
        pass

    def on_disable(self):
        self.stop()

    def stop(self) -> None:
        self.mode = self._Mode.Idle

    def setHeading(self, desired_heading):
        self.mode = self._Mode.Heading
        self.desired_heading = desired_heading
        self.pidf.setSetpoint(self.desired_heading)

    def getHeading(self):
        return self.turret_motor.getPosition()

    def updateNetworkTables(self):
        """Update network table values related to component."""
        pass

    def execute(self):
        if self.mode == self._Mode.Idle:
            pass
        elif self.mode == self._Mode.Heading:
            cur_heading = self.getHeading()

            output = self.pidf.update(cur_heading, 0.02)

            self.turret_motor.set(output)
