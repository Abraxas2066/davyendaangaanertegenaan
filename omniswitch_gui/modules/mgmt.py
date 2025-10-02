from tkinter import ttk
from .base import ModuleBase
from .utils import ip, mask_ok, same_subnet


class ModMgmt(ModuleBase):
    key = "mgmt"
    title = "Mgmt VLAN"

    def build_ui(self):
        f = self.parent
        self.e_vid  = ttk.Entry(f, width=6)
        self.e_vn   = ttk.Entry(f, width=16)
        self.e_svi  = ttk.Entry(f, width=16)
        self.e_ip   = ttk.Entry(f, width=16)
        self.e_mask = ttk.Entry(f, width=16)
        self.e_gw   = ttk.Entry(f, width=16)

        r = 0
        ttk.Label(f, text="VLAN ID").grid(row=r, column=0, sticky="w"); self.e_vid.grid(row=r, column=1, sticky="w"); r+=1
        ttk.Label(f, text="VLAN naam").grid(row=r, column=0, sticky="w"); self.e_vn.grid(row=r, column=1, sticky="w"); r+=1
        ttk.Label(f, text="SVI naam").grid(row=r, column=0, sticky="w"); self.e_svi.grid(row=r, column=1, sticky="w"); r+=1
        ttk.Label(f, text="IP").grid(row=r, column=0, sticky="w"); self.e_ip.grid(row=r, column=1, sticky="w"); r+=1
        ttk.Label(f, text="Mask").grid(row=r, column=0, sticky="w"); self.e_mask.grid(row=r, column=1, sticky="w"); r+=1
        ttk.Label(f, text="Default GW").grid(row=r, column=0, sticky="w"); self.e_gw.grid(row=r, column=1, sticky="w"); r+=1

    def collect(self):
        return {
            "vid": self.e_vid.get().strip(),
            "name": self.e_vn.get().strip() or "MGMT",
            "svi": self.e_svi.get().strip(),
            "ip": self.e_ip.get().strip(),
            "mask": self.e_mask.get().strip(),
            "gw": self.e_gw.get().strip(),
        }

    def validate(self):
        d = self.collect()
        errs = []
        if d["ip"] and not ip(d["ip"]):
            errs.append("Mgmt IP ongeldig.")
        if d["mask"] and not mask_ok(d["mask"]):
            errs.append("Mgmt mask ongeldig.")
        if d["gw"] and not ip(d["gw"]):
            errs.append("Mgmt gateway ongeldig.")
        if d["ip"] and d["mask"] and d["gw"] and not same_subnet(d["ip"], d["mask"], d["gw"]):
            errs.append("Gateway niet in zelfde subnet als Mgmt IP.")
        return errs, []

    def build_config(self, d):
        out = []
        if d["vid"]:
            out.append(f"vlan {d['vid']} name {d['name']}")
        svi = d["svi"] or (f"vlan{d['vid']}ip" if d["vid"] else "")
        if d["vid"] and d["ip"] and d["mask"] and svi:
            out.append(f"ip interface {svi} address {d['ip']} mask {d['mask']} vlan {d['vid']}")
        if d["gw"]:
            out.append(f"ip static-route 0.0.0.0/0 gateway {d['gw']}")
        return out
