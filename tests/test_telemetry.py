from isar_robot.telemetry import Telemetry, _get_pressure_level


def test_get_battery_level() -> None:
    telemetry = Telemetry()
    for is_home in [None, True, False]:
        for _ in range(100):
            battery_level: float = telemetry._get_battery_level(is_home=is_home)
            assert battery_level >= 0
            assert battery_level <= 100


def test_get_pressure_level() -> None:
    for _ in range(100):
        pressure_level: float = _get_pressure_level()
        assert pressure_level >= 0.011
        assert pressure_level <= 0.079
