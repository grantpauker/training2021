from enum import Enum

import hal
import numpy as np
import wpilib
from networktables import NetworkTables
from wpilib.geometry import Pose2d, Rotation2d
from wpilib.kinematics import (ChassisSpeeds, DifferentialDriveKinematics,
                               DifferentialDriveOdometry,
                               DifferentialDriveWheelSpeeds)

from utils import lazypigeonimu, lazytalonfx, units
from controls import motorstate

class WheelState:
    def __init__(self, left=0, right=0):
        self.left = left
        self.right = right

    def norm(self, value):
        max_output = np.max(np.abs([self.left, self.right]))
        if max_output == 0:
            return
        scale = value / max_output
        self.left *= scale
        self.right *= scale

    def __str__(self):
        return f"({self.left}, {self.right})"


class Chassis:

    # chassis physical constants
    WHEEL_DIAMETER = 6 * units.inches
    WHEEL_RADIUS = WHEEL_DIAMETER / 2
    WHEEL_CIRCUMFERENCE = 2 * np.pi * WHEEL_RADIUS
    GEAR_RATIO = (48 / 14) * (50 / 16)  # 10.7142861

    BUMPER_WIDTH = 3.25 * units.inches
    ROBOT_WIDTH = 30 * units.inches + BUMPER_WIDTH
    ROBOT_LENGTH = 30 * units.inches + BUMPER_WIDTH
    ROBOT_MASS = 100 * units.pounds

    TRACK_WIDTH = 24 * units.inches
    TRACK_RADIUS = TRACK_WIDTH / 2

    # conversions
    RADIANS_PER_METER = (2 * np.pi * GEAR_RATIO) / WHEEL_CIRCUMFERENCE
    METERS_PER_RADIAN = WHEEL_CIRCUMFERENCE / (2 * np.pi * GEAR_RATIO)

    # motor config
    LEFT_INVERTED = True
    RIGHT_INVERTED = False

    # motor coefs
    KS = 0.149 * units.volts
    KV = 2.4 * (units.volts / units.seconds)
    KA = 0.234 * (units.volts / units.seconds / units.seconds)

    # velocity pidf gains
    VL_KP = 0.000363
    VL_KI = 0
    VL_KD = 0
    VL_KF = 0

    VR_KP = 0.000363
    VR_KI = 0
    VR_KD = 0
    VR_KF = 0

    # joystick
    MAX_JOYSTICK_OUTPUT = 1

    # required devices
    dm_l: lazytalonfx.LazyTalonFX
    dm_r: lazytalonfx.LazyTalonFX
    ds_l: lazytalonfx.LazyTalonFX
    ds_r: lazytalonfx.LazyTalonFX

    imu: lazypigeonimu.LazyPigeonIMU

    # constraints
    MAX_VELOCITY = 3 * (units.meters / units.seconds)

    class _Mode(Enum):
        Idle = 0
        PercentOutput = 1
        Velocity = 2

    def __init__(self):
        self.mode = self._Mode.Idle

        self.odometry = DifferentialDriveOdometry(Rotation2d.fromDegrees(0))

        self.desired_output = WheelState()
        self.desired_velocity = WheelState()

        self.feedforward = WheelState()

        self.wheel_left = motorstate.MotorState()
        self.wheel_right = motorstate.MotorState()

        self.nt = NetworkTables.getTable(f"/components/chassis")

    def setup(self):
        self.dm_l.setInverted(self.LEFT_INVERTED)
        self.dm_r.setInverted(self.RIGHT_INVERTED)

        self.dm_l.setRadiansPerUnit(self.RADIANS_PER_METER)
        self.dm_r.setRadiansPerUnit(self.RADIANS_PER_METER)

        self.dm_l.setPIDF(
            0, self.VL_KP, self.VL_KI, self.VL_KD, self.VL_KF,
        )
        self.dm_r.setPIDF(
            0, self.VR_KP, self.VR_KI, self.VR_KD, self.VR_KF,
        )

    def on_enable(self):
        pass

    def on_disable(self):
        self.stop()

    def stop(self) -> None:
        self.mode = self._Mode.Idle
        if wpilib.RobotBase.isSimulation():
            self._setSimulationOutput(1, 0)
            self._setSimulationOutput(3, 0)

    def setOutput(self, output_l: float, output_r: float) -> None:
        self.mode = self._Mode.PercentOutput
        self.desired_output.left = output_l
        self.desired_output.right = output_r

    def setWheelVelocity(self, velocity_l: float, velocity_r: float) -> None:
        self.mode = self._Mode.Velocity
        self.desired_velocity.left = velocity_l
        self.desired_velocity.right = velocity_r

    def setChassisVelocity(
        self, velocity_x: float, velocity_y: float, velocity_omega
    ) -> None:
        state = ChassisSpeeds(velocity_x, velocity_y, -velocity_omega)
        velocity = self.kinematics.toWheelSpeeds(state)
        self.setWheelVelocity(velocity.left, velocity.right)

    def setTankDrive(self, throttle, rotation):
        self.mode = self._Mode.PercentOutput
        self.desired_output.left = throttle + rotation
        self.desired_output.right = throttle - rotation
        # self.desired_output.norm(self.MAX_JOYSTICK_OUTPUT)

    def setForzaDrive(self, throttle, reverse, rotation):
        if throttle <= 0:
            throttle = -reverse
        self.setTankDrive(throttle, rotation)

    def ntPutLeftRight(self, key, value):
        self.nt.putNumber(f"{key}_left", value.left)
        self.nt.putNumber(f"{key}_right", value.right)

    def updateNetworkTables(self):
        """Update network table values related to component."""
        self.wheel_left.putNT(self.nt, "wheel_left")
        self.wheel_right.putNT(self.nt, "wheel_right")
        self.ntPutLeftRight("desired_output", self.desired_output)
        self.ntPutLeftRight("desired_velocity", self.desired_velocity)
        self.ntPutLeftRight("feedforward", self.feedforward)

    def getHeading(self):
        return self.getPose().rotation().radians()

    def getPose(self):
        if wpilib.RobotBase.isSimulation():
            x = (
                wpilib.simulation.SimDeviceSim("Field2D").getDouble("x").get()
                * units.meters
            )
            y = (
                wpilib.simulation.SimDeviceSim("Field2D").getDouble("y").get()
                * units.meters
            )
            rot = (
                wpilib.simulation.SimDeviceSim("Field2D").getDouble("rot").get()
                * units.degrees
            )
            rot = units.angle_range(rot)
            return Pose2d(x, y, rot)
        else:
            return self.odometry.getPose()

    def _setSimulationOutput(self, id, output):
        wpilib.simulation.SimDeviceSim(f"Talon FX[{id}]").getDouble("Motor Output").set(
            output
        )

    def _getSimulationPosition(self, id):
        return (
            wpilib.simulation.SimDeviceSim(f"Custom Talon FX[{id}]")
            .getDouble("Position")
            .get()
        )

    def execute(self):
        dt = 0.02
        self.wheel_left.update(self.dm_l.getPosition(), dt)
        self.wheel_right.update(self.dm_r.getPosition(), dt)
        if wpilib.RobotBase.isSimulation():
            self.wheel_left.position = self._getSimulationPosition(1)
            self.wheel_right.position = self._getSimulationPosition(3)

        self.odometry.update(
            Rotation2d(self.getHeading()),
            self.wheel_left.position,
            self.wheel_right.position,
        )

        if self.mode == self._Mode.Idle:
            self.dm_l.setOutput(0)
            self.dm_r.setOutput(0)
        elif self.mode == self._Mode.PercentOutput:
            self.dm_l.setOutput(self.desired_output.left)
            self.dm_r.setOutput(self.desired_output.right)
        elif self.mode == self._Mode.Velocity:
            self.feedforward.left = (
                self.feedforward_l.calculate(self.desired_velocity.left, dt) / 12
            )

            self.feedforward.right = (
                self.feedforward_r.calculate(self.desired_velocity.right, dt) / 12
            )
            if not wpilib.RobotBase.isSimulation():
                self.dm_l.setVelocity(
                    self.desired_velocity.left, self.feedforward.left,
                )
                self.dm_r.setVelocity(
                    self.desired_velocity.right, self.feedforward.right,
                )
            else:
                self.dm_l.setOutput(self.desired_velocity.left / self.MAX_VELOCITY)
                self.dm_r.setOutput(self.desired_velocity.right / self.MAX_VELOCITY)
        self.updateNetworkTables()
