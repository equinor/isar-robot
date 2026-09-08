from isar_robot.config.settings import settings
from isar_robot.telemetry import Telemetry, _get_pressure_level


def test_get_battery_level() -> None:
    telemetry = Telemetry()
    for is_home in [None, True, False]:
        for _ in range(100):
            battery_level: float = telemetry._get_battery_level(is_home=is_home)
            assert battery_level >= 0
            assert battery_level <= 100


def test_battery_starts_at_configured_initial_level(mocker) -> None:
    mocker.patch.object(settings, "INITIAL_BATTERY_LEVEL", 26.0)

    telemetry = Telemetry()

    assert telemetry.current_battery_level == 26.0


def test_battery_discharges_from_configured_initial_level(mocker) -> None:
    mocker.patch.object(settings, "INITIAL_BATTERY_LEVEL", 26.0)
    telemetry = Telemetry()

    battery_level: float = telemetry._get_battery_level(is_home=False)

    assert battery_level == 26.0 - telemetry.discharging_rate


def test_get_pressure_level() -> None:
    for _ in range(100):
        pressure_level: float = _get_pressure_level()
        assert pressure_level >= 0.011
        assert pressure_level <= 0.079
