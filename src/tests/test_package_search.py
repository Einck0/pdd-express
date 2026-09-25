import unittest
from unittest.mock import MagicMock, patch
from flask import Flask

from utils.validators import validate_keyword
from utils.token import generate_token
from routes.packages import packages_bp


class TestPackageSearch(unittest.TestCase):
    def test_validate_keyword_min_length(self):
        # 少于 4 位应被拦截
        self.assertFalse(validate_keyword(""))
        self.assertFalse(validate_keyword("1"))
        self.assertFalse(validate_keyword("12"))
        self.assertFalse(validate_keyword("123"))

        # 4 位（订单尾号/虚拟号分机号/手机尾号）应通过校验
        self.assertTrue(validate_keyword("5473"))
        self.assertTrue(validate_keyword("2221"))
        self.assertTrue(validate_keyword("abcd"))

        # 5 位及 6 位单号尾号也应通过
        self.assertTrue(validate_keyword("12345"))
        self.assertTrue(validate_keyword("123456"))
        self.assertTrue(validate_keyword("76979657398740"))

    def test_package_service_allows_four_and_six_digits(self):
        from services.package_service import PackageService

        with patch.object(PackageService, "__init__", lambda self: None):
            ps = PackageService()
            ps.cookies = {}
            ps.headers = {}
            ps.get_response = MagicMock()
            ps._response_is_valid = MagicMock(return_value=True)
            ps.parse_packages = MagicMock(return_value=[{"waybill_code": "TEST1234"}])

            # 3 位字符应被快速过滤返回空
            self.assertEqual(ps.get_packages("123"), [])
            ps.get_response.assert_not_called()

            # 4 位尾号（如 5473）应正常触发请求，不再被拦截
            result_4 = ps.get_packages("5473")
            self.assertEqual(len(result_4), 1)
            self.assertEqual(result_4[0]["waybill_code"], "TEST1234")
            self.assertEqual(ps.get_response.call_count, 1)

            # 6 位单号尾号也应正常触发请求，不再被拦截
            ps.get_response.reset_mock()
            result_6 = ps.get_packages("123456")
            self.assertEqual(len(result_6), 1)
            self.assertEqual(ps.get_response.call_count, 1)

    def test_search_package_route_allows_four_digits(self):
        app = Flask(__name__)
        app.register_blueprint(packages_bp)

        # 模拟 package_service
        mock_pkg_service = MagicMock()
        mock_pkg_service.get_packages.return_value = [
            {"waybill_code": "76979657398740", "pickup_code": "3-0-4011"}
        ]
        app.package_service = mock_pkg_service

        client = app.test_client()
        token = generate_token("test_user_wxid")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 3 位关键词应被拦截返回 400
        res_short = client.post("/package", json={"keyword": "123"}, headers=headers)
        self.assertEqual(res_short.status_code, 400)
        self.assertIn("少于4个字符", res_short.get_json()["message"])

        # 2. 4 位订单尾号应成功放行并返回结果
        res_valid = client.post("/package", json={"keyword": "5473"}, headers=headers)
        self.assertEqual(res_valid.status_code, 200)
        body = res_valid.get_json()
        self.assertEqual(body["code"], 0)
        self.assertEqual(len(body["data"]["packages"]), 1)
        self.assertEqual(body["data"]["packages"][0]["pickup_code"], "3-0-4011")


if __name__ == "__main__":
    unittest.main()
