"""A window to display a message for the user and potentially getting a yes/no answer."""
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QMessageBox

from typing import Optional


class UserInformation(QDialog):
    """A dialog to transport information to/from user.

    Methods
    -------
    inform
        Send a message to the use to be accepted with the `OK` button.
    confirm
        Pose a yes/no question and obtain the answer.
    """

    @classmethod
    def _create_message(
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
        """Send a message to the user in a pop-up window with an OK-Button.

        For example this might be useful if something crashed during loading data or executing an algoritihm and you
        would like to provide more context to the user.

        Parameters
        ----------
        text
            The information you want to give to the user.

        help_link
            If you pass this, it will hide behind the `Learn More` button in the lower part of the message.



        Examples
        --------
        Note: If you want to execute the following example without having a MaD GUI instance running (i.e. you did
        not use :meth:`mad_gui.start_gui`, you need to:

        >>> from PySide2.QtWidgets import QApplication
        >>> app = QApplication()

        You do not need the above code snippet, if you want to implement the lines below into your plugin.

        >>> from mad_gui.components.dialogs import UserInformation
        >>> UserInformation.inform("Please make sure to X")
        """
        if help_link:
            msg = cls._create_message(text, [QMessageBox.StandardButton.Ok], help_link)
        else:
            msg = cls._create_message(text, [QMessageBox.StandardButton.Ok])
        msg.exec_()

    @classmethod
    def confirm(cls, text: str, help_link: Optional[str] = None) -> bool:
        """Ask the user something and obtain yes or no as answer.

        Parameters
        ----------
        text
            The question you want to pose to the user.

        help_link
            If you pass this, it will hide behind the `Learn More` button in the lower part of the message.

        Returns
        -------
        answer
            Either `Yes` or `No` of the class :py:class:`PySide2.QtWidgets.QMessageBox`.
            :py:

        Examples
        --------
        Note: If you want to execute the following example without having a MaD GUI instance running (i.e. you did
        not use :meth:`mad_gui.start_gui`, you need to:

        >>> from PySide2.QtWidgets import QApplication
        >>> app = QApplication()

        You do not need the above code snippet, if you want to implement the lines below into your plugin.

        >>> from PySide2.QtWidgets import QMessageBox
        >>> from mad_gui.components.dialogs import UserInformation
        >>> answer = UserInformation.confirm("Do you want to perform X?")
        >>> if answer == QMessageBox.Yes:
        ...    print("Yes!")
        ...
        Yes!
        """
        msg = cls()._create_message(text, [QMessageBox.Yes, QMessageBox.No], help_link)
        return msg.exec_()
