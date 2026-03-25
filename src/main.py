from flask import Flask, jsonify, request
import requests

from DBService import DBService
from PackageService import PackageService
from logging_config import configure_logging
from settings import get_settings
from user_service import UserPhoneService
from utils_common import parse_json_body

logger = configure_logging("main")
settings = get_settings()


class ExpressEndpointApp:
    def __init__(self, package_service: PackageService | None = None):
        self.APPID = settings.appid
        self.SECRET = settings.secret
        self.API_PREFIX = settings.api_prefix
        self.db = DBService()
        self.user_phone_service = UserPhoneService(self.db)
        self.app = Flask(__name__)
        self.package_service = package_service if package_service else PackageService()
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/health", view_func=self.health_check, methods=["GET"])
        self.app.add_url_rule(
            f"{self.API_PREFIX}/cookie",
            view_func=self.update_sub_pass_id,
            methods=["POST"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/package/<wxid>",
            view_func=self.query_package,
            methods=["POST"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/phones/<wxid>",
            view_func=self.get_phones,
            methods=["GET"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/package/<wxid>",
            view_func=self.get_package_by_wxid,
            methods=["GET"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/phones/<wxid>",
            view_func=self.add_phone,
            methods=["POST"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/phones/<wxid>",
            view_func=self.update_phone,
            methods=["PUT"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/phones/<wxid>",
            view_func=self.delete_phone,
            methods=["DELETE"],
        )
        self.app.add_url_rule(
            f"{self.API_PREFIX}/wxlogin",
            view_func=self.wx_login,
            methods=["POST"],
        )

    def ok(self, data=None, message="ok", status=200):
        payload = {"success": True, "message": message}
        if data is not None:
            payload["data"] = data
        return jsonify(payload), status

    def fail(self, message, status=400, code=None, details=None):
        payload = {"success": False, "error": message}
        if code is not None:
            payload["code"] = code
        if details is not None:
            payload["details"] = details
        return jsonify(payload), status

    def health_check(self):
        return self.ok(
            {
                "service": "pdd-express",
                "api_prefix": self.API_PREFIX,
                "port": settings.port,
            },
            message="service is healthy",
        )

    def register_user(self, openid=None):
        wxid = openid
        if not wxid:
            return self.fail("wxid is required", 400)

        existing = self.user_phone_service.get_user(wxid)
        if existing:
            return self.ok({"wxid": wxid}, message="user already exists")

        self.user_phone_service.create_user_if_missing(wxid)
        return self.ok({"wxid": wxid}, message="user registered successfully", status=201)

    def update_sub_pass_id(self):
        data = parse_json_body(request)
        sub_pass_id = data.get("sub_pass_id")
        if not sub_pass_id:
            return self.fail("sub_pass_id is required", 400)

        self.package_service.set_sub_pass_id(sub_pass_id)
        return self.ok(
            {"sub_pass_id": sub_pass_id},
            message="sub_pass_id updated in memory",
        )

    def query_package(self, wxid: str):
        data = parse_json_body(request)
        keyword = str(data.get("keyword", "")).strip()
        if not keyword:
            return self.fail("keyword is required", 400)
        if len(keyword) < 4:
            return self.fail("keyword length must be at least 4", 400)

        try:
            packages = self.package_service.get_packages(keyword)
        except Exception as e:
            logger.exception(
                "Error querying packages for wxid=%s: %s",
                wxid,
                e,
                extra={"wxid": wxid},
            )
            return self.fail("failed to query packages", 500)

        return self.ok(
            {"wxid": wxid, "keyword": keyword, "packages": packages},
            message="packages retrieved successfully",
        )

    def get_phones(self, wxid: str):
        user = self.user_phone_service.get_user(wxid)
        if not user:
            self.user_phone_service.create_user_if_missing(wxid)
            return self.ok(
                {"wxid": wxid, "phones": []},
                message="user created with empty phone list",
            )

        return self.ok(
            {"wxid": wxid, "phones": self.user_phone_service.get_phones(wxid)},
            message="phones retrieved successfully",
        )

    def get_package_by_wxid(self, wxid: str):
        user = self.user_phone_service.get_user(wxid)
        if not user:
            return self.fail("wxid not found", 404, code=4001)

        phones = self.user_phone_service.get_phones(wxid)
        packages = []
        try:
            for phone in phones:
                packages.extend(self.package_service.get_packages(phone))
            return self.ok(
                {"wxid": wxid, "phones": phones, "packages": packages},
                message="packages retrieved successfully",
            )
        except Exception as e:
            logger.exception(
                "Error retrieving packages for wxid=%s: %s",
                wxid,
                e,
                extra={"wxid": wxid},
            )
            return self.fail("failed to retrieve packages", 500)

    def add_phone(self, wxid: str):
        data = parse_json_body(request)
        phone = str(data.get("phone", "")).strip()
        if not phone:
            return self.fail("phone is required", 400)
        payload, status = self.user_phone_service.add_phone(wxid, phone)
        if status >= 400:
            return self.fail(payload["error"], status)
        return self.ok(payload, message="phone added successfully", status=status)

    def update_phone(self, wxid: str):
        data = parse_json_body(request)
        old_phone = str(data.get("old_phone", "")).strip()
        new_phone = str(data.get("new_phone", "")).strip()
        if not old_phone or not new_phone:
            return self.fail("old_phone and new_phone are required", 400)
        payload, status = self.user_phone_service.update_phone(wxid, old_phone, new_phone)
        if status >= 400:
            return self.fail(payload["error"], status)
        return self.ok(payload, message="phone updated successfully", status=status)

    def delete_phone(self, wxid: str):
        data = parse_json_body(request)
        phone = str(data.get("phone", "")).strip()
        if not phone:
            return self.fail("phone is required", 400)
        payload, status = self.user_phone_service.delete_phone(wxid, phone)
        if status >= 400:
            return self.fail(payload["error"], status)
        return self.ok(payload, message="phone deleted successfully", status=status)

    def wx_login(self):
        data = parse_json_body(request)
        code = data.get("code")
        if not code:
            return self.fail("login code is required", 400)

        response = requests.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": self.APPID,
                "secret": self.SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        if response.status_code != 200:
            return self.fail("failed to call WeChat API", 500)

        res_data = response.json()
        if "openid" not in res_data:
            return self.fail("openid not found", 400, details=res_data)

        openid = res_data["openid"]
        return self.register_user(openid)


express_app = ExpressEndpointApp()
app = express_app.app


if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
