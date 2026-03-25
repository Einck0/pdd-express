from typing import Union, Dict

import execjs
import os
import requests

from DBService import DBService
from logging_config import configure_logging
from settings import get_settings

logger = configure_logging("package_service")
REQUSET_URL = "https://mdkd-api.pinduoduo.com/api/orion/op/package/search"


class PackageService:
    def __init__(self):
        self.settings = get_settings()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.db = DBService()

        self.mobile = self.settings.pdd_mobile
        self.encrypted_password = self.settings.pdd_encrypted_password
        self.initial_cookie_str = self.settings.pdd_cookie_string
        self.anti_content_value = ""

        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,en-GB;q=0.8,zh-CN;q=0.7,zh;q=0.6",
            "anti-content": self.anti_content_value,
            "etag": "ldS3alWcZCeStDKx0FzLRvxAwy0k7PU5",
            "origin": "https://mdkd.pinduoduo.com",
            "p-appname": "DDStore-PC",
            "pdd-id": "ldS3alWcZCeStDKx0FzLRvxAwy0k7PU5",
            "priority": "u=1, i",
            "referer": "https://mdkd.pinduoduo.com/",
            "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": self.settings.pdd_user_agent,
        }

        self.cookies = self.parse_cookie_string(self.initial_cookie_str)
        self.cookies["JSESSIONID"] = self.cookies.get("JSESSIONID", "")

        self.update_anti_content()
        if not self.cookies.get("SUB_PASS_ID"):
            self.update_sub_pass_id()

    def parse_cookie_string(self, cookie_str: str) -> Dict[str, str]:
        cookies = {}
        if not cookie_str:
            return cookies
        for line in cookie_str.split("; "):
            try:
                key, value = line.split("=", 1)
                cookies[key.strip()] = value.strip()
            except ValueError:
                logger.warning("解析 cookie 时遇到问题: %s", line)
        return cookies

    def set_sub_pass_id(self, sub_pass_id: str) -> None:
        self.cookies["SUB_PASS_ID"] = str(sub_pass_id)

    def get_sub_pass_id_from_login(self) -> str | None:
        logger.info("尝试通过模拟登录 API 请求获取 SUB_PASS_ID...")
        login_url = "https://mdkd-api.pinduoduo.com/sixers/api/user/loginByMobile"

        if "pdd-id" not in self.headers or not self.headers["pdd-id"]:
            if "_bee" in self.cookies:
                self.headers["pdd-id"] = self.cookies["_bee"]
            else:
                logger.warning("Cookies 中未找到 '_bee'，pdd-id 请求头可能缺失。")

        payload = {
            "mobile": self.mobile,
            "encryptedPassword": self.encrypted_password,
            "appIndex": 0,
        }
        session = requests.Session()
        session.cookies.update(self.cookies)

        try:
            response = session.post(
                login_url, headers=self.headers, json=payload, timeout=20
            )
            response.raise_for_status()

            sub_pass_id = None
            for cookie_name, cookie_object in session.cookies.items():
                if cookie_name.upper() == "SUB_PASS_ID":
                    sub_pass_id = cookie_object

            if sub_pass_id is not None:
                self.cookies["SUB_PASS_ID"] = str(sub_pass_id)
                return str(sub_pass_id)

            logger.warning("未在响应后的 session cookies 中找到 SUB_PASS_ID。")
            return None
        except requests.exceptions.RequestException as e:
            logger.error("请求失败: %s", e)
            return None
        except Exception as e:
            logger.error("发生未知错误: %s", e)
            return None

    def update_sub_pass_id(self):
        logger.info("开始更新 SUB_PASS_ID")
        new_sub_pass_id = self.get_sub_pass_id_from_login()
        if new_sub_pass_id:
            self.cookies["SUB_PASS_ID"] = new_sub_pass_id
            return new_sub_pass_id

        logger.warning("获取 SUB_PASS_ID 失败，尝试更新 anti-content 后重试。")
        self.update_anti_content()
        new_sub_pass_id = self.get_sub_pass_id_from_login()
        if new_sub_pass_id:
            self.cookies["SUB_PASS_ID"] = new_sub_pass_id
            return new_sub_pass_id

        logger.error("获取 SUB_PASS_ID 失败，无法继续操作。")
        return None

    def update_anti_content(self):
        js_file_path = os.path.join(self.script_dir, "res.js")
        try:
            with open(js_file_path, encoding="utf-8") as f:
                js_code = f.read()
            runtime = execjs.get("Node")
            if not runtime:
                raise RuntimeError("Node.js runtime not found.")
            ctx = runtime.compile(js_code)
            at = ctx.call("getAntiContent", self.headers["user-agent"])
            self.headers["anti-content"] = at
        except Exception as e:
            logger.error("Failed to get anti-content: %s", e)

    def get_responese(self, code):
        payload = {
            "content": str(code),
            "selected": False,
            "page_size": 10,
            "page_index": 1,
            "waybill_status": 100,
        }
        return requests.post(
            REQUSET_URL,
            headers=self.headers,
            cookies=self.cookies,
            json=payload,
        )

    def get_info_from_response(self, response):
        try:
            data = response.json()
            if data.get("error_code", 0) != 0:
                logger.error(
                    "API returned error: %s",
                    data.get("error_msg", "Unknown error"),
                )
                return []

            details = data.get("result", {}).get("detail", [])
            return [
                {
                    "waybill_code": item.get("waybill_code", ""),
                    "customer_name": item.get("customer_name", ""),
                    "mobile": item.get("mobile", ""),
                    "pickup_code": item.get("pickup_code", ""),
                }
                for item in details
            ]
        except Exception as e:
            logger.error("Error parsing response: %s", e)
            return []

    def get_packages(self, code: Union[int, str]):
        code = str(code)
        if code == "11111111111":
            return [
                {
                    "waybill_code": "5452467463656",
                    "customer_name": "邱",
                    "mobile": "111****1111",
                    "pickup_code": "5-5-4511",
                },
                {
                    "waybill_code": "8786736566826",
                    "customer_name": "邱",
                    "mobile": "111****1111",
                    "pickup_code": "10-1-3118",
                },
                {
                    "waybill_code": "9786735245466",
                    "customer_name": "邱",
                    "mobile": "111****1111",
                    "pickup_code": "10-4-4419",
                },
            ]
        if len(code) < 5 or len(code) == 6:
            return []

        response = self.get_responese(code)
        if self._response_is_valid(response):
            return self.get_info_from_response(response)

        logger.warning("Initial request failed, attempting to refresh credentials and retry.")
        self.update_anti_content()
        self.update_sub_pass_id()
        response = self.get_responese(code)
        if self._response_is_valid(response):
            return self.get_info_from_response(response)

        raise Exception("Failed to get package information.")

    def _response_is_valid(self, response):
        if response.status_code != 200:
            logger.error("API request failed with status code: %s", response.status_code)
            return False

        try:
            response_data = response.json()
            if response_data.get("error_code", 0) != 0:
                logger.error("API returned error code: %s", response_data.get("error_code"))
                return False
        except ValueError:
            logger.error("Response is not valid JSON.")
            return False

        return True

        try:
            data = response.json()
            if data.get("success", False) is True:
                return True
            if not data.get("result", {}).get("detail"):
                logger.warning("API response contains no package details.")
                return False
        except Exception as e:
            logger.error("Error validating response: %s", e)
            return False
        return True
