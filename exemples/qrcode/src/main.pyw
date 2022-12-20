# coding: utf-8
"""A simple exemple of an UI implementation of the qrcode module with tkyml"""

# For better code
from enum import StrEnum

# For interface
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import tkyml as tkyml

# To make qrcode
from qrcode.image.svg import SvgPathImage
import qrcode

# For relative path
import os


PATH_UI_FILE = "assets/window.yml"


class Variant(StrEnum):
    # Variant class
    FOCUS = "focus"
    UNFOCUS = "unfocus"
    EMPTY = "empty"


class Event(StrEnum):
    # Mouse events
    CLICK = "<Button>"
    FOCUS = "<FocusIn>"
    UNFOCUS = "<FocusOut>"
    KEYRELEASE = "<KeyRelease>"
    CHANGE = "<<Change>>"


@tkyml.define
class QRCode(tkyml.WIDGETS.Img):

    qr: qrcode.QRCode = None

    def __call__(self, data: any, error_correction: int, mask_pattern):
        self.qr = qrcode.QRCode(
            error_correction=error_correction
        )
        self.qr.add_data(data)
        self.draw()

    def draw(self):
        self.qr.make(fit=True)
        self.data(self.qr.make_image())

    def saveto(self, filepath: str):
        self.qr.make_image(image_factory=SvgPathImage).save(filepath)


class AppWidgets(tkyml.WidgetMap):

    qrcode: QRCode = "img.qrcode"
    text: tkyml.WIDGETS.TEntry = "entry.text"
    file: tkyml.WIDGETS.TButton = "entry.file"
    error: tkyml.WIDGETS.TOptionMenu = "output.error"
    pattern: tkyml.WIDGETS.TOptionMenu = "output.pattern"
    save: tkyml.WIDGETS.TButton = "output.save"


class App(tkyml.App):

    __is_empty: bool = True

    def __init__(self) -> None:
        super().__init__(PATH_UI_FILE)
        self.w = AppWidgets(self)
        self.set_events()
        self.mainloop()

    def set_events(self) -> None:

        # Entry placeholder

        @self.w.text.event(Event.FOCUS)
        def _(ev):
            ev.widget.clear()
            ev.widget.variant(Variant.FOCUS)
            ev.widget.unbind(Event.FOCUS)

        @self.w.text.event(Event.UNFOCUS)
        def _(ev):
            if self.__is_empty:
                ev.widget.variant(Variant.EMPTY)

                @ev.widget.event(Event.FOCUS)
                def _(ev):
                    ev.widget.clear()
                    ev.widget.variant(Variant.FOCUS)
                    ev.widget.unbind(Event.FOCUS)

        # File entry

        @self.w.file.event(Event.CLICK)
        def _():
            file = fd.askopenfile(
                mode='r',
                filetypes=(
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*"),
                )
            )
            if file:
                self.__is_empty = False

                self.w.text.clear()
                self.w.text.text(file.name)
                self.w.text.variant(Variant.UNFOCUS)

                @self.w.text.event(Event.FOCUS)
                def _(ev):
                    ev.widget.clear()
                    ev.widget.variant(Variant.FOCUS)
                    ev.widget.unbind(Event.FOCUS)

                try:
                    self.w.qrcode(file.read(), self.w.error.value, self.w.pattern.value)
                    self.__is_empty = False
                except Exception as err:
                    mb.showerror(err.__class__.__name__, repr(err))

                file.close()

        # Error entry

        @self.w.error.event(Event.CHANGE)
        def _(ev):
            if self.w.qrcode.qr:
                self.w.qrcode.qr.error_correction = self.w.error.value
                self.w.qrcode.draw()

        # Pattern entry

        @self.w.pattern.event(Event.CHANGE)
        def _(ev):
            if self.w.qrcode.qr:
                self.w.qrcode.qr.mask_pattern = self.w.pattern.value
                self.w.qrcode.draw()

        # Text entry

        @self.w.text.event(Event.KEYRELEASE)
        def _(ev):
            data = ev.widget.value
            if data:
                try:
                    self.w.qrcode(data, self.w.error.value, self.w.pattern.value)
                    self.__is_empty = False
                except Exception as err:
                    mb.showerror(err.__class__.__name__, repr(err))
            else:
                self.w.qrcode.variant(Variant.EMPTY)
                self.__is_empty = True

        # Save

        @self.w.save.event(Event.CLICK)
        def _():
            if self.__is_empty:
                return
            filepath = fd.asksaveasfilename(
                filetypes=(
                    ("SVG Files", "*.svg"),
                )
            )
            if filepath:
                self.w.qrcode.saveto(filepath)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    App()
