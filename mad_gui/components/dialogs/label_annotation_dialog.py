from functools import reduce

from PySide2.QtCore import QEvent, Qt
from PySide2.QtWidgets import QButtonGroup, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout, QRadioButton, QVBoxLayout

from typing import Any, Dict, List, Tuple, Union


def depth(d):
    if isinstance(d, dict):
        if not d:
            # empty dict
            return 1
        all_depths = (depth(v) for v in d.values())
        return 1 + max(all_depths)
    if isinstance(d, list):
        return 1
    if d is None:
        return 0
    raise ValueError(f"Unknown type {type(d)}")


class NestedLabelSelectDialog(QDialog):
    """A Window with Radio Buttons or Checkboxes"""

    _max_depth: int
    _label_options: Union[List[str], Dict[str, Any]]

    latest_selection_: Tuple[str, ...] = ()

    def __init__(self, parent=None, initial_selection: Tuple[str, ...] = None):
        super().__init__()
        self.parent = parent
        self.setWindowIcon(self.parent.windowIcon())
        self.setPalette(self.parent.palette())
        self.initial_selection = initial_selection or NestedLabelSelectDialog.latest_selection_
        self.main_layout = QVBoxLayout()
        self.level_widgets: List[QVBoxLayout] = []
        self.level_button_group: List[QButtonGroup] = []
        self.buttons = QDialogButtonBox(parent=self)
        self.buttons.addButton("Ok", QDialogButtonBox.AcceptRole)
        self.buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.current_selection_ = NestedLabelSelectDialog.latest_selection_
        self.setWindowTitle("Set description")

        self.setLayout(self.main_layout)

    def _setup_layout(self):
        # Create emtpy layouts based max depth
        label_layout = QHBoxLayout()
        self.main_layout.addLayout(label_layout)
        for i in range(self._max_depth):
            group_box = QGroupBox(parent=self, title=f"Level {i}")
            group_box.setPalette(self.palette())
            inner_layout = QVBoxLayout()
            inner_layout.addStretch()
            group_box.setLayout(inner_layout)
            label_layout.addWidget(group_box)
            self.level_widgets.append(inner_layout)
            button_group = QButtonGroup(parent=group_box)
            button_group.setObjectName(str(i))
            button_group.buttonToggled.connect(self._on_label_select)
            self.level_button_group.append(button_group)

        self.main_layout.addWidget(self.buttons)
        self._setup_level(self._get_level_keys(self._label_options), level=0)

        self.level_button_group[0].checkedButton().setFocus()

    def _on_label_select(self, value):
        if not value:
            return None
        level = int(self.sender().objectName())
        choices = self._get_choices(level + 1)
        if choices is not None:
            return self._setup_level(choices, level + 1)
        # We have a final choice.
        # We do nothing, but we need to cleanup all further levels"
        for i in range(level + 1, self._max_depth):
            self._clean_level(i)

        self.current_selection_ = tuple(b.checkedButton().objectName() for b in self.level_button_group[: level + 1])
        return None

    def _get_choices(self, level):
        if level == 0:
            choices = self._label_options
        else:
            choices = reduce(
                lambda x, y: x[y.checkedButton().objectName()],
                self.level_button_group[: level - 1],
                self._label_options,
            )
            if isinstance(choices, dict):
                choices = choices[self.level_button_group[level - 1].checkedButton().objectName()]
                if choices is None:
                    # We have a final choice
                    return None
            else:
                # We have a final choice
                return None
        return self._get_level_keys(choices)

    @staticmethod
    def _get_level_keys(level_choice: Union[List[str], Dict[str, Any]]):
        if isinstance(level_choice, dict):
            return list(level_choice.keys())
        return level_choice

    def _clean_level(self, level):
        group = self.level_button_group[level]
        for b in group.buttons():
            b.deleteLater()

    def _setup_level(self, choices: List[str], level: int):
        widget = self.level_widgets[level]
        group = self.level_button_group[level]

        self._clean_level(level)

        pre_selected = None

        initial_choice_for_level = None
        if self.initial_selection and len(self.initial_selection) > level:
            initial_choice_for_level = self.initial_selection[level]

        for i, choice in enumerate(choices):
            button = QRadioButton(str(i + 1) + ": " + choice, parent=self)
            # This is required so that we can capture the space key
            button.installEventFilter(self)
            button.setObjectName(choice)
            if i == 0:
                # per default we select the first button
                pre_selected = button
            if initial_choice_for_level == choice:
                pre_selected = button
            # We insert instead of add to keep the stretch at the bottom
            widget.insertWidget(widget.count() - 1, button)
            group.addButton(button)

        # Enable first checkbox:
        pre_selected.setChecked(True)

    def get_label(self, label_options: Union[List[str], Dict[str, Any]]):
        self._max_depth = depth(label_options)
        self._label_options = label_options
        self._setup_layout()
        if self.exec_():
            NestedLabelSelectDialog.latest_selection_ = self.current_selection_
            return self.current_selection_
        return None

    def keyPressEvent(self, event):  # noqa
        # Camelcase method overwrites qt method
        if event.key() in (Qt.Key_Return, Qt.Key_Space):
            event.accept()
            self.accept()
            return
        if event.key() == Qt.Key_Escape:
            event.accept()
            self.reject()
            return
        current_focus = self.focusWidget().parentWidget()
        try:
            level = self.level_widgets.index(current_focus.layout())
        except ValueError:
            # This happens if a widget is focused that is not part of the label selection
            return
        choices = self._get_choices(level)
        # Number keys start at 49 to 59
        mapping = dict(zip(range(49, 59), choices))
        k_choice = mapping.get(event.key(), None)
        if k_choice is None:
            return
        button: QRadioButton = current_focus.findChild(QRadioButton, k_choice)
        button.setChecked(True)
        event.accept()

    def eventFilter(self, q_object, event) -> bool:  # noqa
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            self.keyPressEvent(event)
        return super(NestedLabelSelectDialog, self).eventFilter(q_object, event)  # noqa
