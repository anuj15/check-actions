import allure
from pytest_bdd import scenario, given, when, then

from conftest import allure_labels
from features.utils.config_manager import ConfigManager

config = ConfigManager()


@allure_labels("Suite 1", "Feature 1", "Story 1", "tag 1")
@scenario("../feature_files/a.feature", "validate a scenario")
def test_validate_scenario():
    allure.dynamic.title("First Scenario")


@given("a common step")
@allure.step("Executing common step")
def common_step():
    print("Executing common step")


@when("I perform an action")
@allure.step("Performing action step")
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
@allure.step("Verifying result step")
def see_result():
    print("Seeing the result")


@allure_labels("Suite 2", "Feature 2", "Story 2", "tag 2")
@scenario("../feature_files/a.feature", "validate another scenario")
def test_validate_another_scenario():
    allure.dynamic.title("Second Scenario")


@when("I perform another action")
@allure.step("Performing another action step")
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
@allure.step("Verifying different result step")
def see_different_result():
    print("Seeing a different result")
