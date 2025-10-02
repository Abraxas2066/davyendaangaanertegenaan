from tkinter import ttk
from .base import ModuleBase

class ModLACP(ModuleBase):
    key="lacp"; title="LACP"

    def build_ui(self):
        f=self.parent
        self.rows=[]
        self.box=ttk.Frame(f); self.box.pack(fill="x")
        bar=ttk.Frame(f); bar.pack(fill="x", pady=4)
        ttk.Button(bar, text="+ Aggregatie", command=self.add_row).pack(side="left")
        ttk.Button(bar, text="🗑 Verwijder laatste", command=self.remove_last).pack(side="left", padx=6)
        self.add_row()

    def add_row(self):
        r=ttk.Frame(self.box, relief="groove", borderwidth=1)
        e_id =ttk.Entry(r, width=6)
        e_mode=ttk.Combobox(r, values=["active","passive"], width=8); e_mode.set("active")
        e_ports=ttk.Entry(r, width=24)
        e_vl  =ttk.Entry(r, width=24)
        e_lagp=ttk.Entry(r, width=10)
        for label,w in [("agg ID",e_id),("mode",e_mode),("member ports (comma)",e_ports),("tag VLANs (comma)",e_vl),("lag vport",e_lagp)]:
            ttk.Label(r, text=label).pack(side="left"); w.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3, fill="x")
        self.rows.append((r,e_id,e_mode,e_ports,e_vl,e_lagp))

    def remove_row(self, frame):
        for i,row in enumerate(self.rows):
            if row[0] is frame:
                row[0].destroy()
                self.rows.pop(i); break

    def remove_last(self):
        if not self.rows: return
        fr, *_ = self.rows.pop()
        fr.destroy()

    def collect(self):
        aggs=[]
        for _, e_id, e_mode, e_ports, e_vl, e_lagp in self.rows:
            aggs.append({
                "id": e_id.get().strip(),
                "mode": e_mode.get().strip() or "active",
                "ports": e_ports.get().strip(),
                "vlans": e_vl.get().strip(),
                "lag_port": e_lagp.get().strip() or "1/1/1"
            })
        return {"aggs": aggs}

    def build_config(self, d):
        out=[]
        for a in d["aggs"]:
            if not a["id"]: continue
            out.append(f"lacp agg {a['id']} admin state enable")
            out.append(f"lacp agg {a['id']} mode {a['mode']}")
            if a["ports"]:
                for p in [x.strip() for x in a["ports"].split(",") if x.strip()]:
                    out.append(f"interface {p} lacp agg {a['id']}")
            if a["vlans"]:
                for vid in [x.strip() for x in a["vlans"].split(",") if x.strip()]:
                    out.append(f"vlan {vid} {a['lag_port']}")
        return out
