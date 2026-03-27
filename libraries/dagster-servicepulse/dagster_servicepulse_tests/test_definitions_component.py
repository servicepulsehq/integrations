from dagster.components.core.component_tree import ComponentTree

from dagster_servicepulse import ServicePulseDefinitionsComponent


def test_service_pulse_definitions_component_build_defs():
    comp = ServicePulseDefinitionsComponent(
        required_vendors=["stripe"],
        include_transition_sensor=False,
    )
    ctx = ComponentTree.for_test().load_context
    defs = comp.build_defs(ctx)
    assert len(defs.jobs) == 1
    assert len(defs.sensors) == 0
    assert "servicepulse" in defs.resources


def test_service_pulse_definitions_component_custom_token_env():
    comp = ServicePulseDefinitionsComponent(
        required_vendors=[],
        include_transition_sensor=False,
        api_token_env_var="MY_SP_TOKEN",
    )
    defs = comp.build_defs(ComponentTree.for_test().load_context)
    res = defs.resources["servicepulse"]
    assert getattr(res, "api_token", None) is not None
