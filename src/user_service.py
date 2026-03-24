from typing import Optional

from DBService import DBService
from logging_config import configure_logging
from repository import UserPhoneRepository

logger = configure_logging("user_service")


class UserPhoneService:
    def __init__(self, db_service: Optional[DBService] = None, repository: Optional[UserPhoneRepository] = None):
        self.db = db_service or DBService()
        self.repo = repository or UserPhoneRepository()
        self.repo.ensure_schema()

    def get_user(self, wxid: str):
        return self.repo.get_user(wxid)

    def create_user_if_missing(self, wxid: str):
        return self.repo.create_user_if_missing(wxid)

    def get_phones(self, wxid: str) -> list[str]:
        return [row["phone"] for row in self.repo.get_phone_rows(wxid)]

    def save_phones(self, wxid: str, phones: list[str]):
        self.repo.replace_phones(wxid, phones)

    def add_phone(self, wxid: str, phone: str):
        user = self.get_user(wxid)
        if not user:
            return {"error": "wxid not found"}, 404

        phones = self.get_phones(wxid)
        if len(phones) >= 5:
            return {"error": "Maximum 5 phone numbers allowed"}, 400
        if phone in phones:
            return {"error": "Phone number already exists for this user"}, 409

        phones.append(phone)
        self.save_phones(wxid, phones)
        return {"message": "Phone number added successfully", "wxid": wxid, "phone": phone}, 201

    def update_phone(self, wxid: str, old_phone: str, new_phone: str):
        user = self.get_user(wxid)
        if not user:
            return {"error": "wxid not found"}, 404

        phones = self.get_phones(wxid)
        if old_phone not in phones:
            return {"error": "Old phone number not found for this user"}, 404
        if new_phone in phones:
            return {"error": "New phone number already exists for this user"}, 409

        index = phones.index(old_phone)
        phones[index] = new_phone
        self.save_phones(wxid, phones)
        return {
            "message": "Phone number updated successfully",
            "wxid": wxid,
            "old_phone": old_phone,
            "new_phone": new_phone,
        }, 200

    def delete_phone(self, wxid: str, phone: str):
        user = self.get_user(wxid)
        if not user:
            return {"error": "wxid not found"}, 404

        phones = self.get_phones(wxid)
        if phone not in phones:
            return {"error": "Phone number not found for this user"}, 404

        phones.remove(phone)
        self.save_phones(wxid, phones)
        return {"message": "Phone number deleted successfully", "wxid": wxid, "phone": phone}, 200
