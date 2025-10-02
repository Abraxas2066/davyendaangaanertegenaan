from tkinter import ttk
from .base import ModuleBase

class ModLoopback(ModuleBase):
    key="loop"; title="Loopback & Flood"

    def build_ui(self):
        f=self.parent
        self.e_ports = ttk.Entry(f, width=18)
        self.e_rect  = ttk.Entry(f, width=8)
        self.e_recmax= ttk.Entry(f, width=8)
        ttk.Label(f, text="Poorten (bv. 1/1-1/48)").grid(row=0, column=0, sticky='w'); self.e_ports.grid(row=0, column=1, sticky='w')
        ttk.Label(f, text="Recovery time (s)").grid(row=1, column=0, sticky='w'); self.e_rect.grid(row=1, column=1, sticky='w')
        ttk.Label(f, text="Recovery maximum").grid(row=2, column=0, sticky='w'); self.e_recmax.grid(row=2, column=1, sticky='w')

        self.rows=[]
        box=ttk.LabelFrame(f, text="Flood limits"); box.grid(row=3, column=0, columnspan=2, sticky='ew', padx=6, pady=6)
        self.box=ttk.Frame(box); self.box.pack(fill="x")
        bar=ttk.Frame(box); bar.pack(fill="x", pady=4)
        ttk.Button(bar, text="+ Regel", command=self.add_row).pack(side="left")
        ttk.Button(bar, text="🗑 Laatste", command=self.remove_last).pack(side="left", padx=6)
        self.add_row()

    def add_row(self):
        r=ttk.Frame(self.box)
        t=ttk.Combobox(r, values=["bcast","mcast","uucast"], width=8)
        rate=ttk.Entry(r, width=6)
        act=ttk.Combobox(r, values=["","shutdown"], width=10)
        ports=ttk.Entry(r, width=12)
        for label,w in [("Type",t),("Rate %",rate),("Actie",act),("Poorten",ports)]:
            ttk.Label(r, text=label).pack(side="left"); w.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3)
        self.rows.append((r,t,rate,act,ports))

    def remove_row(self, frame):
        for i,row in enumerate(self.rows):
            if row[0] is frame:
                row[0].destroy(); self.rows.pop(i); break

    def remove_last(self):
        if not self.rows: return
        fr, *_ = self.rows.pop(); fr.destroy()

    def collect(self):
        fl=[]
        for _,t,rate,act,ports in self.rows:
            fl.append({"type": t.get(), "rate": rate.get(), "action": act.get(), "ports": ports.get()})
        return {"ports": self.e_ports.get().strip(),
                "rect": self.e_rect.get().strip(),
                "recmax": self.e_recmax.get().strip(),
                "flood": fl}

    def build_config(self, d):
        out=["loopback-detection enable"]
        if d["ports"]: out.append(f"loopback-detection port {d['ports']} enable")
        if d["rect"]:  out.append(f"violation port {d.get('ports','1/1-1/48')} recovery-time {d['rect']}")
        if d["recmax"]:out.append(f"violation recovery-maximum {d['recmax']}")
        for fl in d["flood"]:
            t=fl["type"]; ports=fl["ports"] or "1/1-1/48"
            if fl["rate"]:   out.append(f"interfaces port {ports} flood-limit {t} rate cap% {fl['rate']}")
            if fl["action"]: out.append(f"interfaces port {ports} flood-limit {t} action {fl['action']}")
        return out
