import pytest

from ckanext.ytp_request.tests import ytp_request_db_setup


@pytest.fixture(autouse=True)
def ytp_request_setup(clean_db):
    ytp_request_db_setup()
