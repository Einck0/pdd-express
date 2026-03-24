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
        self.packageService = package_service if package_service else PackageService()
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule(f"{self.API_PREFIX}/cookie", view_func=self.update_sub_pass_id, methods=["POST"])
        self.app.add_url_rule(f"{self.API_PREFIX}/package/<wxid>", view_func=self.query_package, methods=["POST"])
        self.app.add_url_rule(f"{self.API_PREFIX}/phones/<wxid>", view_func=self.get_phones, methods=["GET"])
        self.app.add_url_rule(f"{self.API_PREFIX}/package/<wxid>", view_func=self.get_package_by_wxid, methods=["GET"])
        self.app.add_url_rule(f"{self.API_PREFIX}/phones/<wxid>", view_func=self.add_phone, methods=["POST"])
        self.app.add_url_rule(f"{self.API_PREFIX}/phones/<wxid>", view_func=self.update_phone, methods=["PUT"])
        self.app.add_url_rule(f"{self.API_PREFIX}/phones/<wxid>", view_func=self.delete_phone, methods=["DELETE"])
        self.app.add_url_rule(f"{self.API_PREFIX}/wxlogin", view_func=self.wx_login, methods=["POST"])

    def register_user(self, openid=None):
        wxid = openid
        if not wxid:
            return jsonify({"error": "wxid is required"}), 400
        existing = self.user_phone_service.get_user(wxid)
        if existing:
            return jsonify({"error": "wxid already exists"}), 201
        self.user_phone_service.create_user_if_missing(wxid)
        return jsonify({"message": "User registered successfully", "wxid": wxid}), 201

    def update_sub_pass_id(self):
        data = parse_json_body(request)
        sub_pass_id = data.get("sub_pass_id")
        if not sub_pass_id:
            return jsonify({"error": "sub_pass_id is required"}), 400

        record = self.db.fetch_one("SELECT * FROM cookies WHERE name = ?", ("SUB_PASS_ID",))
        if record:
            self.db.execute("UPDATE cookies SET value = ? WHERE name = ?", (sub_pass_id, "SUB_PASS_ID"))
        else:
            self.db.execute("INSERT INTO cookies (name, value) VALUES (?, ?)", ("SUB_PASS_ID", sub_pass_id))
        return jsonify({"message": "sub_pass_id cookie updated", "sub_pass_id": sub_pass_id}), 200

    def query_package(self, wxid: str):
        data = parse_json_body(request)
        keyword = data.get("keyword")
        if not keyword:
            return jsonify({"error": "No keyword provided"}), 400
        if len(keyword) < 4:
            return jsonify({"error": "Invalid keyword length"}), 400

        try:
            packages = self.packageService.get_packages(keyword)
        except Exception as e:
            logger.exception("Error querying packages for wxid=%s: %s", wxid, e, extra={"wxid": wxid})
            return jsonify({"error": "Failed to query packages"}), 500
        return jsonify({"packages": packages})

    def get_phones(self, wxid: str):
        user = self.user_phone_service.get_user(wxid)
        if not user:
            self.user_phone_service.create_user_if_missing(wxid)
            return jsonify({"phones": []})
        return jsonify({"phones": self.user_phone_service.get_phones(wxid)})

    def get_package_by_wxid(self, wxid: str):
        user = self.user_phone_service.get_user(wxid)
        if not user:
            return jsonify({"error": "wxid not found", "code": 4001}), 404

        phones = self.user_phone_service.get_phones(wxid)
        packages = []
        try:
            for phone in phones:
                packages += self.packageService.get_packages(phone)
            return jsonify({"packages": packages})
        except Exception as e:
            logger.exception("Error retrieving packages for wxid=%s: %s", wxid, e, extra={"wxid": wxid})
            return jsonify({"error": "Failed to retrieve packages"}), 500

    def add_phone(self, wxid: str):
        data = parse_json_body(request)
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "phone is required"}), 400
        payload, status = self.user_phone_service.add_phone(wxid, phone)
        return jsonify(payload), status

    def update_phone(self, wxid: str):
        data = parse_json_body(request)
        old_phone = data.get("old_phone")
        new_phone = data.get("new_phone")
        if not old_phone or not new_phone:
            return jsonify({"error": "old_phone and new_phone are required"}), 400
        payload, status = self.user_phone_service.update_phone(wxid, old_phone, new_phone)
        return jsonify(payload), status

    def delete_phone(self, wxid: str):
        data = parse_json_body(request)
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "phone is required"}), 400
        payload, status = self.user_phone_service.delete_phone(wxid, phone)
        return jsonify(payload), status

    def wx_login(self):
        data = parse_json_body(request)
        code = data.get("code")
        if not code:
            return jsonify({"error": "Login code is required"}), 400

        response = requests.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": self.APPID,
                "secret": self.SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            return jsonify({"error": "Failed to call WeChat API"}), 500

        res_data = response.json()
        if "openid" not in res_data:
            return jsonify({"error": "Invalid WeChat code or API error", "detail": res_data}), 400
        return jsonify({"openid": res_data["openid"]}), 200

    def run(self):
        self.app.run(host=settings.host, debug=settings.debug, port=settings.port)


if __name__ == "__main__":
    app_instance = ExpressEndpointApp(package_service=PackageService())
    app_instance.run()
