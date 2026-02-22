"""E2E Playwright tests for st_echarts basic chart rendering."""

from __future__ import annotations

import pytest
from conftest import ImageCompareFunction, wait_for_app_run
from playwright.sync_api import Page, expect


def test_basic_line_chart_renders(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that a basic line chart renders without errors."""
    # Wait for all echarts components to mount
    wait_for_app_run(app)

    instances = app.locator("[data-testid=stBidiComponentRegular]")
    expect(instances).to_have_count(4)  # basic, streamlit, dark, event

    first_chart = instances.nth(0)
    canvas = first_chart.locator("canvas")
    expect(canvas).to_be_visible()
    assert_snapshot(first_chart, name="basic_line_chart")


def test_streamlit_theme_chart_renders(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that a chart with the built-in streamlit theme renders."""
    wait_for_app_run(app)

    instances = app.locator("[data-testid=stBidiComponentRegular]")
    streamlit_theme_chart = instances.nth(1)
    canvas = streamlit_theme_chart.locator("canvas")
    expect(canvas).to_be_visible()
    assert_snapshot(streamlit_theme_chart, name="streamlit_theme_chart")


def test_dark_theme_chart_renders(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that a chart with the dark theme renders."""
    wait_for_app_run(app)

    instances = app.locator("[data-testid=stBidiComponentRegular]")
    dark_chart = instances.nth(2)
    canvas = dark_chart.locator("canvas")
    expect(canvas).to_be_visible()
    assert_snapshot(dark_chart, name="dark_theme_chart")


def test_themed_charts_light_and_dark(
    themed_app: Page, assert_snapshot: ImageCompareFunction, app_theme: str
):
    """Test that the streamlit theme chart adapts to light and dark Streamlit themes."""
    wait_for_app_run(themed_app)

    instances = themed_app.locator("[data-testid=stBidiComponentRegular]")
    streamlit_theme_chart = instances.nth(1)
    canvas = streamlit_theme_chart.locator("canvas")
    expect(canvas).to_be_visible()
    assert_snapshot(streamlit_theme_chart, name=f"streamlit_theme-{app_theme}")
