"""
member_manager.py - Register, view, search, update and delete members.

Module owner : Member 4
Concepts used: Classes, methods, lists, dictionaries, string methods,
               conditionals, date handling, exception handling
"""

from datetime import date

import validators as v
from exceptions import OperationNotAllowedError, ValidationError
from models import Member


class MemberManager:
    def __init__(self, store):
        self.store = store

    # ------------------------------------------------------------------ add
    def validate_new_email(self, value, ignore_member_id=None):
        """Validate the e-mail format AND make sure nobody else uses it."""
        email = v.validate_email(value)
        for member in self.store.members.values():
            if member.email == email and member.member_id != ignore_member_id:
                raise ValidationError(
                    f"E-mail {email} is already registered ({member.member_id}).")
        return email

    def add_member(self, name, email, phone):
        name = v.validate_name(name, "Name")
        email = self.validate_new_email(email)
        phone = v.validate_phone(phone)

        member = Member(self.store.next_member_id(), name, email, phone,
                        date.today())
        self.store.members[member.member_id] = member
        self.store.save()
        return member

    # ----------------------------------------------------------------- view
    def get_member(self, member_id):
        return self.store.get_member(member_id)

    def list_members(self):
        return sorted(self.store.members.values(), key=lambda m: m.member_id)

    # --------------------------------------------------------------- search
    def search_members(self, keyword):
        """Search by name, member ID or e-mail (case-insensitive)."""
        keyword = v.validate_text(keyword, "Search keyword", 50).lower()
        return [m for m in self.list_members()
                if keyword in m.name.lower()
                or keyword in m.member_id.lower()
                or keyword in m.email]

    # --------------------------------------------------------------- update
    def update_member(self, member_id, name=None, email=None, phone=None):
        member = self.get_member(member_id)
        new_name = v.validate_name(name, "Name") if name is not None else member.name
        new_email = (self.validate_new_email(email, ignore_member_id=member.member_id)
                     if email is not None else member.email)
        new_phone = v.validate_phone(phone) if phone is not None else member.phone

        member.name, member.email, member.phone = new_name, new_email, new_phone
        self.store.save()
        return member

    # --------------------------------------------------------------- delete
    def delete_member(self, member_id):
        """Remove a member. Not allowed while they still hold issued books."""
        member = self.get_member(member_id)
        loans = self.store.open_loans_of_member(member.member_id)
        if loans:
            raise OperationNotAllowedError(
                f"Cannot delete {member.name}: {len(loans)} book(s) not returned yet.")
        del self.store.members[member.member_id]
        self.store.save()
        return member

    # -------------------------------------------------------------- history
    def history_of(self, member_id):
        """All loans (open and returned) of one member, oldest first."""
        member = self.get_member(member_id)
        return [t for t in self.store.transactions
                if t.member_id == member.member_id]
