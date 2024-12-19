from .communicator import Communicator
import tkinter as tk
from tkinter import ttk, WORD
from scraper.scraper import Backend
from .common import Common
import threading


class Frontend:
    def __init__(self):
        """Initializing frontend layout"""

        # Root window setup
        self.root = tk.Tk()
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.root.title("Google Maps Scraper")

        # Set a modern background color
        self.root.configure(bg="#F8F9FA")

        """Title Label"""
        self.title_label = tk.Label(
            self.root,
            text="Google Maps Scraper",
            font=("Arial", 26, "bold"),
            bg="#F8F9FA",
            fg="#343A40",
        )
        self.title_label.pack(pady=20)

        """Input Frame"""
        self.input_frame = tk.Frame(self.root, bg="#F8F9FA")
        self.input_frame.pack(pady=20)

        # Search Entry
        tk.Label(
            self.input_frame,
            text="Search Query:",
            font=("Arial", 14),
            bg="#F8F9FA",
            fg="#495057",
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.search_box = ttk.Entry(self.input_frame, width=40, font=("Arial", 14))
        self.search_box.grid(row=0, column=1, padx=15, pady=10)

        # Output Format
        tk.Label(
            self.input_frame,
            text="Output Format:",
            font=("Arial", 14),
            bg="#F8F9FA",
            fg="#495057",
        ).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.outputFormatButton = ttk.Combobox(
            self.input_frame, values=["Excel+Json", "Excel", "Json", "Csv"], state="readonly"
        )
        self.outputFormatButton.grid(row=1, column=1, padx=15, pady=10)
        self.outputFormatButton.set("Excel+Json")  # Default format

        # Headless Mode
        self.healdessCheckBoxVar = tk.IntVar(value=1)
        self.healdessCheckBox = tk.Checkbutton(
            self.input_frame,
            text="Disable Debug Mode",
            variable=self.healdessCheckBoxVar,
            bg="#F8F9FA",
            fg="#495057",
            font=("Arial", 12),
        )
        self.healdessCheckBox.grid(row=2, column=1, pady=10, sticky="w")

        """Submit Button"""
        self.submit_button = ttk.Button(
            self.root,
            text="Start Scraping",
            command=self.getinput,
            style="Submit.TButton",
        )
        self.submit_button.pack(pady=10)

        """Message Display"""
        self.show_text = tk.Text(
            self.root,
            font=("Arial", 12),
            height=15,
            width=80,
            state="disabled",
            wrap=WORD,
            bg="#FFFFFF",
            fg="#212529",
            bd=2,
            relief="groove",
        )
        self.show_text.pack(padx=20, pady=20)

        """Styling"""
        self.style = ttk.Style()
        self.style.configure(
            "Submit.TButton",
            font=("Arial", 14, "bold"),
            background="#28A745",
            foreground="black",
            padding=10,
        )
        self.style.map(
            "Submit.TButton", background=[("active", "#218838")], foreground=[("active", "white")]
        )

        self.__replacingtext("Welcome to Google Maps Scraper")

        # Initialize communicator
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_frontend_object(self)

    def __replacingtext(self, text):
        """This function will insert the text in the message box"""

        self.show_text.config(state="normal")
        self.show_text.insert(tk.END, "• " + text + "\n\n")
        self.show_text.see(tk.END)
        self.show_text.config(state="disabled")

    def getinput(self):
        self.searchQuery = self.search_box.get()
        self.outputFormatValue = self.outputFormatButton.get()

        if len(self.searchQuery) == 0 and len(self.outputFormatValue) == 0:
            self.__replacingtext(text="Oops! Your query is not valid")

        elif len(self.searchQuery) == 0:
            self.__replacingtext(text="Oops! You did an empty search")
        elif len(self.outputFormatValue) == 0:
            self.__replacingtext(text="Oops! You did not select an output format")

        else:
            self.submit_button.config(state="disabled")
            self.searchQuery = self.searchQuery.lower()
            self.outputFormatValue = self.outputFormatValue.lower()
            self.headlessMode = self.healdessCheckBoxVar.get()

            # Start the backend in a new thread
            self.threadToStartBackend = threading.Thread(
                target=self.startscraping
            )
            self.threadToStartBackend.start()

    def closingbrowser(self):
        """Close the app cleanly"""

        try:
            Common.set_close_thread()
            self.root.destroy()
        except:
            pass

    def startscraping(self):
        backend = Backend(
            self.searchQuery,
            self.outputFormatValue,
            healdessmode=self.headlessMode
        )

        backend.mainscraping()
        self.__replacingtext("Scraping completed successfully!")
        self.end_processing()

    def end_processing(self):
        self.submit_button.config(state="normal")
        try:
            if self.threadToStartBackend.is_alive():
                self.threadToStartBackend.join()
        except:
            pass

    def messageshowing(self, message):
        self.__replacingtext(message)


if __name__ == "__main__":
    app = Frontend()
    app.root.protocol("WM_DELETE_WINDOW", app.closingbrowser)
    app.root.mainloop()
