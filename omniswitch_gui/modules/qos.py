from tkinter import ttk
from .base import ModuleBase

class ModQoS(ModuleBase):
    key="qos"; title="QoS"

    def build_ui(self):
        f=self.parent
        self.rows=[]
        self.box=ttk.Frame(f); self.box.pack(fill="x")
        bar=ttk.Frame(f); bar.pack(fill="x", pady=4)
        ttk.Button(bar, text="+ Policy", command=self.add_row).pack(side="left")
        ttk.Button(bar, text="🗑 Laatste", command=self.remove_last).pack(side="left", padx=6)
        self.add_row()

    def add_row(self):
        r=ttk.Frame(self.box, relief="groove", borderwidth=1)
        name=ttk.Entry(r, width=14)
        dscp=ttk.Entry(r, width=6)
        prio=ttk.Entry(r, width=4)
        vlan_id=ttk.Entry(r, width=6)
        rate=ttk.Entry(r, width=8)
        attach_port=ttk.Entry(r, width=8)
        attach_vlan=ttk.Entry(r, width=6)
        for label,widget in [("Naam",name),("DSCP",dscp),("Prio",prio),("VLAN",vlan_id),("Rate",rate),("→Port",attach_port),("→VLAN",attach_vlan)]:
            ttk.Label(r, text=label).pack(side="left"); widget.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3, fill="x")
        self.rows.append((r,name,dscp,prio,vlan_id,rate,attach_port,attach_vlan))

    def remove_row(self, frame):
        for i,row in enumerate(self.rows):
            if row[0] is frame:
                row[0].destroy(); self.rows.pop(i); break

    def remove_last(self):
        if not self.rows: return
        fr,*_ = self.rows.pop(); fr.destroy()

    def collect(self):
        ps=[]
        for _,name,dscp,prio,vlan_id,rate,attach_port,attach_vlan in self.rows:
            ps.append({"name": name.get().strip(),
                       "dscp": dscp.get().strip(),
                       "prio": prio.get().strip(),
                       "vid": vlan_id.get().strip(),
                       "rate": rate.get().strip(),
                       "pattach": attach_port.get().strip(),
                       "vattach": attach_vlan.get().strip()})
        return {"pols": ps}

    def build_config(self, d):
        out=[]
        for p in d["pols"]:
            if not p["name"]: continue
            out.append(f"qos policy create {p['name']}")
            if p["dscp"] and p["prio"]:
                out.append(f"qos rule create {p['name']} dscp {p['dscp']} priority {p['prio']}")
            if p["rate"] and p["vid"]:
                out.append(f"qos rule create {p['name']} vlan {p['vid']} rate-limit {p['rate']}")
            if p["pattach"]:
                out.append(f"interface ethernet {p['pattach']} qos policy {p['name']}")
            if p["vattach"]:
                out.append(f"interface vlan {p['vattach']} qos policy {p['name']}")
        return out
