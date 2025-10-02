from tkinter import ttk
from .base import ModuleBase

class ModDHCP(ModuleBase):
    key="dhcp"; title="DHCP Snooping & DAI"

    def build_ui(self):
        f=self.parent
        self.e_trust = ttk.Entry(f, width=22)
        self.e_untr  = ttk.Entry(f, width=22)
        self.v_arp   = tk.BooleanVar(value=True)
        self.e_arpvl = ttk.Entry(f, width=22)
        ttk.Label(f, text="Trusted ports").grid(row=0, column=0, sticky='w'); self.e_trust.grid(row=0, column=1, sticky='w')
        ttk.Label(f, text="Untrusted ports").grid(row=1, column=0, sticky='w'); self.e_untr.grid(row=1, column=1, sticky='w')
        ttk.Checkbutton(f, text="ARP Inspection aan", variable=self.v_arp).grid(row=2, column=0, sticky='w')
        ttk.Label(f, text="ARP VLANs (comma)").grid(row=3, column=0, sticky='w'); self.e_arpvl.grid(row=3, column=1, sticky='w')

    def collect(self):
        return {
            "trust": self.e_trust.get().strip(),
            "untrust": self.e_untr.get().strip(),
            "arp": self.v_arp.get(),
            "arp_vlans": [x.strip() for x in (self.e_arpvl.get().strip() or "").split(",") if x.strip()]
        }

    def build_config(self, d):
        out=["ip dhcp snooping enable"]
        if d["trust"]:   out.append(f"ip dhcp snooping trust {d['trust']}")
        if d["untrust"]: out.append(f"ip dhcp snooping untrust {d['untrust']}")
        if d["arp"]:
            out.append("ip arp inspection enable")
            for v in d["arp_vlans"]:
                out.append(f"ip arp inspection vlan {v} enable")
        return out

import tkinter as tk
tk.BooleanVar
