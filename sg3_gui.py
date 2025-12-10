"""
***sg3_gui***
was made using Thonny
~~~~~~~~~~~~~~~~~~~~~
Authors: Gabriel Jackson, Caleb Jacobs, Luke Chaney, Paul Corbin
Date: 12/09/2025

Tkinter GUI for SG3 frontend. Uses sg3_core.py for logic.

- Opening description window -> Main Menu

    ~Options:

  1) Open a text file (up to 10)
  2) Find a word in all open files (disabled until >=1 file)
  3) Build concordance for ONE open file (disabled until >=1 file)
  4) Close ONE of the files (disabled until >=1 file)
  5) Quit program
  
  """

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import os
import re

# Import corrected SG3_core functions
from sg3_core import (
    validate_filename,
    getContent,
    countOccurrences,
    build_Concordance,
    create_Concordance_text,
    read_Extra_Lists
)


class SG3App(tk.Tk):

    BG_MAIN = "#FAF3E3"
    BG_BOX = "#EFE5D5"
    FG_TEXT = "#2B2B2B"
    BTN_MAIN = "#A8DADC"
    BTN_ACTIVE = "#DDA15E"

    def __init__(self):
        super().__init__()

        self.open_files = {}          # filename → wordlist
        self.file_order = []          # keep order of opening

        self.title("SG3 — Word Processing System")
        self.configure(bg=self.BG_MAIN)
        self.geometry("1000x700")

        self.show_intro_popup()
                # Override the window close button (X) to use quit confirmation
        self.protocol("WM_DELETE_WINDOW", self.quit_program)

        

    # -------------------------------------------------------------
    # INTRO POPUP
    # -------------------------------------------------------------
    def show_intro_popup(self):

        intro = tk.Toplevel(self)
        intro.title("Welcome to SG3")

        win_w, win_h = 900, 550
        scr_w = intro.winfo_screenwidth()
        scr_h = intro.winfo_screenheight()
        x_pos = (scr_w - win_w) // 2
        y_pos = (scr_h - win_h) // 2

        intro.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")
        intro.configure(bg=self.BG_MAIN)
        intro.transient(self)
        intro.grab_set()

        intro.protocol("WM_DELETE_WINDOW",
                       lambda: self._close_intro(intro))

        frame = tk.Frame(intro, bg=self.BG_MAIN)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        welcome_msg = (
            "WELCOME TO SG3\n\n"
            "This program allows you to:\n"
            " • Open up to 10 text files\n"
            " • Search for a word across all open files\n"
            " • Build a concordance for any open file\n"
            " • Close files at any time\n\n"
            "Press ENTER or close this window to continue."
        )

        lbl = tk.Label(
            frame,
            text=welcome_msg,
            font=("Arial", 20, "bold"),
            bg=self.BG_MAIN,
            fg=self.FG_TEXT
        )
        lbl.pack()

        intro.bind("<Return>", lambda e: self._close_intro(intro))

    def _close_intro(self, win):
        win.grab_release()
        win.destroy()
        self.build_main_menu()
        

    # -------------------------------------------------------------
    # MAIN MENU
    # -------------------------------------------------------------
    def build_main_menu(self):

        self.menu_frame = tk.Frame(self, bg=self.BG_MAIN)
        self.menu_frame.pack(pady=40)

        title = tk.Label(
            self.menu_frame,
            text="SG3 MAIN MENU",
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Arial", 28, "bold")
        )
        title.pack(pady=10)

        self.button_style = {
            "font": ("Arial", 18, "bold"),
            "bg": self.BTN_MAIN,
            "fg": self.FG_TEXT,
            "activebackground": self.BTN_ACTIVE,
            "activeforeground": self.FG_TEXT,
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 0,
            "padx": 10,
            "pady": 10,
            "width": 28
        }

        self._menu_button("1. Open a Text File", self.gui_open_file)
        self._menu_button("2. Find a Word in All Files", self.gui_find_word)
        self._menu_button("3. Build a Concordance", self.gui_build_concordance)
        self._menu_button("4. Close a File", self.gui_close_file)
        self._menu_button("5. Quit Program", self.quit_program)

        self.files_frame = tk.Frame(self, bg=self.BG_BOX, bd=3, relief="ridge")
        self.files_frame.pack(fill="both", expand=False, padx=50, pady=20)

        label = tk.Label(
            self.files_frame,
            text="Open Files:",
            bg=self.BG_BOX,
            fg=self.FG_TEXT,
            font=("Arial", 20, "bold")
        )
        label.pack(anchor="w", padx=10, pady=10)

        self.file_listbox = tk.Listbox(
            self.files_frame,
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Arial", 16),
            bd=0,
            highlightthickness=0,
            height=6
        )
        self.file_listbox.pack(fill="both", padx=20, pady=10)

        self.update_file_listbox()

    def _menu_button(self, text, command):
        btn = tk.Button(self.menu_frame, text=text, command=command, **self.button_style)
        btn.pack(pady=10)

    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for f in self.file_order:
            wc = len(self.open_files[f])
            dc = len(set(self.open_files[f]))
            self.file_listbox.insert(tk.END, f"{f}  — {wc} words, {dc} distinct")

    # -------------------------------------------------------------
    # OPTION 1 — OPEN FILE
    # -------------------------------------------------------------
    def gui_open_file(self):

        if len(self.open_files) >= 10:
            messagebox.showerror("Limit Reached", "Maximum of 10 files allowed.")
            return

        path = filedialog.askopenfilename(
            title="Choose a .TXT File",
            filetypes=[("Text Files", "*.txt")]
        )
        if not path:
            return

        filename = os.path.basename(path)

        ok, info = validate_filename(filename)
        if not ok:
            messagebox.showerror("Invalid Name", info)
            return

        if filename in self.open_files:
            messagebox.showerror("Duplicate File", "This file is already open.")
            return

        try:
            words = getContent(path, False)
        except Exception:
            messagebox.showerror("Error", "Could not read this file.")
            return

        self.open_files[filename] = words
        self.file_order.append(filename)
        self.update_file_listbox()

    # -------------------------------------------------------------
    # OPTION 2 — FIND WORD
    # -------------------------------------------------------------
    def gui_find_word(self):

        if not self.open_files:
            messagebox.showerror("No Files Open", "Open at least one file first.")
            return

        win = tk.Toplevel(self)
        win.title("Find a Word")
        win.configure(bg=self.BG_MAIN)
        win.geometry("500x300")

        tk.Label(
            win,
            text="Enter a word to search for:",
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        entry = tk.Entry(win, font=("Arial", 18))
        entry.pack(pady=10)

        def execute_search():

            word = entry.get().strip().lower()

            if not re.fullmatch(r"[A-Za-z]+(?:-[A-Za-z]+)*", word):
                messagebox.showerror(
                    "Invalid Word",
                    "Must contain only letters or single internal hyphens."
                )
                return

            out = tk.Toplevel(win)
            out.title(f"Results for '{word}'")
            out.configure(bg=self.BG_MAIN)
            out.geometry("600x500")

            text = ScrolledText(
                out,
                bg=self.BG_BOX,
                fg=self.FG_TEXT,
                font=("Consolas", 14),
                wrap="word"
            )
            text.pack(fill="both", expand=True)

            # FIXED PARAM ORDER
            for filename in self.file_order:
                count = countOccurrences(self.open_files[filename], word)
                text.insert(tk.END, f"{filename:30s} {count} occurrences\n")

        tk.Button(win,
                  text="Search",
                  command=execute_search,
                  **self.button_style).pack(pady=20)

    # -------------------------------------------------------------
    # OPTION 3 — BUILD CONCORDANCE
    # -------------------------------------------------------------
    def gui_build_concordance(self):

        if not self.open_files:
            messagebox.showerror("No Files Open", "No files available.")
            return

        win = tk.Toplevel(self)
        win.title("Build Concordance")
        win.configure(bg=self.BG_MAIN)
        win.geometry("500x300")

        tk.Label(
            win,
            text="Select a file:",
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        cb = ttk.Combobox(win, values=self.file_order, font=("Arial", 16))
        cb.pack(pady=10)

        def build():

            selected = cb.get()
            if not selected:
                messagebox.showerror("Error", "Choose a file.")
                return

            ignore, highlight = read_Extra_Lists()
            try:
                file_index = self.file_order.index(selected)
            except ValueError:
                messagebox.showerror("Error", "Selected file is not in the open file list.")
                return

            # Passes file number into concordance for positional numbers
            file_number = file_index + 1  
            file_numbers = {selected: file_number}
            concord = build_Concordance(
                ignore,
                file_numbers
            )

            # FIXED: correct arg order: concord, highlight
            lines = create_Concordance_text(concord, highlight)

            outfile = selected + "_CONCORDANCE.txt"
            with open(outfile, "w") as f:
                f.write("\n".join(lines))

            messagebox.showinfo(
                "Concordance Saved",
                f"Saved as:\n{outfile}"
            )

        tk.Button(win, text="Build Concordance", command=build, **self.button_style).pack(pady=20)

    # -------------------------------------------------------------
    # OPTION 4 — CLOSE FILE
    # -------------------------------------------------------------
    def gui_close_file(self):

        if not self.open_files:
            messagebox.showerror("No Files Open", "Nothing to close.")
            return

        win = tk.Toplevel(self)
        win.title("Close a File")
        win.configure(bg=self.BG_MAIN)
        win.geometry("500x300")

        tk.Label(
            win,
            text="Select a file to close:",
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        cb = ttk.Combobox(win, values=self.file_order, font=("Arial", 16))
        cb.pack(pady=10)

        def close():
            f = cb.get()
            if not f:
                messagebox.showerror("Error", "Choose a file.")
                return

            del self.open_files[f]
            self.file_order.remove(f)
            self.update_file_listbox()
            win.destroy()

        tk.Button(win, text="Close File", command=close, **self.button_style).pack(pady=20)

    # -------------------------------------------------------------
    # OPTION 5 — QUIT
    # -------------------------------------------------------------
    def quit_program(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.destroy()


if __name__ == "__main__":
    app = SG3App()
    app.mainloop()
