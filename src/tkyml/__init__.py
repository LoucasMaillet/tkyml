# coding: utf-8

"""Generate tkinter UI

Build our interface based on a yaml template, containing our
properties and widgets with this syntax:

[SYNTAX]

    [GENERAL]

        :name: ...  ->  Declare an attribute / call a method (accept
                        either only 1 positional arg or some **kwargs).

        _name: ...  ->  Declare an hidden variable.

        .name: {...} ->  Declare a class varation of the widget

        name: {...} ->  Declare a child of current widget

    [SPECIALS]

        :type: ...  ->  Declare type of widget, derived eiter from tk, ttk or style.py (as st).
                        Use with a prefix from the module: tk.<widget_class_name> or ttk.<widget_class_name>
                        or cst.<widget_class_name> 

        ::     ...  ->  Declare a list of methods/attributes, so you can use the same two time in a row.
"""

# Typing
from __future__ import annotations
from typing import Callable, Iterable
from enum import StrEnum

# To build application
from multiprocessing import Process
from inspect import ismethod
import yaml

# For tkinter app / wigdget
from tkinter import ttk
import tkinter as tk

# To load custom fonts
from tkextrafont import Font
from pathlib import Path

# For image widgets
from PIL import Image, ImageTk, ImageColor
from itertools import count, cycle

# For transparent widgets
import win32gui
import win32api
import win32con


__author__ = "Lucas Maillet"
__email__ = "loucas.maillet.pro@gmail.com"
__license__ = "MIT"
__version__ = "0.0.2"
__status__ = "Production"
__repository__ = "https://github.com/LoucasMaillet/tkyml"


# For .yml declaration
class _Prefix(StrEnum):
    HID = '_'
    ATTR = ':'
    CLASS = '.'

LABEL_ATTR = _Prefix.ATTR + "label"
MODE_ATTR = _Prefix.ATTR + "mode"
END = tk.END + "-1c"
MODE_ERROR = TypeError("Mode not found, please refer to docstring.")

# For yaml parser
TAG_YML_SEQ = "tag:yaml.org,2002:seq"


def __construct_sequence(loader, node):
    yield tuple(loader.construct_sequence(node))


yaml.add_constructor(TAG_YML_SEQ, __construct_sequence) # Load sequence as tuple (optimized)


# Functions


def register(cls: Callable):
    """Register a custom widget

    Args:
        cls (Callable): Some class derived one of WIDGET

    Returns:
        Callable: Return the class to avoid error
    """
    setattr(WIDGETS, cls.__name__, cls)
    return cls


# Base widgets class


