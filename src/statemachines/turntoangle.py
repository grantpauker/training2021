from magicbot.state_machine import StateMachine, state
from components import chassis
import numpy as np
from utils import units


class TurnToAngle(StateMachine):

    chassis: chassis.Chassis

    KP = 0.25
    TOLERANCE = 5 * units.degrees

    def __init__(self):
        self.desired_angle = 90 * units.degrees

    def setup(self):
        pass

    def align(self):
        self.engage()

    def isAligned(self):
        heading = self.chassis.getHeading()
        return abs(units.angle_diff(heading, self.desired_angle)) <= self.TOLERANCE

    @state(first=True)
    def turnToAngle(self, initial_call):
        heading = self.chassis.getHeading()
        error = units.angle_diff(
            heading, self.desired_angle
        )  # number between [-pi, pi]
        output = self.KP * error  # scale error by proportionality constant
        self.chassis.setOutput(-output, output)
        if self.isAligned():
            self.next_state("lockInPlace")

    @state()
    def lockInPlace(self, initial_call):
        self.chassis.stop()
        if not self.isAligned():
            self.next_state("turnToAngle")

    def done(self):
        super().done()
        self.chassis.stop()