from dagster_servicepulse import build_servicepulse_defs


def test_build_servicepulse_defs_structure():
    defs = build_servicepulse_defs(include_sensor=True)
    assert len(defs.jobs) == 1
    assert len(defs.sensors) == 1
    assert "servicepulse" in defs.resources

    defs_no_sensor = build_servicepulse_defs(include_sensor=False)
    assert len(defs_no_sensor.sensors) == 0
