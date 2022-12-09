import pytest

from graphics.graphics_service import GraphicsService


@pytest.fixture()
def graphics_service():
    return GraphicsService()