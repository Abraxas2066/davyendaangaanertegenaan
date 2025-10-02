from tkinter import ttk
from .base import ModuleBase

class ModSTP(ModuleBase):
    key="stp"; title="STP"

    def build_ui(self):
        f=self.parent
        self.e_mode=ttk.Combobox(f, values=["rstp","stp","mstp"], width=10); self.e_mode.set("rstp")
        self.e_prio=ttk.Entry(f, width=8)
        self.e_vl  =ttk.Entry(f, width=30)  # comma of leeg
        self.v_bpdu=tk.BooleanVar(value=True)
        self.e_root=ttk.Entry(f, width=18)
        r=0
        ttk.Label(f, text="Mode").grid(row=r, column=0, sticky='w'); self.e_mode.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="Priority").grid(row=r, column=0, sticky='w'); self.e_prio.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="STP-VLANs (comma, leeg = later bepalen)").grid(row=r, column=0, sticky='w'); self.e_vl.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Checkbutton(f, text="BPDU Guard", variable=self.v_bpdu).grid(row=r, column=0, sticky='w'); r+=1
        ttk.Label(f, text="Root-guard poorten").grid(row=r, column=0, sticky='w'); self.e_root.grid(row=r, column=1, sticky='w'); r+=1

    def collect(self):
        vstp=[x.strip() for x in (self.e_vl.get().strip() or "").split(",") if x.strip()]
        return {
            "mode": self.e_mode.get().strip() or "rstp",
            "prio": self.e_prio.get().strip(),
            "vlans": vstp,
            "bpdu": self.v_bpdu.get(),
            "root_ports": self.e_root.get().strip()
        }

    def validate(self):
        d=self.collect(); errs=[]
        for v in d["vlans"]:
            if not v.isdigit(): errs.append(f"STP VLAN '{v}' niet numeriek.")
        return errs, []

    def build_config(self, d):
        out=[f"spantree mode {d['mode']}"]
        if d["prio"]: out.append(f"spantree priority {d['prio']}")
        for v in d["vlans"]:
            out.append(f"spantree vlan {v} enable")
        if d["bpdu"]: out.append("spantree bpdu-guard enable")
        if d["root_ports"]: out.append(f"spantree root-guard enable {d['root_ports']}")
        return out

# tk var
import tkinter as tk
tk.BooleanVar  
