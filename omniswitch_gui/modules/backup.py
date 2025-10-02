from tkinter import ttk
from .base import ModuleBase
from .utils import ip

class ModBackup(ModuleBase):
    key="backup"; title="Backup"

    def build_ui(self):
        f=self.parent
        self.e_ip=ttk.Entry(f, width=16)
        self.e_fn=ttk.Entry(f, width=18)
        ttk.Label(f, text="TFTP IP").grid(row=0, column=0, sticky='w'); self.e_ip.grid(row=0, column=1, sticky='w')
        ttk.Label(f, text="Bestandsnaam").grid(row=1, column=0, sticky='w'); self.e_fn.grid(row=1, column=1, sticky='w')

    def collect(self):
        return {"ip": self.e_ip.get().strip(), "fn": self.e_fn.get().strip()}

    def build_config(self, d):
        out=[]
        if ip(d["ip"]) and d["fn"]:
            out.append(f"copy working tftp {d['ip']} {d['fn']}")
        return out