class __Widget:

    __class: dict[str, dict]

    def __attributes(self, callbacks: tuple[dict[str, any]]):
        """Call a bunc of functions of widget.

        Args:
            callbacks (tuple[dict[str, any]]): The functions in the followinf format: ({ <#fn.__name__> : {**kwargs} or arg }, ...)
        """
        for call in callbacks:
            if call:
                method, args = tuple(call.items())[0]
                if args:
                    if isinstance(args, dict):
                        getattr(self, method)(**args)
                    else:
                        getattr(self, method)(args)
                else:
                    getattr(self, method)()

    def set_class(self, classname: str):
        """Update widget class.

        Args:
            classname (str): The class name.
        """
        self.upd_values(self.__class[classname])

    def set_values(self, values: dict[str, any]):
        """Set attributes, methods, ... from values.

        Args:
            values (dict[str, any]): Some settings values.
        """
        self.__class = {}
        for key, val in values.items():
            match key[0]:
                case _Prefix.ATTR:  # Attribute declaration / Method call
                    key = key[1:]
                    if hasattr(self, key):
                        if isinstance(val, dict):
                            getattr(self, key)(**val)
                        elif val == None:
                            getattr(self, key)()
                        else:
                            getattr(self, key)(val)
                    elif key == '':
                        self.__attributes(val)
                    else:
                        self.configure({key: val})

                case _Prefix.CLASS:
                    self.__class[key[1:]] = val

                case _Prefix.HID:  # Variable declaration
                    continue

                case _:
                    getattr(WIDGETS, val.pop(
                        _Prefix.ATTR + "type"))(self, key, val)

    def upd_values(self, values: dict[str, any]):
        """Update attributes, methods, ... from values.

        Args:
            values (dict[str, any]): Some settings values.
        """
        for key, val in values.items():
            match key[0]:
                case _Prefix.ATTR:  # Attribute declaration / Method call
                    key = key[1:]
                    if hasattr(self, key):
                        if isinstance(val, dict):
                            getattr(self, key)(**val)
                        elif val == None:
                            getattr(self, key)()
                        else:
                            getattr(self, key)(val)
                    elif key == '':
                        self.__attributes(val)
                    else:
                        self.configure({key: val})

                case _Prefix.HID:  # Variable declaration
                    continue

                case _:
                    self.nametowidget(key).upd_values(val)

    def child_destroy(self, name: None):
        """Remove all childs."""
        for child in self.winfo_children():
            child.destroy()

    def event(self, name: str, add=True) -> Callable:
        """Link a function to some event. 

        Args:
            name (str): Corresponding event.
            add (bool, optional): If we add or overwrite the current function binded. Defaults to False.

        Returns:
            Callable: Sub wrapper function
        """
        def wrapper(fn: Callable) -> Callable:
            if fn.__code__.co_argcount - ismethod(fn):
                self.bind(name, fn, add)
            else:
                self.bind(name, lambda _: fn(), add)
            return fn
        return wrapper

    def __hide(self, rgb: tuple[int]):
        """Hide some rgb color

        Args:
            rgb (tuple[int]): RGB Color that will be hided.
        """
        id = self.winfo_id()
        colorkey = win32api.RGB(*rgb)
        wnd_exstyle = win32gui.GetWindowLong(id, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(id, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(
            id, colorkey, 0, win32con.LWA_COLORKEY)

    def hidecl(self, color: ImageColor._Ink):
        """Hide some color

        Args:
            color (ImageColor._Ink): Color that will disappear.
        """
        self.__hide(ImageColor.getrgb(color))

    def hidebg(self, color: ImageColor._Ink):
        rgb = ImageColor.getrgb(color)
        self["bg"] = "#{:02x}{:02x}{:02x}".format(*rgb)
        self.__hide(rgb)


class _Widget(__Widget):

    def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
        super().__init__(master=master, name=name)
        self.set_values(values)

    def scroll(self, y=False, x=False):
        """Add scrollbar to the widget

        Args:
            y (bool): If you want a vertical scrollbar. Defaults to False.
            x (bool, optional):  If you want an horizontal scrollbar. Defaults to False.
        """
        if y:
            scy = ttk.Scrollbar(self)
            scy.pack(side=tk.RIGHT, fill=tk.Y)
            scy.config(command=self.yview)
            self.config(yscrollcommand=scy.set)
        if x:
            scx = ttk.Scrollbar(self, orient="horizontal")
            scx.pack(side=tk.BOTTOM, fill=tk.X)
            scx.config(command=self.xview)
            self.config(xscrollcommand=scx.set)


class _TtkWidget(_Widget):

    def style(self, **values: dict[str, any]):
        stylename = f"""{self.winfo_name()}.{self.winfo_class()}"""
        ttk.Style().configure(stylename, **values)
        self.configure(style=stylename)

    def layout(self, values: list[any]):
        stylename = f"""{self.winfo_name()}.{self.winfo_class()}"""
        ttk.Style(self).layout(stylename, [values])
        self.configure(style=stylename)


class _Text():

    def get_text(self) -> str:
        """Get actual text.

        Returns:
            str: Widget's text
        """
        return self.get(1.0, END)

    def text(self, string: str):
        """Overwrite text.

        Args:
            string (str): New text
        """
        self.insert(tk.END, string)


class _Img:

    MODE_CONTAIN = "contain"
    MODE_FILL = "fill"
    MODE_KEEP = "keep"

    def mode(self, mode: str):
        f"""Select a way of sizing the img.

        Args:
            mode (str): Some mode of sizing (either {self.MODE_CONTAIN}, {self.MODE_FILL} or {self.MODE_KEEP}).

        Raises:
            MODE_ERROR: If mode isn't conforming.
        """
        match mode:
            case self.MODE_CONTAIN:
                self.bind('<Configure>', self._resize_contain)
            case self.MODE_FILL:
                self.bind('<Configure>', self._resize_fill)
            case self.MODE_KEEP:
                self.bind('<Configure>', self._resize_keep)
            case _:
                raise MODE_ERROR


# Main class


class App(tk.Tk, __Widget):

    """A base tkinter app.

    Allow the creation of an app from a yaml file.
    """

    def __init__(self, file: str, *args: any, **kwargs: dict[str, any]):
        super().__init__(*args, **kwargs)
        with open(file, 'r') as file:
            self.set_values(yaml.load(file, Loader=yaml.SafeLoader))

    @classmethod
    def new(cls, *args: any, **kwargs: dict[str, any]) -> App:
        """Create a new app's window.

        Returns:
            App: A new window.
        """
        Process(target=cls, args=args, kwargs=kwargs).start()

    def prot(self, name: str) -> Callable:
        """Link a function to some protocol. 

        Args:
            name (str): Corresponding protocol.

        Returns:
            Callable: Sub wrapper function.
        """
        def wrapper(fn: Callable) -> Callable:
            self.protocol(name, fn)
            return fn
        return wrapper

    def loadfont(self, fontpath: str):
        Font(self, file=fontpath, name=Path(fontpath).name)
        
# Widgets build class


class WIDGETS:

    """The widgets container
    """

    class Img(_Widget, _Img, tk.Label):

        """Image widget based on tkinter's Label
        """

        __img: Image.Image
        __frame: ImageTk.PhotoImage

        def _resize_contain(self, ev: tk.Event):
            img = self.__img.copy()
            img.thumbnail((ev.width, ev.height))
            self.__frame = ImageTk.PhotoImage(img)
            self.configure(image=self.__frame)

        def _resize_keep(self, ev: tk.Event):
            ratio = max(self.__img.width, self.__img.height) / \
                min(ev.width, ev.height)
            if ratio == self.__img.width or ratio == self.__img.height:
                return
            self.__frame = ImageTk.PhotoImage(self.__img.resize(
                (int(self.__img.width / ratio), int(self.__img.height / ratio))), Image.ANTIALIAS)
            self.configure(image=self.__frame)

        def _resize_fill(self, ev: tk.Event):
            self.__frame = ImageTk.PhotoImage(
                self.__img.resize((ev.width, ev.height)), Image.ANTIALIAS)
            self.configure(image=self.__frame)

        def file(self, file: str):
            """Load image from filepath.

            Args:
                file (str): File's path.
            """
            self.__img = Image.open(file)
            self.__frame = ImageTk.PhotoImage(self.__img)
            self.configure(image=self.__frame)

    class Gif(_Widget, tk.Label):

        """Gif image widget based on tkinter's Label
        """

        __imgs: tuple[Image.Image]
        __frames: Iterable[ImageTk.PhotoImage]
        __delay = 100
        __id: str

        def __update(self):
            self.configure(image=next(self.__frames))
            self.__id = self.after(self.__delay, self.__update)

        def __resize_frame(img: Image.Image, size: tuple[int]):
            img = img.copy()
            img.thumbnail(size)
            return ImageTk.PhotoImage(img, Image.ANTIALIAS)

        def _resize_contain(self, ev: tk.Event):
            self.after_cancel(self.__id)
            size = (ev.width, ev.height)
            self.__frames = cycle(self.__resize_frame(img, size)
                                  for img in self.__imgs)
            self.__update()

        def _resize_keep(self, ev: tk.Event):
            ratio = max(self.__imgs[0].width, self.__imgs[0].height) / \
                min(ev.width, ev.height)
            if ratio == self.__imgs[0].width or ratio == self.__imgs[0].height:
                return
            size = (int(self.__imgs[0].width / ratio),
                    int(self.__imgs[0].height / ratio))
            self.__frame = cycle(ImageTk.PhotoImage(img.resize(
                size), Image.ANTIALIAS) for img in self.__imgs)
            self.configure(image=self.__frame)

        def _resize_fill(self, ev: tk.Event):
            self.after_cancel(self.__id)
            size = (ev.width, ev.height)
            self.__frames = cycle(ImageTk.PhotoImage(
                img.resize(size), Image.ANTIALIAS) for img in self.__imgs)
            self.__update()

        def file(self, file: str):
            """Load gif from filepath.

            Args:
                file (str): File's path.
            """
            imgs = [Image.open(file)]
            try:
                for i in count(1):
                    imgs.append(imgs[0].copy())
                    imgs[0].seek(i)
            except EOFError:
                pass
            self.__imgs = tuple(imgs)
            self.__frames = cycle(ImageTk.PhotoImage(img)
                                  for img in self.__imgs)
            self.pack(fill=tk.BOTH, expand=tk.YES)
            self.__update()

        def delay(self, delay: int):
            """Set gif delay for each frame.

            Args:
                delay (int): Frame delay.
            """
            self.__delay = delay

    # Widgets from tk

    class Button(_Widget, tk.Button):
        ...

    class Canvas(_Widget, tk.Canvas):
        ...

    class Checkbutton(_Widget, tk.Checkbutton):
        ...

    class Entry(_Widget, _Text, tk.Entry):
        ...

    class Frame(_Widget, tk.Frame):
        ...

    class Label(_Widget, tk.Label):
        ...

    class LabelFrame(_Widget, tk.LabelFrame):
        ...

    class Listbox(_Widget, tk.Listbox):
        ...

    class Menu(_Widget, tk.Menu):

        def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
            if isinstance(master, self.__class__):
                label = values.pop(LABEL_ATTR)
                super().__init__(master, name, values)
                master.add_cascade(label=label, menu=self)
            elif isinstance(master, App):
                super().__init__(master, name, values)
                master.config(menu=self)

        def clear(self, _: None):
            self.delete(0, END)

        def entry(self, label: str) -> Callable:
            """Link a function to a Menubutton by his label. 

            Args:
                label (str): Corresponding label.

            Returns:
                Callable: Sub wrapper function.
            """
            def wrapper(fn: Callable) -> Callable:
                self.entryconfigure(label, command=fn)
                return fn
            return wrapper

        def nbuttons(self, labels: list[str]):
            """Add multiple normal buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_command(label=label)

        def rbuttons(self, labels: list[str]):
            """Add multiple radio buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_radiobutton(label=label)

        def cbuttons(self, labels: list[str]):
            """Add multiple check buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_checkbutton(label=label)

    class Menubutton(_Widget, tk.Menubutton):

        MODE_NORMAL = "normal"
        MODE_CHECK = "check"
        MODE_RADIO = "radio"

        def __init__(self, master: WIDGETS.Menu, name: str, values: dict[str, any]) -> None:
            label = values.pop(LABEL_ATTR)
            super().__init__(master, name, values)
            if MODE_ATTR in values:
                match values.pop(MODE_ATTR):
                    case self.MODE_CHECK:
                        master.add_checkbutton(label=label)
                    case self.MODE_RADIO:
                        master.add_radiobutton(label=label)
                    case self.MODE_NORMAL:
                        master.add_command(label=label)
                    case _:
                        raise MODE_ERROR
            else:
                master.add_command(label=label)

    class Message(_Widget, tk.Message):
        ...

    class OptionMenu(_Widget, tk.OptionMenu):
        ...

    class PanedWindow(_Widget, tk.PanedWindow):
        ...

    class Radiobutton(_Widget, tk.Radiobutton):
        ...

    class Scale(_Widget, tk.Scale):
        ...

    class Scrollbar(_Widget, tk.Scrollbar):
        ...

    class Spinbox(_Widget, tk.Spinbox):
        ...

    class Text(_Widget, _Text, tk.Text):
        ...

    class Widget(_Widget, tk.Widget):
        ...

    # Widgets from tk.ttk

    class TButton(_TtkWidget, ttk.Button):
        ...

    class TCheckbutton(_TtkWidget, ttk.Checkbutton):
        ...

    class TCombobox(_TtkWidget, ttk.Combobox):
        ...

    class TEntry(_TtkWidget, _Text, ttk.Entry):
        ...

    class TFrame(_TtkWidget, ttk.Frame):
        ...

    class TLabel(_TtkWidget, ttk.Label):
        ...

    class TLabelFrame(_TtkWidget, ttk.Labelframe):
        ...

    class TLabeledScale(_TtkWidget, ttk.LabeledScale):
        ...

    class TLabelframe(_TtkWidget, ttk.Labelframe):
        ...

    class TMenubutton(_TtkWidget, ttk.Menubutton):
        ...

    class TNotebook(_TtkWidget, ttk.Notebook):
        ...

    class TOptionMenu(_TtkWidget, ttk.OptionMenu):
        ...

    class TPanedwindow(_TtkWidget, ttk.Panedwindow):
        ...

    class TProgressbar(_TtkWidget, ttk.Progressbar):
        ...

    class TRadiobutton(_TtkWidget, ttk.Radiobutton):
        ...

    class TScale(_TtkWidget, ttk.Scale):
        ...

    class TScrollbar(_TtkWidget, ttk.Scrollbar):
        ...

    class TSeparator(_TtkWidget, ttk.Separator):
        ...

    class TSizegrip(_TtkWidget, ttk.Sizegrip):
        ...

    class TSpinbox(_TtkWidget, ttk.Spinbox):
        ...

    class TTreeview(_TtkWidget, ttk.Treeview):
        ...

    class TWidget(_TtkWidget, ttk.Widget):
        ...
