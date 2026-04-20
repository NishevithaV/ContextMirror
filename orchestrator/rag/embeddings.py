"""
Converts a list of DayRecords into a plain-text summary
that ChromaDB can embed and store.
"""

from statistics import mean, median

from mcp_client.models import DayRecord


def summarise_week(records: list[DayRecord], week_label: str) -> str:
    """
    Produce a short prose summary of a week's DayRecords.

    week_label is an ISO week string like "2024-W03", used as a header.
    Returns a single string that gets stored in ChromaDB as the document.
    """
    if not records:
        return f"{week_label}: no data recorded."

    lines: list[str] = [f"Week: {week_label}"]

    # Sleep 
    sleep_vals = [
        r.health.sleep_hours
        for r in records
        if r.health and r.health.sleep_hours is not None
    ]
    if sleep_vals:
        lines.append(
            f"Sleep: avg {mean(sleep_vals):.1f}h, "
            f"median {median(sleep_vals):.1f}h "
            f"over {len(sleep_vals)} days."
        )

    # Steps
    step_vals = [
        r.health.steps
        for r in records
        if r.health and r.health.steps is not None
    ]
    if step_vals:
        lines.append(f"Steps: avg {int(mean(step_vals)):,}/day.")

    # Calendar
    all_events = [e for r in records for e in (r.calendar_events or [])]
    if all_events:
        event_count = len(all_events)
        avg_per_day = event_count / len(records)
        lines.append(
            f"Calendar: {event_count} events total, "
            f"{avg_per_day:.1f}/day on average."
        )

    # Messaging
    all_summaries = [s for r in records for s in (r.message_summaries or [])]
    if all_summaries:
        total_sent = sum(s.sent for s in all_summaries)
        total_received = sum(s.received for s in all_summaries)
        contact_set = {s.contact_name for s in all_summaries}
        lines.append(
            f"Messages: sent {total_sent}, received {total_received} "
            f"across {len(contact_set)} contacts."
        )

    # Active hours across the week (union of all reported hours)
    all_hours: set[int] = set()
    for s in all_summaries:
        all_hours.update(s.active_hours or [])
    if all_hours:
        h_sorted = sorted(all_hours)
        lines.append(f"Active messaging hours: {h_sorted}.")

    return "\n".join(lines)


def week_label_for_records(records: list[DayRecord]) -> str:
    """
    Derive an ISO week label (e.g. '2024-W03') from the first record's date.
    Falls back to the raw date string if parsing fails.
    """
    if not records:
        return "unknown-week"
    first = records[0].date
    try:
        from datetime import date
        d = date.fromisoformat(str(first))
        return f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
    except (ValueError, AttributeError):
        return str(first)
