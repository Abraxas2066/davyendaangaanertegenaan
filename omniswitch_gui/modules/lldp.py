from tkinter import ttk
from .base import ModuleBase

class ModLLDP(ModuleBase):
    key="lldp"; title="LLDP / MED"

    def build_ui(self):
        f=self.parent
        self.v_med = tk.BooleanVar(value=False)
        self.e_voice = ttk.Entry(f, width=8)
        ttk.Label(f, text="Voice VLAN (optioneel)").grid(row=0, column=0, sticky='w'); self.e_voice.grid(row=0, column=1, sticky='w')
        ttk.Checkbutton(f, text="LLDP-MED aan", variable=self.v_med).grid(row=1, column=0, sticky='w')

    def collect(self):
        return {"med": self.v_med.get(), "voice": self.e_voice.get().strip()}

    def build_config(self, d):
        out=[
            "lldp enable",
            "lldp chassis tlv management system-name enable",
            "lldp chassis tlv management system-description enable",
            "lldp chassis tlv management system-capabilities enable",
            "lldp chassis tlv management management-address enable",
            "lldp chassis tlv management port-description enable",
        ]
        if d["med"]:
            out.append("lldp med enable")
            if d["voice"]:
                out.append(f"lldp med network-policy 1 application voice vlan {d['voice']}")
        return out

import tkinter as tk
tk.BooleanVar
