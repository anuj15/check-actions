from typing import Generator, Any

import pytest
from features.utils.network_manager import NetworkManager
from features.utils.report_manager import ReportManager
from playwright.sync_api import sync_playwright
from pytest_metadata.plugin import metadata_key

from features.utils.config_manager import ConfigManager, is_ci

obj_config = ConfigManager()
report_manager = ReportManager()
bool_is_ci_env = is_ci()
obj_network = NetworkManager()


@pytest.hookimpl
def pytest_configure(config: pytest.Config):
    if not bool_is_ci_env:
        config.option.allure_report_dir = obj_config.allure_result_dir
    config.option.self_contained_html = True
    config.option.disable_warnings = True
    config.option.strict_markers = True
    config.option.reruns = 0
    config.option.color = "yes"
    config.option.timeout = 3000
    config.option.timeout_method = "thread"
    config.option.tb = "short"
    config.stash[metadata_key]["Environment"] = obj_config.get("environment")
    config.stash[metadata_key]["Browser"] = obj_config.get("browser")

@pytest.hookimpl
def pytest_sessionstart(session: pytest.Session):
    obj_network.clear_network_calls()
    report_manager.empty_reports_directory()
    report_manager.add_environment_info_to_report(session)


@pytest.fixture(scope="session")
def browser() -> Generator[Any, Any, None]:
    browser_args = ["--start-maximized"]
    browser_name = obj_config.get("browser")
    headless = obj_config.get("headless")
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=headless, args=browser_args)
        yield browser
        browser.close()


@pytest.hookimpl
def pytest_bdd_before_scenario(request, feature, scenario):
    report_manager.skip_scenarios_in_report(feature, scenario)


@pytest.fixture(scope="function")
def page(browser, request) -> Generator[Any, Any, None]:
    headless = obj_config.get("headless")
    viewport = {"width": 1920, "height": 1080} if headless else None
    no_viewport = not headless
    context = browser.new_context(no_viewport=no_viewport, viewport=viewport, accept_downloads=True)
    page = context.new_page()
    yield page
    context.close()


def allure_labels(suite: str, feature: str, story: str, *tags: str):
    return report_manager.add_labels_to_report(suite, feature, story, *tags)


@pytest.hookimpl
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    obj_network.intercept_network_calls(feature, request)
    if not bool_is_ci_env or step == scenario.steps[-1]:
        report_manager.attach_screenshots_on_each_step(feature, request, step)


@pytest.hookimpl
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    report_manager.attach_screenshot_on_failure(feature, request, step)


@pytest.hookimpl
def pytest_bdd_after_scenario(request, feature, scenario):
    NetworkManager.clear_calls()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call: pytest.CallInfo) -> Generator[None, Any, None]:
    outcome = yield
    report_manager.attach_screenshot_to_report(outcome, call)


@pytest.hookimpl
def pytest_sessionfinish(session: pytest.Session, exitstatus):
    obj_network.write_network_calls_to_file()
    report_manager.run_report()
