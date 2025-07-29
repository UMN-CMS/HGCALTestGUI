import tkinter as tk
import sys

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state="normal")  # Allow editing
        self.text_widget.insert("end", message)  # Insert new text
        self.text_widget.see("end")  # Auto-scroll to the bottom
        self.text_widget.config(state="disabled")  # Prevent user edits

    def flush(self):
        pass  # Required for compatibility with sys.stdout