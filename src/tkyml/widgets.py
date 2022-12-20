# Typing
from typing import Callable, Iterable, TypeAlias, Union, TypeVar
from enum import StrEnum

# For tkinter wigdget
from inspect import ismethod
from tkinter import ttk
import tkinter as tk

# For image widgets
from PIL import Image, ImageTk, ImageColor
from itertools import count, cycle

# For transparent widgets
import win32gui
import win32api
import win32con


_C = TypeVar('_C', bound=object)  # To decorate and keep track of classes' type
_Ink: TypeAlias = str | int | Union[tuple[int, int, int], tuple[int, int, int, int]]


class Prefix(StrEnum):
    # For .yml declaration
    HID = '_'
    ATTR = ':'
    CLASS = '.'


class Event(StrEnum):
    # For Custom event
    CHANGE = "<<Change>>"


LABEL_ATTR = Prefix.ATTR + "label"
MODE_ATTR = Prefix.ATTR + "mode"
END = tk.END + "-1c"
MODE_ERROR = TypeError("Mode not found, please refer to docstring.")


# Widgets bases class


class _BaseWidget:

    __variants: dict[str, dict]  # Variant of the widget

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

    def __setattr(self, __name: str, __value: any) -> None:
        attr = getattr(self, __name, None)
        if not attr is None:
            if ismethod(attr):
                if isinstance(__value, dict):
                    attr(**__value)
                elif __value == None:
                    attr()
                else:
                    attr(__value)
            else:
                setattr(self, __name, __value)
        elif __name == '':
            self.__attributes(__value)
        else:
            self.configure({__name: __value})

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
        win32gui.SetLayeredWindowAttributes(id, colorkey, 0, win32con.LWA_COLORKEY)

    def _set(self, values: dict[str, any]):
        """Set attributes, methods, ... from values.

        Args:
            values (dict[str, any]): Some settings values.
        """
        self.__variants = {}
        for name, value in values.items():
            match name[0]:
                case Prefix.ATTR:  # Attribute declaration / Method call
                    self.__setattr(name[1:], value)

                case Prefix.CLASS:
                    self.__variants[name[1:]] = value

                case Prefix.HID:  # Hided value
                    continue

                case _:
                    getattr(WIDGETS, value.pop(Prefix.ATTR + "type"))(self, name, value)

    def _variant(self, values: dict[str, any]):
        """Update attributes, methods, ... from values.

        Args:
            values (dict[str, any]): Some settings values.
        """
        for name, value in values.items():
            match name[0]:
                case Prefix.ATTR:  # Attribute declaration / Method call
                    self.__setattr(name[1:], value)

                case Prefix.HID:  # Hided value
                    continue

                case _:
                    self.nametowidget(name)._variant(value)

    def variant(self, variant_name: str):
        """Update widget class.

        Args:
            variant_name (str): The variant name.
        """
        self._variant(self.__variants[variant_name])

    def nametowidget(self, name: str) -> _C:
        """Return the Tkinter instance of a widget identified by its Tcl name NAME.

        Args:
            name (str): Name to the widget.

        Returns:
            _C: The corresponding widget.
        """
        return tk.Tk.nametowidget(self, name)

    def empty(self):
        """Remove all childs."""
        for child in self.winfo_children():
            child.destroy()

    def event(self, name: str, add=True) -> Callable:
        """Link a function to some event. 

        Args:
            name (str): Corresponding event.
            add (bool, optional): If we add or overwrite the current function binded. Defaults to False.

        Returns:
            Callable: Sub wrapper function.
        """
        def wrapper(fn: Callable) -> Callable:
            if fn.__code__.co_argcount - ismethod(fn):
                self.bind(name, fn, add)
            else:
                self.bind(name, lambda _: fn(), add)
            return fn
        return wrapper

    def hidecl(self, color: _Ink):
        """Hide some color

        Args:
            color (_Ink): Color that will disappear.
        """
        self.__hide(ImageColor.getrgb(color))

    def hidebg(self, color: _Ink):
        """Hide a background color value

        Args:
            color (_Ink): Color that will disappear.
        """
        rgb = ImageColor.getrgb(color)
        self["bg"] = "#{:02x}{:02x}{:02x}".format(*rgb)
        self.__hide(rgb)


class _Widget(_BaseWidget):

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

    def hidebg(self, color: _Ink):
        """Hide a background color value

        Args:
            color (_Ink): Color that will disappear.
        """
        rgb = ImageColor.getrgb(color)
        self.style(background="#{:02x}{:02x}{:02x}".format(*rgb))
        self.__hide(rgb)

    def style(self, **values: dict[str, any]):
        """Style a ttk widget.

        Args:
            **values (dict[str, any]): Styles key & values.
        """
        stylename = f"""{self.winfo_name()}.{self.winfo_class()}"""
        ttk.Style().configure(stylename, **values)
        self.configure(style=stylename)

    def layout(self, values: list[any]):
        """Add a layout.

        Args:
            values (list[any]): Layout values.
        """
        stylename = f"""{self.winfo_name()}.{self.winfo_class()}"""
        ttk.Style(self).layout(stylename, [values])
        self.configure(style=stylename)


