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
from typing import Callable

# To build application
from multiprocessing import Process
import yaml

# To load custom fonts
from tkextrafont import Font
from pathlib import Path


# Widgets
from .widgets import tk, _BaseWidget, WIDGETS, _C


__author__ = "Lucas Maillet"
__email__ = "loucas.maillet.pro@gmail.com"
__license__ = "MIT"
__version__ = "0.0.4"
__status__ = "Production"
__repository__ = "https://github.com/LoucasMaillet/tkyml"


__TAG_YML_SEQ = "tag:yaml.org,2002:seq"  # To parse yaml


def define(cls: _C) -> _C:
    """Define a custom widget

    Args:
        cls (_C): Some class derived one of WIDGET

    Returns:
        _C: Return the class to avoid error
    """
    setattr(WIDGETS, cls.__name__, cls)
    return cls


class WidgetMap:

    @classmethod
    def __init__(cls, app: App) -> None:
        searchdict = dict(cls.__dict__)
        searchdict.pop("__module__")
        for wname, wpath in searchdict.items():
            if isinstance(wpath, str):
                setattr(cls, wname, app.nametowidget(wpath))


class App(tk.Tk, _BaseWidget):

    """A base tkinter app.

    Allow the creation of an app from a yaml file.
    """

    def __init__(self, file: str, *args: any, **kwargs: dict[str, any]):
        super().__init__(*args, **kwargs)
        with open(file, 'r') as file:
            self._set(yaml.load(file, Loader=yaml.SafeLoader))

    @classmethod
    def new(cls, *args: any, **kwargs: dict[str, any]) -> App:
        """Create a new app's window.

        Returns:
            App: A new window.
        """
        Process(target=cls, args=args, kwargs=kwargs).start()

    def proto(self, name: str) -> Callable:
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

    def loadfont(self, filepath: str):
        """Load a font in app

        Args:
            filepath (str): Path to the font
        """
        Font(self, file=filepath, name=Path(filepath).name)


# Load sequence as tuple (optimized)
def __construct_sequence(loader, node):
    yield tuple(loader.construct_sequence(node))


yaml.SafeLoader.add_constructor(__TAG_YML_SEQ, __construct_sequence)
