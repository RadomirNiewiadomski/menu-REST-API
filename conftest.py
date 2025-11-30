"""
Global pytest configuration and fixtures.
"""

import pytest


@pytest.fixture(autouse=True)
def use_temporary_media_root(tmp_path, settings):
    """
    Sets MEDIA_ROOT to a temporary directory for all tests.

    This fixture runs automatically (autouse=True) for every test.
    It ensures that any file uploaded during tests is saved to a
    temporary folder (managed by pytest's tmp_path) instead of
    the actual project's 'media' folder.
    """
    temp_media_dir = tmp_path / "media"
    temp_media_dir.mkdir()

    settings.MEDIA_ROOT = str(temp_media_dir)
