"""
Stub module for email_validator to satisfy Pydantic's import_email_validator.
"""


def validate_email(email: str):
    """Dummy validate_email that returns the input without error."""
    return type("EmailValidationResult", (), {"email": email})


class EmailNotValidError(Exception):
    pass
