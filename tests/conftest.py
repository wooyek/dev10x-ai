import pytest

from tests.fakers import (
    BashHookInputFactory,
    CompensationFactory,
    ConfigFactory,
    EditHookInputFactory,
    HookInputFactory,
    RuleFactory,
)


@pytest.fixture()
def hook_input_factory() -> type[HookInputFactory]:
    return HookInputFactory


@pytest.fixture()
def bash_hook_input_factory() -> type[BashHookInputFactory]:
    return BashHookInputFactory


@pytest.fixture()
def edit_hook_input_factory() -> type[EditHookInputFactory]:
    return EditHookInputFactory


@pytest.fixture()
def rule_factory() -> type[RuleFactory]:
    return RuleFactory


@pytest.fixture()
def compensation_factory() -> type[CompensationFactory]:
    return CompensationFactory


@pytest.fixture()
def config_factory() -> type[ConfigFactory]:
    return ConfigFactory
