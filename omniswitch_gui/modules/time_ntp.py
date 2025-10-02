import tkinter as tk
from tkinter import ttk
from .base import ModuleBase
from .utils import ip

class ModTime(ModuleBase):
    key = "time"; title = "Tijd & NTP"

    def build_ui(self):
        f = self.parent
        self.e_tz  = ttk.Entry(f, width=10); self.e_tz.insert(0, "CET")
        self._dst  = tk.BooleanVar(value=True)
        self.e_n1  = ttk.Entry(f, width=16)
        self.e_n2  = ttk.Entry(f, width=16)
        self.e_n3  = ttk.Entry(f, width=16)
        r=0
        ttk.Label(f, text="Timezone").grid(row=r, column=0, sticky='w'); self.e_tz.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Checkbutton(f, text="Daylight savings enable", variable=self._dst).grid(row=r, column=0, sticky='w'); r+=1
        ttk.Label(f, text="NTP 1").grid(row=r, column=0, sticky='w'); self.e_n1.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="NTP 2").grid(row=r, column=0, sticky='w'); self.e_n2.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="NTP 3").grid(row=r, column=0, sticky='w'); self.e_n3.grid(row=r, column=1, sticky='w'); r+=1

    def collect(self):
        return {
            "tz": self.e_tz.get().strip() or "CET",
            "dst": self._dst.get(),
            "ntp": [self.e_n1.get().strip(), self.e_n2.get().strip(), self.e_n3.get().strip()],
        }

    def validate(self):
        d = self.collect()
        errs=[]
        for s in d["ntp"]:
            if s and not ip(s): errs.append(f"NTP '{s}' ongeldig.")
        return errs, []

    def build_config(self, d):
        out=[f"system timezone {d['tz']}"]
        if d["dst"]: out.append("system daylight-savings-time enable")
        for s in d["ntp"]:
            if ip(s): out.append(f"ntp server {s}")
        out.append("ntp client admin-state enable")
        return out