class _Entry:

    @property
    def value(self) -> str:
        """Get actual text.

        Returns:
            str: Widget's text
        """
        return self.get()

    @value.setter
    def value(self, string: str):
        """Overwrite text.

        Args:
            string (str): New text
        """
        self.clear()
        self.insert(tk.END, string)

    def clear(self):
        """Empty text.
        """
        self.delete(0, tk.END)


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


class _OptionMenu:
    
    _menu: tk.Menu
    label: tk.StringVar
    value = None

    def default(self, label: str, value: any = None):
        """Set default label & value.

        Args:
            label (str): Default label.
            value (any, optional): Default value. Defaults to None.
        """
        self.label.set(label)
        self.value = value

    def __select_cmd(self, label: str, value: any):
        def __cmd():
            self.label.set(label)
            self.value = value
            self.event_generate(Event.CHANGE)
        return __cmd

    def select(self, **label_values: dict[str, any]):
        """Add select command, that change menu label and value.

        Args:
            label_values** (dict[str, any]): Combinaison of key-values.
        """
        for label, value in label_values.items():
            self._menu.add_command(label=label, command=self.__select_cmd(label, value))

    def __choice_cmd(self, value: any):
        def __cmd():
            self.value = value
            self.event_generate(Event.CHANGE)
        return __cmd

    def choice(self, **label_values: Iterable[any]):
        """Add select command, that change menu value.

        Args:
            label_values** (dict[str, any]): Combinaison of key-values.
        """
        for label, value in label_values.items():
            self._menu.add_radiobutton(label=label, command=self.__choice_cmd(value))

    def __flag_cmd(self, label: str, flag: int):
        def __cmd():
            self.label.set(label)
            self.value = self.value ^ flag
            self.event_generate(Event.CHANGE)
        return __cmd

    def flags(self, **label_flags):
        """Add select command, that change menu value with binaray flags.

        Args:
            label_flags** (dict[str, any]): Combinaison of key-values.
        """
        for label, flag in label_flags.items():
            self._menu.add_checkbutton(label=label, command=self.__flag_cmd(label, flag))


class _DefaultInit:

    def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
        super().__init__(master=master, name=name)
        self._set(values)


# Usable Widget storage


