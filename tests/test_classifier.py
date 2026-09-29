import pytest

from app.categories import CATEGORY_VALUES, Category


def test_seven_exact_categories():
    assert len(CATEGORY_VALUES) == 7
    assert len(set(CATEGORY_VALUES)) == 7
    assert Category("Debt collection") is Category.DEBT_COLLECTION


@pytest.mark.parametrize("invalid", ["debt collection", "Debt Collection", "Other"])
def test_categories_are_strict(invalid):
    with pytest.raises(ValueError):
        Category(invalid)

