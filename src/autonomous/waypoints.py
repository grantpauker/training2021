from wpilib.geometry import Pose2d

from utils import units


class Waypoints:
    MIN_FIELD_X = 0 * units.feet
    MAX_FIELD_X = 54 * units.feet
    MIN_FIELD_Y = 0 * units.feet
    MAX_FIELD_Y = 27 * units.feet

    INITATION_LINE_X = 10 * units.feet

    IDEAL_SHOOT_X = 12 * units.feet

    START_LAWFUL = Pose2d(INITATION_LINE_X, 7.3 * units.meters, 180 * units.degrees)
    TRENCH_RUN_LAWFUL = Pose2d(
        8.3 * units.meters, 7.3 * units.meters, 180 * units.degrees
    )

    START_STEAL = Pose2d(INITATION_LINE_X, 0.7 * units.meters, 180 * units.degrees)
    TRENCH_RUN_STEAL = Pose2d(
        6.2 * units.meters, 0.7 * units.meters, 180 * units.degrees
    )

    START_CENTER = Pose2d(INITATION_LINE_X, 5.8 * units.meters, 180 * units.degrees)
    RENDEZVOUS_TWO_BALLS = Pose2d(
        6.3 * units.meters, 5.5 * units.meters, 120 * units.degrees
    )

    IDEAL_SHOOT = Pose2d(IDEAL_SHOOT_X, 5.8 * units.meters, 180 * units.degrees)
