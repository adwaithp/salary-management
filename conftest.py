import pytest
import django
from django.conf import settings




@pytest.fixture(autouse=True)
def disable_pagination(settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_PAGINATION_CLASS": None,
        "PAGE_SIZE": None,
    }