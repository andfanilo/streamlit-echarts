"""E2E Playwright tests for the selection API."""

from __future__ import annotations

from conftest import wait_for_app_run
from playwright.sync_api import Page, expect


def test_click_selection_on_bar_chart(app: Page):
    """Click on a bar chart with on_select='rerun' and verify selection has 1 point."""
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

    # Check that selection output appeared
    selected_text = app.locator("text=Selected points: 1")
    expect(selected_text).to_be_visible(timeout=10000)


def test_ignore_mode_returns_dict(app: Page):
    """Verify ignore mode returns a plain dict without selection."""
    wait_for_app_run(app)

    # The ignore mode chart should render and return a dict
    ignore_text = app.locator("text=Ignore result type: dict")
    expect(ignore_text).to_be_visible(timeout=10000)
