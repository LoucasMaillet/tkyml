
# Documentation on tkyml
### Generate tkinter UI

Build our interface based on a yaml file template, containing our
properties and widgets with this syntax:

# Syntax

Syntax of a yaml file template that declare a tkinter UI.

### General terms

    :name: ...  ->  Declare an attribute / call a method (accept
                    either only 1 positional arg or some **kwargs).

    _name: ...  ->  Declare an hidden value (not related with anything in tkyml).

    .name: {...} ->  Declare a class varation of the widget

    name: {...} ->  Declare a child of current widget

### Specials terms

    :type: ...  ->  Declare type of widget, derived eiter from tk and ttk or custom made (see in WIDGETS).
                    The one derived from ttk take a "T" prefix on their original name (like TButton).

    ::     ...  ->  Declare a list of methods/attributes, so you can use the same two time in a row.

# Functions


`register(cls: Callable)`
:   Register a custom widget

    Args:
        cls (Callable): Some class derived one of WIDGET

    Returns:
        Callable: Return the class to avoid error

# Classes

## `App(file: str, *args: any, **kwargs: dict[str, any])`

A base tkinter app.

Allow the creation of an app from a yaml file.

Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
be created. BASENAME will be used for the identification of the profile file (see
readprofile).
It is constructed from sys.argv[0] without extensions if None is given. CLASSNAME
is the name of the widget class.

### Ancestors (in MRO)

* tkinter.Tk
* tkinter.Misc
* tkinter.Wm
* tkyml.__Widget


### Static methods

`new(*args: any, **kwargs: dict[str, any]) ‑> tkyml.App`
:   Create a new app's window.

    Returns:
        App: The new window.

### Methods

`prot(self, name: str) ‑> Callable`
:   Link a function to some protocol.

    Args:
        name (str): Corresponding protocol.

    Returns:
        Callable: Sub wrapper function.

`loadfont(self, fontpath: str)`
:   Load custom font from file.

    Args:
        fontpath (str): Path to the font file (.otf, .tff, ...).


## `WIDGETS` 

The widgets container

### Class variables

`Button`
:   Button widget.

`Canvas`
:   Canvas widget to display graphical elements like lines or text.

`Checkbutton`
:   Checkbutton widget which is either in on- or off-state.

`Entry`
:   Entry widget which allows displaying simple text.

`Frame`
:   Frame widget which may contain other widgets and can have a 3D border.

`Gif`
:   Gif image widget based on tkinter's Label

`Img`
:   Image widget based on tkinter's Label

`Label`
:   Label widget which can display text and bitmaps.

`LabelFrame`
:   labelframe widget.

`Listbox`
:   Listbox widget which can display a list of strings.

`Menu`
:   Menu widget which allows displaying menu bars, pull-down menus and pop-up menus.

`Menubutton`
:   Menubutton widget, obsolete since Tk8.0.

`Message`
:   Message widget to display multiline text. Obsolete since Label does it too.

`OptionMenu`
:   OptionMenu which allows the user to select a value from a menu.

`PanedWindow`
:   panedwindow widget.

`Radiobutton`
:   Radiobutton widget which shows only one of several buttons in on-state.

`Scale`
:   Scale widget which can display a numerical scale.

`Scrollbar`
:   Scrollbar widget which displays a slider at a certain position.

`Spinbox`
:   spinbox widget.

`TButton`
:   Ttk Button widget, displays a textual label and/or image, and
    evaluates a command when pressed.

`TCheckbutton`
:   Ttk Checkbutton widget which is either in on- or off-state.

`TCombobox`
:   Ttk Combobox widget combines a text field with a pop-down list of
    values.

`TEntry`
:   Ttk Entry widget displays a one-line text string and allows that
    string to be edited by the user.

`TFrame`
:   Ttk Frame widget is a container, used to group other widgets
    together.

`TLabel`
:   Ttk Label widget displays a textual label and/or image.

`TLabelFrame`
:   Ttk Labelframe widget is a container used to group other widgets
    together. It has an optional label, which may be a plain text string
    or another widget.

`TLabeledScale`
:   A Ttk Scale widget with a Ttk Label widget indicating its
    current value.

    The Ttk Scale can be accessed through instance.scale, and Ttk Label
    can be accessed through instance.label

`TLabelframe`
:   Ttk Labelframe widget is a container used to group other widgets
    together. It has an optional label, which may be a plain text string
    or another widget.

`TMenubutton`
:   Ttk Menubutton widget displays a textual label and/or image, and
    displays a menu when pressed.

`TNotebook`
:   Ttk Notebook widget manages a collection of windows and displays
    a single one at a time. Each child window is associated with a tab,
    which the user may select to change the currently-displayed window.

`TOptionMenu`
:   Themed OptionMenu, based after tkinter's OptionMenu, which allows
    the user to select a value from a menu.

`TPanedwindow`
:   Ttk Panedwindow widget displays a number of subwindows, stacked
    either vertically or horizontally.

`TProgressbar`
:   Ttk Progressbar widget shows the status of a long-running
    operation. They can operate in two modes: determinate mode shows the
    amount completed relative to the total amount of work to be done, and
    indeterminate mode provides an animated display to let the user know
    that something is happening.

`TRadiobutton`
:   Ttk Radiobutton widgets are used in groups to show or change a
    set of mutually-exclusive options.

`TScale`
:   Ttk Scale widget is typically used to control the numeric value of
    a linked variable that varies uniformly over some range.

`TScrollbar`
:   Ttk Scrollbar controls the viewport of a scrollable widget.

`TSeparator`
:   Ttk Separator widget displays a horizontal or vertical separator
    bar.

`TSizegrip`
:   Ttk Sizegrip allows the user to resize the containing toplevel
    window by pressing and dragging the grip.

`TSpinbox`
:   Ttk Spinbox is an Entry with increment and decrement arrows

    It is commonly used for number entry or to select from a list of
    string values.

`TTreeview`
:   Ttk Treeview widget displays a hierarchical collection of items.

    Each item has a textual label, an optional image, and an optional list
    of data values. The data values are displayed in successive columns
    after the tree label.

`TWidget`
:   Base class for Tk themed widgets.

`Text`
:   Text widget which can display text in various forms.

`Widget`
:   Internal class.

    Base class for a widget which can be positioned with the geometry managers
    Pack, Place or Grid.
