#!/usr/bin/env python3
import ctre
import hal
import numpy as np
import wpilib
from magicbot import MagicRobot
from utils import units
from components.chassis import Chassis
from utils import lazypigeonimu, lazytalonfx


class Robot(MagicRobot):

    DS_R_ID = 0
    DM_R_ID = 1
    DS_L_ID = 2
    DM_L_ID = 3

    ACTUATOR_ID = 5

    chassis: Chassis

    def createObjects(self):
        """Initialize all wpilib motors & sensors"""
        self.ds_r = lazytalonfx.LazyTalonFX(self.DS_R_ID)
        self.dm_r = lazytalonfx.LazyTalonFX(self.DM_R_ID)

        self.ds_l = lazytalonfx.LazyTalonFX(self.DS_L_ID)
        self.dm_l = lazytalonfx.LazyTalonFX(self.DM_L_ID)

        self.dm_l.follow(self.ds_l)
        self.dm_r.follow(self.ds_r)

        self.actuator = ctre.WPI_TalonSRX(self.ACTUATOR_ID)

        self.imu = lazypigeonimu.LazyPigeonIMU(self.actuator)

        self.driver = wpilib.XboxController(0)

    def robotPeriodic(self):
        pass

    def teleopPeriodic(self):
        try:
            throttle = -self.driver.getRawAxis(1)
            throttle = 0 if abs(throttle) <= 0.3 else throttle

            rotation = -self.driver.getRawAxis(3)
            rotation = 0 if abs(rotation) <= 0.3 else rotation / 3

            self.chassis.setTankDrive(1.0, rotation)
        except:
            self.onException()


if __name__ == "__main__":
    wpilib.run(Robot)
