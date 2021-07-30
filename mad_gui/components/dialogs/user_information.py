"""A window to display a message for the user and potentially getting a yes/no answer."""
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QMessageBox

from typing import Optional


class UserInformation(QDialog):
    @classmethod
    def create_message(
        cls, text: str, buttons: [QMessageBox.StandardButton], help_link: Optional[str] = None
    ) -> QMessageBox:
        """Used in different contexts to create a message

        Parameters
        ----------
        text
            The text you want to show the user
        help_link
            A URL-link to supplementary information
        buttons
            The buttons are the options the user has to answer your text
        parent
            The parent widget, whose palette and icon will be used
        """
        msg = QMessageBox()
        for i_button in buttons:
            msg.addButton(i_button)
        if help_link:
            text = text + (
                ' <html><head/><body><p><span style=" color:#063d69;"></span><a href="'
                + help_link
                + '"><span style=" text-decoration: underline; color:#063d69;">Learn More'
            )
        msg.setText(text)
        msg.setAutoFillBackground(True)
        msg.setWindowTitle("Information")
        msg.setWindowFlag(Qt.FramelessWindowHint, True)
        return msg

    @classmethod
    def inform(cls, text: str, help_link: Optional[str] = None) -> bool:
        if help_link:
            msg = cls.create_message(text, [QMessageBox.StandardButton.Ok], help_link)
        else:
            msg = cls.create_message(text, [QMessageBox.StandardButton.Ok])
        return msg.exec_()

    def confirm(self, text: str) -> bool:
        msg = self.create_message(text, [QMessageBox.Yes, QMessageBox.No])
        return msg.exec_()
