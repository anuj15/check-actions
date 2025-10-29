from pytest_bdd import scenario, given, when, then

from features.utils.config_manager import ConfigManager

config = ConfigManager()


@scenario("../feature_files/a.feature", "validate a scenario")
def test_validate_scenario():
    pass


@given("a common step")
def common_step():
    print("Executing common step")


@when("I perform an action")
def perform_action():
    print("Performing action")
    print(config.get("suite"), flush=True)
    print(config.get("browser"), flush=True)
    print(config.get("base_url"), flush=True)
    print(config.get("headless"), flush=True)
    print(config.get("ui_pages"), flush=True)
    print(config.get("user_type"), flush=True)
    print(config.get("api_pages"), flush=True)
    print(config.get("company_id"), flush=True)
    print(config.get("environment"), flush=True)
    print(config.get("detailed_testing"), flush=True)
    print(config.get("number_of_companies"), flush=True)


@then("I should see the result")
def see_result():
    print("Seeing the result")


@scenario("../feature_files/a.feature", "validate another scenario")
def test_validate_another_scenario():
    pass


@when("I perform another action")
def perform_another_action():
    print("Performing another action")
    print(config.get("suite"), flush=True)
    print(config.get("browser"), flush=True)
    print(config.get("base_url"), flush=True)
    print(config.get("headless"), flush=True)
    print(config.get("ui_pages"), flush=True)
    print(config.get("user_type"), flush=True)
    print(config.get("api_pages"), flush=True)
    print(config.get("company_id"), flush=True)
    print(config.get("environment"), flush=True)
    print(config.get("detailed_testing"), flush=True)
    print(config.get("number_of_companies"), flush=True)


@then("I should see a different result")
def see_different_result():
    print("Seeing a different result")
