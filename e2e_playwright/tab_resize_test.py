"""E2E Playwright tests for chart resize on tab switch."""

from __future__ import annotations

from conftest import ImageCompareFunction, wait_for_app_run
from playwright.sync_api import Page, expect


def test_chart_resizes_on_tab_switch(app: Page, assert_snapshot: ImageCompareFunction):
    """Test that a chart in a hidden tab renders correctly after switching to it."""
    wait_for_app_run(app)

    # Click Tab 2
    app.get_by_role("tab", name="Tab 2").click()
    wait_for_app_run(app)

    # Verify the chart rendered with non-zero dimensions
    chart = app.locator("[data-testid=stBidiComponentRegular]")
    expect(chart).to_have_count(1)
    canvas = chart.locator("canvas")
    expect(canvas).to_be_visible()
    box = canvas.bounding_box()
    assert box is not None and box["width"] > 100

    # Snapshot comparison
    assert_snapshot(chart, name="chart_in_tab2")