class WIDGETS:

    """The widgets storage
    """

    class Img(_DefaultInit, _Widget, _Img, tk.Label):

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

        def __set_data(self):
            self.__frame = ImageTk.PhotoImage(self.__img)
            self.configure(image=self.__frame)

        def file(self, file: str):
            """Load image from filepath.

            Args:
                file (str): File's path.
            """
            self.__img = Image.open(file)
            self.__set_data()

        def data(self, img: Image.Image):
            """Change image data

            Args:
                img (Image.Image): New image
            """
            self.__img = img
            self.__set_data()

    class Gif(_DefaultInit, _Widget, tk.Label):

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

        def __set_data(self):
            self.__frames = cycle(ImageTk.PhotoImage(img)
                                  for img in self.__imgs)
            self.pack(fill=tk.BOTH, expand=tk.YES)
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
            self.__set_data()

        def data(self, imgs: Iterable[Image.Image]):
            """Change image data

            Args:
                imgs (Iterable[Image.Image]): New images
            """
            self.__imgs = tuple(imgs)
            self.__set_data()

        def delay(self, delay: int):
            """Set gif delay for each frame.

            Args:
                delay (int): Frame delay.
            """
            self.__delay = delay

    # Widgets from tk

    class Button(_DefaultInit, _Widget, tk.Button):
        ...

    class Canvas(_DefaultInit, _Widget, tk.Canvas):
        ...

    class Checkbutton(_DefaultInit, _Widget, tk.Checkbutton):
        ...

    class Entry(_DefaultInit, _Widget, _Entry, tk.Entry):
        ...

    class Frame(_DefaultInit, _Widget, tk.Frame):
        ...

    class Label(_DefaultInit, _Widget, tk.Label):
        ...

    class LabelFrame(_DefaultInit, _Widget, tk.LabelFrame):
        ...

    class Listbox(_DefaultInit, _Widget, tk.Listbox):
        ...

    class Menu(_DefaultInit, _Widget, tk.Menu):

        def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
            if isinstance(master, self.__class__):
                label = values.pop(LABEL_ATTR)
                super().__init__(master, name, values)
                master.add_cascade(label=label, menu=self)
            elif isinstance(master, tk.Tk):
                super().__init__(master, name, values)
                master.config(menu=self)

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

        def button(self, labels: list[str]):
            """Add multiple normal buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_command(label=label)

        def choice(self, labels: list[str]):
            """Add multiple radio buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_radiobutton(label=label)

        def check(self, labels: list[str]):
            """Add multiple check buttons.

            Args:
                labels (list[str]): List of buttons' label.
            """
            for label in labels:
                self.add_checkbutton(label=label)

    class Menubutton(_DefaultInit, _Widget, tk.Menubutton):

        MODE_NORMAL = "normal"
        MODE_CHECK = "check"
        MODE_RADIO = "radio"

        def __init__(self, master: tk.Menu, name: str, values: dict[str, any]) -> None:
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

    class Message(_DefaultInit, _Widget, tk.Message):
        ...

    class OptionMenu(_Widget, _OptionMenu, tk.OptionMenu):
            
        def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
            self.label = tk.StringVar(master)
            super().__init__(master, self.label, None)
            # Weird trick to actually rename the widget
            self._menu = self.children["menu"]
            self._menu.delete(0) # Remove default item
            master.children.pop(self.winfo_name())
            master.children[name] = self
            self._set(values)

    class PanedWindow(_DefaultInit, _Widget, tk.PanedWindow):
        ...

    class Radiobutton(_DefaultInit, _Widget, tk.Radiobutton):
        ...

    class Scale(_DefaultInit, _Widget, tk.Scale):
        ...

    class Scrollbar(_DefaultInit, _Widget, tk.Scrollbar):
        ...

    class Spinbox(_DefaultInit, _Widget, tk.Spinbox):
        ...

    class Text(_DefaultInit, _Widget, tk.Text):
            
        @property
        def value(self) -> str:
            """Get actual text.

            Returns:
                str: Widget's text
            """
            return self.get("1.0", END)

        @value.setter
        def value(self, string: str):
            """Overwrite text.

            Args:
                string (str): New text
            """
            self.clear()
            self.insert(tk.END, string)

        def clear(self):
            """Empty text.
            """
            self.delete("1.0", tk.END)

    class Widget(_DefaultInit, _Widget, tk.Widget):
        ...

    # Widgets from tk.ttk

    class TButton(_DefaultInit, _TtkWidget, ttk.Button):
        ...

    class TCheckbutton(_DefaultInit, _TtkWidget, ttk.Checkbutton):
        ...

    class TCombobox(_DefaultInit, _TtkWidget, ttk.Combobox):
        ...

    class TEntry(_DefaultInit, _TtkWidget, _Entry, ttk.Entry):
        ...

    class TFrame(_DefaultInit, _TtkWidget, ttk.Frame):
        ...

    class TLabel(_DefaultInit, _TtkWidget, ttk.Label):
        ...

    class TLabelFrame(_DefaultInit, _TtkWidget, ttk.Labelframe):
        ...

    class TLabeledScale(_DefaultInit, _TtkWidget, ttk.LabeledScale):
        ...

    class TLabelframe(_DefaultInit, _TtkWidget, ttk.Labelframe):
        ...

    class TMenubutton(_DefaultInit, _TtkWidget, ttk.Menubutton):
        ...

    class TNotebook(_DefaultInit, _TtkWidget, ttk.Notebook):
        ...

    class TOptionMenu(_TtkWidget, _OptionMenu, ttk.OptionMenu):
            
        def __init__(self, master: tk.Widget, name: str, values: dict[str, any]) -> None:
            self.label = tk.StringVar(master)
            super().__init__(master, self.label)
            # Weird trick to actually rename the widget
            self._menu = self.children["!menu"]
            master.children.pop(self.winfo_name())
            master.children[name] = self
            self._set(values)

    class TPanedwindow(_DefaultInit, _TtkWidget, ttk.Panedwindow):
        ...

    class TProgressbar(_DefaultInit, _TtkWidget, ttk.Progressbar):
        ...

    class TRadiobutton(_DefaultInit, _TtkWidget, ttk.Radiobutton):
        ...

    class TScale(_DefaultInit, _TtkWidget, ttk.Scale):
        ...

    class TScrollbar(_DefaultInit, _TtkWidget, ttk.Scrollbar):
        ...

    class TSeparator(_DefaultInit, _TtkWidget, ttk.Separator):
        ...

    class TSizegrip(_DefaultInit, _TtkWidget, ttk.Sizegrip):
        ...

    class TSpinbox(_DefaultInit, _TtkWidget, ttk.Spinbox):
        ...

    class TTreeview(_DefaultInit, _TtkWidget, ttk.Treeview):
        ...

    class TWidget(_DefaultInit, _TtkWidget, ttk.Widget):
        ...
