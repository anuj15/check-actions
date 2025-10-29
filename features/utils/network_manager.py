import os
from urllib.parse import urlparse

import pandas as pd

from features.utils.config_manager import is_ci, ConfigManager


class NetworkManager:
    _network_calls = []

    def __init__(self):
        self._all_calls_data = []
        self.obj_config = ConfigManager()
        self.EXTENSIONS = ('.js', '.css', '.woff', '.woff2', '.ttf', '.otf', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.map', '.json')
        self.KEYWORDS = ('telemetry', 'analytics', 'sentry', 'hotjar', 'intercom', 'segment', 'datadog', 'logging', 'CIQDotNet', 'tours')
        self.RESPONSE_STATUS = (900, 901)

    @classmethod
    def _add_call(cls, call):
        cls._network_calls.append(call)

    @classmethod
    def get_calls(cls):
        return cls._network_calls

    @classmethod
    def clear_calls(cls):
        cls._network_calls.clear()

    def intercept_network_calls(self, feature, request):
        if 'ui' in feature.tags:
            page = request.getfixturevalue("page")
            if not page:
                return
            try:
                if not page.is_closed():
                    if not hasattr(page, "_network_listeners_attached"):
                        def log_request(requester):
                            url_path = urlparse(requester.url).path
                            if url_path.endswith(self.EXTENSIONS) or (any(key in url_path for key in self.KEYWORDS)):
                                return
                            call_data = {
                                "type": "Request",
                                "method": requester.method,
                                "url": requester.url,
                                "status": ""
                            }
                            self._all_calls_data.append(call_data)

                        def log_response(response):
                            if response.status in self.RESPONSE_STATUS:
                                return
                            url_path = urlparse(response.url).path
                            if url_path.endswith(self.EXTENSIONS) or (any(key in url_path for key in self.KEYWORDS)):
                                return
                            call_data = {
                                "type": "Response",
                                "method": "",
                                "url": response.url,
                                "status": response.status
                            }
                            self._all_calls_data.append(call_data)
                            try:
                                content_type = response.headers.get('content-type', '').lower()
                                if 'text/' in content_type or 'json' in content_type:
                                    content = response.text()
                                    call_data_with_content = {"url": response.url, "status": response.status, "content": content}
                                    NetworkManager._add_call(call_data_with_content)
                            except Exception as ex:
                                print(f"[intercept_network_calls] Failed to get response content for {response.url}: {ex}")

                        page.on("request", log_request)
                        page.on("response", log_response)
                        page._network_listeners_attached = True
                else:
                    print("[intercept_network_calls] Skipping network interception: Page is already closed")
            except Exception as e:
                print(f"[intercept_network_calls] Network interception failed: {e}")

    def write_network_calls_to_file(self) -> None:
        response_calls = [{"Type": call["type"], "URL": call["url"], "Status": call["status"]} for call in self._all_calls_data if
                          call["type"] == "Response"]
        df = pd.DataFrame(response_calls, columns=["Type", "URL", "Status"])
        file_path = self.obj_config.network_call_file
        if is_ci():
            shard_id = os.getenv("SHARD_ID") or os.getenv("MATRIX_SHARD")
            if shard_id:
                base, ext = os.path.splitext(file_path)
                file_path = f"{base}_{shard_id}{ext}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False, encoding="utf-8")

    def clear_network_calls(self):
        network_call_logs = self.obj_config.network_call_file
        if os.path.exists(network_call_logs):
            with open(network_call_logs, "w", encoding="utf-8") as f:
                f.write("")
