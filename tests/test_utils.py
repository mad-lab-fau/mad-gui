import pytest

from mad_gui.components.dialogs.label_annotation_dialog import depth


@pytest.mark.parametrize(
    "val, expected",
    [
        (None, 0),
        (["a"], 1),
        ({"a": None}, 1),
        ({"a": None, "b": None}, 1),
        ({"Jump": None, "Walk": ["Slow", "Normal", "Fast"]}, 2),
        ({"a": {"b": None}}, 2),
        ({"a": {"b": {"c": None}}}, 3),
        ({"a": {"b": {"c": {"d": None}}}}, 4),
    ],
)
def test_depth(val, expected):
    assert depth(val) == expected
