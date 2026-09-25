import unittest
from utils.token import generate_token, verify_token


class TestAuthToken(unittest.TestCase):
    def test_generate_and_verify_token(self):
        openid = "test_openid_12345"
        token = generate_token(openid)
        self.assertIsNotNone(token)
        self.assertIn(".", token)

        extracted = verify_token(token)
        self.assertEqual(extracted, openid)

    def test_verify_tampered_token(self):
        openid = "test_openid_12345"
        token = generate_token(openid)
        # 篡改签名部分
        tampered = token[:-4] + "abcd"
        self.assertIsNone(verify_token(tampered))

    def test_verify_legacy_openid_fallback(self):
        openid = "oABC123456789"
        # 旧版本客户端可能直传 openid
        self.assertEqual(verify_token(openid), openid)

    def test_verify_invalid_token(self):
        self.assertIsNone(verify_token(""))
        self.assertIsNone(verify_token("short"))
        self.assertIsNone(verify_token("invalid.token.structure"))


if __name__ == "__main__":
    unittest.main()
