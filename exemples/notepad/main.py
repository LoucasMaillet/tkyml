# coding: utf-8


from tkinter import messagebox as mb, filedialog as fd
import tkyml as tky


MAX_PILE = 50


class Pile(list): # Implemented for a simple ctr+z / ctrl+maj+z but doesn't work in the end, not related to tkyml though

    """An undo/redo pile"""

    __top: int

    def __init__(self, top: int):
        self.__top = top

    def pack(self, item: any):
        if len(self) >= self.__top:
            self.pop(0)
        self.append(item)


class App(tky.App): # Represent the window object

    filename = ""
    saved = True

    def __init__(self):

        super().__init__("window.yml")

        self.name = self.title()
        self.sub_name = f"Unsaved - {self.name}"
        self.undo = Pile(MAX_PILE)
        self.redo = Pile(MAX_PILE)
        self.undo.pack('')

        # Get needed widget

        self.main = self.nametowidget("main")
        self.menu = self.nametowidget("menu")
        self.fmenu = self.menu.nametowidget("file_menu")
        self.emenu = self.menu.nametowidget("edit_menu")

        # START - EVENTS DEFENITION

        @self.fmenu.entry("Save as ...") # Bind to entry labelled "Save as ..." of menu.file_menu
        def _():
            if self.saveas():
                self.save()

        @self.event("<Control-z>") # Bind to event <Control-z> of app
        @self.emenu.entry("Undo") # And also to entry labelled "Undo" of menu.edit_menu
        def _():
            if self.undo:
                self.redo.pack(self.main.get_text())
                self.main.delete("1.0", tky.tk.END)
                self.main.text(self.undo.pop())

        @self.event("<Control-Z>")
        @self.emenu.entry("Redo")
        def _():
            if self.redo:
                self.undo.pack(self.main.get_text())
                self.main.delete("1.0", tky.tk.END)
                self.main.text(self.redo.pop())

        @self.emenu.entry("Cut")
        def _():
            self.clipboard_clear()
            self.clipboard_append(self.main.selection_get())
            self.selection_get()
            self.main.delete('sel.first','sel.last')

        @self.emenu.entry("Copy")
        def _():
            self.clipboard_clear()
            self.clipboard_append(self.main.selection_get())
            self.selection_get()

        @self.emenu.entry("Paste")
        def _():
            self.main.insert(tky.tk.INSERT, self.clipboard_get())

        @self.event("<Control-s>")
        @self.fmenu.entry("Save")
        def _():
            if self.saveas():
                self.save()
                
                @self.event("<Control-s>")
                @self.fmenu.entry("Save")
                def _():
                    self.undo.pack(self.main.get_text())
                    self.save()
            
        self.event("<Control-o>")(self.open)
        self.fmenu.entry("Open File")(self.open)

        self.event("<Control-n>")(self.new)
        self.fmenu.entry("New Window")(self.new)

        self.fmenu.entry("Exit")(self.close)

        @self.menu.entry("Help")
        def _():
            mb.showinfo("Help", f"Notepad (tkyml v{tky.__version__})\n\nSee more on the repository:\n{tky.__repository__}")

        self.prot("WM_DELETE_WINDOW")(self.close) # Bind to protocol "WM_DELETE_WINDOW" of app

        @self.main.event("<Key>")
        def _():
            if self.saved:
                self.saved = False
                self.title(f"*{self.sub_name}")
            
        @self.main.event("<Button-1>") # Bind to event "<Button-1>" of main
        def _():
            self.main.delete(1.0, tky.tk.END)

            @self.event("<FocusIn>")
            def _():
                self.main.set_class("focus") # Set class ".focus" on main

            @self.event("<FocusOut>")
            def _():
                self.main.set_class("unfocus") # Set class ".unfocus" on main

            self.main.unbind("<Button-1>")

        # END - EVENTS DEFENITION

        self.mainloop()

    def open(self):
        self.filename = fd.askopenfilename(title="Open", defaultextension=".text", filetypes=(
                ("Text files", "*.text"),
                ("All files", "*.*")
        ))
        if self.filename:
            with open(self.filename, 'r') as file:
                self.main.text(file.readline())

    def saveas(self) -> bool:
        self.filename = fd.asksaveasfilename(title="Save as", defaultextension=".txt", filetypes=(
                ("Text files", "*.txt"),
                ("All files", "*.*")
        ))
        if self.filename:
            self.sub_name = f"{self.filename} - {self.name}"
            return True
        return False

    def save(self):
        self.title(self.sub_name)
        with open(self.filename, 'w') as file:
            file.write(self.main.get_text())
        self.saved = True

    def close(self):
        if not self.saved:
            match mb.askyesnocancel("Warning", "Do you want to save your modifications ?", icon='warning'):
                case True:
                    if not self.filename and not self.saveas():
                        return
                    self.save()
                case None:
                    return
        self.destroy()


if __name__ == "__main__":
    App()