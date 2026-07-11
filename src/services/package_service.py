"""
包裹查询服务
负责与拼多多 API 交互，管理认证 cookie 和 anti-content，
提供包裹查询能力。
"""

import os
from typing import Dict, Union

import execjs
import requests

from config import get_settings
from logging_config import configure_logging

logger = configure_logging("package_service")
REQUEST_URL = "https://mdkd-api.pinduoduo.com/api/orion/op/package/search"


class PackageService:
    """包裹查询服务（有状态，管理 cookie 和 anti-content）"""

    def __init__(self):
        self.settings = get_settings()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

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
        """解析 cookie 字符串为字典"""
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
        """手动设置 SUB_PASS_ID"""
        self.cookies["SUB_PASS_ID"] = str(sub_pass_id)

    def set_cookies(self, cookie_string: str) -> None:
        """用完整的 cookie 字符串替换所有 cookie"""
        self.cookies = self.parse_cookie_string(cookie_string)
        self.cookies["JSESSIONID"] = self.cookies.get("JSESSIONID", "")
        logger.info("Cookies 已完全替换, keys: %s", list(self.cookies.keys()))

    def merge_cookies(self, cookie_dict: Dict[str, str]) -> None:
        """合并单个 cookie 键值对到当前 cookies"""
        for k, v in cookie_dict.items():
            self.cookies[k] = v
        logger.info("Cookies 已合并, 更新的 keys: %s", list(cookie_dict.keys()))

    def get_cookie_string(self) -> str:
        """返回当前 cookies 的分号分隔字符串"""
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items() if v)

    def get_cookie_keys(self) -> list:
        """返回当前 cookie 的 key 列表"""
        return list(self.cookies.keys())

    def persist_cookies_to_env(self):
        """将当前 cookie 持久化到 .env 文件"""
        from config import update_env_value
        new_cookie_str = self.get_cookie_string()
        try:
            update_env_value("PDD_COOKIE_STRING", new_cookie_str)
            logger.info("Cookie 已持久化到 .env")
            return True
        except Exception as e:
            logger.error("Cookie 持久化失败: %s", e)
            return False

    def get_sub_pass_id_from_login(self) -> str | None:
        """通过模拟登录 API 获取 SUB_PASS_ID"""
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
        """更新 SUB_PASS_ID（自动重试）"""
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
        """通过 res.js 生成 anti-content 请求头"""
        # res.js 在 src/ 目录下
        js_file_path = os.path.join(os.path.dirname(self.script_dir), "res.js")
        if not os.path.exists(js_file_path):
            # 兼容：如果 services/ 和 src/ 同级
            js_file_path = os.path.join(self.script_dir, "res.js")
        # 回退到 src/res.js
        if not os.path.exists(js_file_path):
            from config import SRC_DIR
            js_file_path = str(SRC_DIR / "res.js")

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

    def get_response(self, code):
        """发送包裹查询请求"""
        payload = {
            "content": str(code),
            "selected": False,
            "page_size": 10,
            "page_index": 1,
            "waybill_status": 100,
        }
        return requests.post(
            REQUEST_URL,
            headers=self.headers,
            cookies=self.cookies,
            json=payload,
        )

    def parse_packages(self, response):
        """从 API 响应中提取包裹信息列表"""
        try:
            data = response.json()
            if data.get("error_code", 0) != 0:
                logger.error(
                    "API 返回错误: %s",
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
            logger.error("解析响应失败: %s", e)
            return []

    def get_packages(self, code: Union[int, str]):
        """查询包裹列表，自动重试刷新凭证"""
        code = str(code)
        # 测试用手机号
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

        response = self.get_response(code)
        if self._response_is_valid(response):
            return self.parse_packages(response)

        logger.warning("初次请求失败，尝试刷新凭证后重试。")
        self.update_anti_content()
        self.update_sub_pass_id()
        response = self.get_response(code)
        if self._response_is_valid(response):
            return self.parse_packages(response)

        raise Exception("获取包裹信息失败。")

    def _response_is_valid(self, response):
        """校验 API 响应是否有效"""
        if response.status_code != 200:
            logger.error("API 请求失败，状态码: %s", response.status_code)
            return False

        try:
            response_data = response.json()
            if response_data.get("error_code", 0) != 0:
                logger.error("API 返回错误码: %s", response_data.get("error_code"))
                return False
        except ValueError:
            logger.error("响应不是有效的 JSON。")
            return False

        return True
