
from decimal import Decimal

from src.loading.incremental import classify_record


def test_new_record():
    new_values = (
        Decimal("150.00"),
        Decimal("155.00"),
        Decimal("148.00"),
        Decimal("153.00"),
        1000000
    )

    result = classify_record(new_values, None)

    assert result == "NEW"


def test_changed_record():
    existing_values = (
        Decimal("150.00"),
        Decimal("155.00"),
        Decimal("148.00"),
        Decimal("153.00"),
        1000000
    )

    new_values = (
        Decimal("150.00"),
        Decimal("155.00"),
        Decimal("148.00"),
        Decimal("154.00"),
        1000000
    )

    result = classify_record(new_values, existing_values)

    assert result == "CHANGED"


def test_unchanged_record():
    existing_values = (
        Decimal("150.00"),
        Decimal("155.00"),
        Decimal("148.00"),
        Decimal("153.00"),
        1000000
    )

    new_values = (
        Decimal("150.00"),
        Decimal("155.00"),
        Decimal("148.00"),
        Decimal("153.00"),
        1000000
    )

    result = classify_record(new_values, existing_values)

    assert result == "UNCHANGED"
