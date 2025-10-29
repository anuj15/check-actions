import base64
import os
import platform
import shutil
import subprocess
from functools import wraps

import allure
import pytest
from pytest_html import extras

from features.utils.config_manager import ConfigManager, is_ci


class ReportManager:

    def __init__(self):
        self.obj_config = ConfigManager()

    def add_environment_info_to_report(self, session: pytest.Session):
        pr_number = None
        github_ref = os.getenv('GITHUB_REF', '')
        github_ref_parts = github_ref.split('/')
        if len(github_ref_parts) >= 3 and github_ref_parts[1] == 'pull':
            pr_number = github_ref_parts[2]
        env_info = {
            'Environment': self.obj_config.get('environment'),
            'Suite': os.getenv('SUITE', 'N/A'),
            'Browser': self.obj_config.get('browser'),
            'User_Type': self.obj_config.get('user_type'),
            'company_id': self.obj_config.get('company_id'),
            'detailed_testing': self.obj_config.get('detailed_testing'),
            'Number_of_Companies': self.obj_config.get('number_of_companies'),
            'number_of_visible_alpha_pages_ui': self.obj_config.get('number_of_visible_alpha_pages_ui'),
            'number_of_visible_alpha_pages_api': self.obj_config.get('number_of_visible_alpha_pages_api'),
            'CI_Execution': is_ci(),
            'Run_Number': os.getenv('GITHUB_RUN_NUMBER', 'N/A'),
            'Workflow': os.getenv('GITHUB_WORKFLOW', 'N/A'),
            'Job': os.getenv('GITHUB_JOB', 'N/A'),
            'Ref': github_ref or 'N/A',
            'PR_Number': pr_number or 'N/A',
            'user': os.getenv('GITHUB_ACTOR') or os.getenv('USERNAME') or os.getenv('USER'),
        }
        allure_result_dir = session.config.option.allure_report_dir or self.obj_config.allure_result_dir
        os.makedirs(allure_result_dir, exist_ok=True)
        str_env_file_path = os.path.join(allure_result_dir, 'environment.properties')
        with open(str_env_file_path, mode='w', encoding='utf-8') as f:
            for key, value in env_info.items():
                f.write(f'{key.upper()}={str(value).upper()}\n')

    def skip_scenarios_in_report(self, feature, scenario):
        try:
            if 'skipped' in feature.tags:
                pytest.skip(f"Skipping feature: {feature.name} due to 'skipped' tag")
            if 'skipped' in scenario.tags:
                pytest.skip(f"Skipping scenario: {scenario.name} due to 'skipped' tag")
        except Exception as e:
            print(f"[skip_scenarios_in_report] Error while skipping scenarios: {e}")

    def add_labels_to_report(self, suite: str, feature: str, story: str, *tags: str):
        try:
            def decorator(func):
                @allure.suite(suite)
                @allure.feature(feature)
                @allure.story(story)
                @allure.tag(*tags)
                @wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper

            return decorator
        except Exception as e:
            print(f"[add_labels_to_report] Error while adding labels: {e}")

    def attach_screenshots_on_each_step(self, feature, request, step):
        if 'ui' in feature.tags:
            page = request.getfixturevalue("page")
            if not page:
                return
            try:
                if not page.is_closed():
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name=f"Step: {step.name}", attachment_type=allure.attachment_type.PNG)
                else:
                    print("[pytest_bdd_after_step] Skipping screenshot: Page is already closed")
            except Exception as e:
                print(f"[pytest_bdd_after_step] Screenshot failed: {e}")

    def attach_screenshot_on_failure(self, feature, request, step):
        if is_ci() and 'ui' in feature.tags:
            try:
                page = request.getfixturevalue("page")
                if page and not page.is_closed():
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name=f"Step failed: {step.name}", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                print(f"[pytest_bdd_step_error] Screenshot failed: {e}")

    def attach_screenshot_to_report(self, outcome, call: pytest.CallInfo):
        try:
            report = outcome.get_result()
            if call.when == "call":
                screenshot = getattr(pytest, "extra_screenshot", None)
                if screenshot and os.path.exists(screenshot):
                    if not hasattr(report, "extra"):
                        report.extra = []
                    with open(screenshot, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")
                        html_img = f'<img src="data:image/png;base64,{encoded}" />'
                        report.extra.append(extras.html(html_img))
                pytest.extra_screenshot = None
        except Exception as e:
            print(f"[attach_screenshot_to_report] Error attaching screenshot: {e}")

    def run_report(self):
        os.chdir(self.obj_config.root_dir)
        allure_cmd = "allure.bat" if platform.system() == "Windows" else "allure"
        try:
            if not is_ci():
                subprocess.run([allure_cmd, "generate", self.obj_config.allure_result_dir, "-o", self.obj_config.allure_report_dir, "--clean"],
                               check=True)
        except FileNotFoundError:
            print(f"Allure command '{allure_cmd}' not found. Skipping report generation.")
        except subprocess.CalledProcessError as e:
            print(f"Allure report generation failed for dir: {self.obj_config.allure_result_dir} with error: {e}")

    def empty_reports_directory(self):
        str_report_dir = self.obj_config.report_dir
        if not is_ci():
            shutil.rmtree(str_report_dir, ignore_errors=True)
            os.makedirs(str_report_dir, exist_ok=True)
            os.makedirs(self.obj_config.allure_report_dir, exist_ok=True)
            os.makedirs(self.obj_config.allure_result_dir, exist_ok=True)
