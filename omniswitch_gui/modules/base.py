import tkinter as tk
from tkinter import ttk, messagebox

class ModuleBase:
    key   = "base"
    title = "Base"

    def __init__(self, parent):
        self.parent = parent

    def build_ui(self): 
        pass

    def collect(self) -> dict:
        return {}

    def validate(self) -> tuple[list[str], list[str]]:
        return [], []

    def build_config(self, data: dict) -> list[str]:
        return []
