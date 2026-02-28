"""E2E Playwright tests for the selection API."""

from __future__ import annotations

from conftest import wait_for_app_run
from playwright.sync_api import Page, expect


def test_click_selection_returns_clicked_element_data(app: Page):
    """Click on a bar chart and verify the returned selection contains correct element data."""
    wait_for_app_run(app)

    instances = app.locator("[data-testid=stBidiComponentRegular]")
    expect(instances.first).to_be_visible()

    # Click on the middle bar (B = 20)
    chart = instances.nth(0)
    canvas = chart.locator("canvas")
    expect(canvas).to_be_visible()

    box = canvas.bounding_box()
    assert box is not None
    # Click roughly in the center of the chart area to hit a bar
    canvas.click(position={"x": box["width"] / 2, "y": box["height"] / 2})

    wait_for_app_run(app, wait_delay=3000)

    # Verify exactly one point was selected
    expect(app.locator("text=Selected points: 1")).to_be_visible(timeout=10000)

    # Verify the returned data matches the clicked bar element
    expect(app.locator("text=First point value: 20")).to_be_visible(timeout=5000)
    expect(app.locator("text=First point series_name: Sales")).to_be_visible(
        timeout=5000
    )
    expect(app.locator("text=First point series_index: 0")).to_be_visible(timeout=5000)
    expect(app.locator("text=First point point_index: 1")).to_be_visible(timeout=5000)


def test_ignore_mode_has_no_selection(app: Page):
    """Verify ignore mode returns a value without selection data."""
    wait_for_app_run(app)

    # The ignore mode chart should render and show its result type
    expect(app.locator("text=/Ignore result type:/")).to_be_visible(timeout=10000)

    # Verify no selection data is present for the ignore-mode chart
    expect(app.locator("text=/Ignore has selection/")).not_to_be_visible()
