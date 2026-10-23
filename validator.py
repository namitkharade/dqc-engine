from __future__ import annotations

import re

from models import DataIssue, DataRecord, SeverityLevel

# RFC 5322 simplified email regex for practical validation.
EMAIL_REGEX = re.compile(
    r"^(?=.{1,254}$)(?=.{1,64}@)[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}$"
)

# E.164 requires a leading plus and 7-15 digits, first digit after '+' cannot be 0.
E164_PHONE_REGEX = re.compile(r"^\+[1-9]\d{6,14}$")

# Top 30 common ISO 3166-1 alpha-2 country codes.
COMMON_ISO_ALPHA2_CODES = {
    "AE",
    "AR",
    "AT",
    "AU",
    "BE",
    "BR",
    "CA",
    "CH",
    "CN",
    "DE",
    "DK",
    "ES",
    "FR",
    "GB",
    "ID",
    "IE",
    "IN",
    "IT",
    "JP",
    "KR",
    "MX",
    "NL",
    "NO",
    "PL",
    "RU",
    "SA",
    "SE",
    "TH",
    "TR",
    "US",
}


def validate_record(record: DataRecord) -> list[DataIssue]:
    issues: list[DataIssue] = []

    name_value = record.name if record.name is not None else ""
    if not name_value.strip():
        issues.append(
            DataIssue(
                field="name",
                issue_type="empty_name",
                severity=SeverityLevel.HIGH,
                suggested_fix=(
                    f"Name value {name_value!r} is empty or whitespace-only. "
                    "Provide a non-empty full name."
                ),
            )
        )

    email_value = "" if record.email is None else str(record.email).strip()
    if not EMAIL_REGEX.fullmatch(email_value):
        if "@" not in email_value and email_value:
            email_hint = (
                f"Email {email_value!r} appears to be missing '@' symbol. "
                "Use format local@domain.tld."
            )
        elif not email_value:
            email_hint = (
                "Email value is missing. Provide an address like 'name@example.com'."
            )
        else:
            email_hint = (
                f"Email {email_value!r} is not in a valid format. "
                "Use format local@domain.tld with a valid domain."
            )

        issues.append(
            DataIssue(
                field="email",
                issue_type="invalid_email_format",
                severity=SeverityLevel.HIGH,
                suggested_fix=email_hint,
            )
        )

    phone_value = "" if record.phone is None else str(record.phone).strip()
    if not E164_PHONE_REGEX.fullmatch(phone_value):
        if phone_value and " " in phone_value:
            phone_hint = (
                f"Phone {phone_value!r} contains spaces. "
                "Use E.164 format: a leading '+', the country code, then the "
                "digits without separators."
            )
        elif not phone_value.startswith("+") and phone_value:
            phone_hint = (
                f"Phone {phone_value!r} is missing leading '+'. "
                "Use E.164 format such as '+14155552671'."
            )
        elif not phone_value:
            phone_hint = (
                "Phone value is missing. Provide E.164 format like '+14155552671'."
            )
        else:
            phone_hint = (
                f"Phone {phone_value!r} is not a valid E.164 number. "
                "Use '+' followed by 7 to 15 digits."
            )

        issues.append(
            DataIssue(
                field="phone",
                issue_type="invalid_phone_e164_format",
                severity=SeverityLevel.MEDIUM,
                suggested_fix=phone_hint,
            )
        )

    if record.price is not None:
        if record.price < 0:
            issues.append(
                DataIssue(
                    field="price",
                    issue_type="negative_price",
                    severity=SeverityLevel.HIGH,
                    suggested_fix=(
                        f"Price {record.price!r} is negative. "
                        "Set price to a non-negative value."
                    ),
                )
            )
        elif record.price > 99999:
            issues.append(
                DataIssue(
                    field="price",
                    issue_type="price_outlier_high",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix=(
                        f"Price {record.price!r} exceeds expected limit of 99999. "
                        "Verify units or correct possible outlier value."
                    ),
                )
            )

    country_value = "" if record.country is None else record.country.strip().upper()
    if country_value not in COMMON_ISO_ALPHA2_CODES:
        if not country_value:
            country_hint = (
                "Country value is missing. Provide a 2-letter ISO code like 'US' or 'DE'."
            )
        elif len(country_value) != 2:
            country_hint = (
                f"Country {record.country!r} must be a 2-letter ISO alpha-2 code, "
                "for example 'US', 'IN', or 'DE'."
            )
        else:
            country_hint = (
                f"Country code {country_value!r} is not in the allowed common ISO alpha-2 set. "
                "Use a valid code such as 'US', 'GB', or 'JP'."
            )

        issues.append(
            DataIssue(
                field="country",
                issue_type="invalid_country_code",
                severity=SeverityLevel.LOW,
                suggested_fix=country_hint,
            )
        )

    return issues
