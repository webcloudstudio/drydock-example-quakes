"""Magnitude-filter story: filter_events keeps events with mag >= min_mag, in feed order."""

from cli.feed import extract_events, filter_events


def _feature(ident, mag):
    return {"type": "Feature", "id": ident,
            "properties": {"mag": mag, "place": "P", "time": 1735706358000, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}}


def _events(mags):
    return extract_events([_feature(f"e{i}", m) for i, m in enumerate(mags)])


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_filter_threshold_inclusive():
    mags = [5.0, 5.4, 5.5, 5.6, 7.1, 5.49]
    kept = filter_events(_events(mags), 5.5)
    expected_ids = [f"e{i}" for i, m in enumerate(mags) if m >= 5.5]
    assert [e.id for e in kept] == expected_ids
    assert any(e.mag == 5.5 for e in kept)


def test_filter_none_keeps_all():
    events = _events([5.0, 6.0, 7.0, 8.0])
    before = list(events)
    kept = filter_events(events, None)
    assert [e.id for e in kept] == [e.id for e in before]
    assert events == before


def test_filter_nothing_matches():
    assert filter_events(_events([5.2]), 9.0) == []


# ── Finer coverage: boundaries and non-mutation ─────────────────────────────────────────


def test_filter_keeps_an_event_exactly_at_the_threshold():
    assert [e.id for e in filter_events(_events([5.5]), 5.5)] == ["e0"]


def test_filter_excludes_an_event_just_below_the_threshold():
    assert filter_events(_events([5.4999]), 5.5) == []


def test_filter_with_zero_threshold_keeps_zero_magnitude_events():
    kept = filter_events(_events([0.0, -0.5, 0.1]), 0.0)
    assert [e.mag for e in kept] == [0.0, 0.1]


def test_filter_with_negative_threshold_keeps_everything_above_it():
    assert [e.mag for e in filter_events(_events([-1.0, -0.5, 2.0]), -0.5)] == [-0.5, 2.0]


def test_filter_on_empty_input_is_empty():
    assert filter_events([], 3.0) == []
    assert filter_events([], None) == []


def test_filter_returns_a_new_list_and_does_not_mutate_its_input():
    events = _events([5.0, 6.0])
    original = list(events)
    kept = filter_events(events, 5.5)
    assert events == original
    assert kept is not events


def test_filter_preserves_feed_order_not_magnitude_order():
    kept = filter_events(_events([6.0, 5.6, 7.0, 5.9]), 5.5)
    assert [e.mag for e in kept] == [6.0, 5.6, 7.0, 5.9]
