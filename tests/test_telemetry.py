from isar_robot.telemetry import _get_pressure_level, _get_battery_level


def test_get_battery_level():
    for _ in range(100):
        pressure_level: float = _get_battery_level()
        assert pressure_level >= 50
        assert pressure_level <= 100


def test_get_pressure_level():
    for _ in range(100):
        pressure_level: float = _get_pressure_level()
        assert pressure_level >= 0.011
        assert pressure_level <= 0.079
