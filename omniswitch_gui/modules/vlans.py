from tkinter import ttk
from .base import ModuleBase


class ModVlans(ModuleBase):
    key = "vlans"
    title = "VLANs & Trunks"

    def build_ui(self):
        f = self.parent

        # --- VLANs ---
        self.vlan_rows = []   # list of dicts: {'frame', 'vid', 'name', 'access'}
        vbox = ttk.LabelFrame(f, text="VLANs")
        vbox.pack(fill="x", padx=6, pady=6)

        vbtnbar = ttk.Frame(vbox); vbtnbar.pack(fill="x", padx=4, pady=4)
        ttk.Button(vbtnbar, text="+ VLAN", command=self.add_vlan).pack(side="left")
        ttk.Button(vbtnbar, text="🗑 Verwijder laatste VLAN", command=self.remove_last_vlan).pack(side="left", padx=6)

        self.vlan_box = ttk.Frame(vbox)
        self.vlan_box.pack(fill="x", padx=4, pady=4)

        # start met één lege rij
        self.add_vlan()

        # --- Trunks ---
        self.trunk_rows = []  # list of dicts: {'frame', 'ports', 'vlans'}
        tbox = ttk.LabelFrame(f, text="Trunks")
        tbox.pack(fill="x", padx=6, pady=6)

        tbtnbar = ttk.Frame(tbox); tbtnbar.pack(fill="x", padx=4, pady=4)
        ttk.Button(tbtnbar, text="+ Trunk", command=self.add_trunk).pack(side="left")
        ttk.Button(tbtnbar, text="🗑 Verwijder laatste Trunk", command=self.remove_last_trunk).pack(side="left", padx=6)

        self.trunk_box = ttk.Frame(tbox)
        self.trunk_box.pack(fill="x", padx=4, pady=4)

        # start met één lege rij
        self.add_trunk()

    # ---------------- VLAN helpers ----------------
    def add_vlan(self, vid_txt: str = "", name_txt: str = "", access_txt: str = ""):
        r = ttk.Frame(self.vlan_box, relief="groove", borderwidth=1)
        ttk.Label(r, text="VLAN").pack(side="left")
        e_vid = ttk.Entry(r, width=6); e_vid.insert(0, vid_txt); e_vid.pack(side="left", padx=6)
        ttk.Label(r, text="Naam").pack(side="left")
        e_name = ttk.Entry(r, width=16); e_name.insert(0, name_txt); e_name.pack(side="left", padx=6)
        ttk.Label(r, text="Access ports").pack(side="left")
        e_acc = ttk.Entry(r, width=24); e_acc.insert(0, access_txt); e_acc.pack(side="left", padx=6)

        # individuele verwijderknop voor deze rij
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_vlan_row(fr)).pack(side="left", padx=6)

        r.pack(anchor="w", pady=3, fill="x")
        self.vlan_rows.append({"frame": r, "vid": e_vid, "name": e_name, "access": e_acc})

    def remove_vlan_row(self, frame):
        # verwijder specifieke rij (via prullenbak-knop)
        for i, row in enumerate(self.vlan_rows):
            if row["frame"] is frame:
                row["frame"].destroy()
                self.vlan_rows.pop(i)
                break

    def remove_last_vlan(self):
        if not self.vlan_rows:
            return
        row = self.vlan_rows.pop()
        row["frame"].destroy()

    # ---------------- Trunk helpers ----------------
    def add_trunk(self, ports_txt: str = "", vlans_txt: str = ""):
        r = ttk.Frame(self.trunk_box, relief="groove", borderwidth=1)
        ttk.Label(r, text="Poorten (spatie)").pack(side="left")
        e_ports = ttk.Entry(r, width=24); e_ports.insert(0, ports_txt); e_ports.pack(side="left", padx=6)
        ttk.Label(r, text="VLANs (comma)").pack(side="left")
        e_vlans = ttk.Entry(r, width=24); e_vlans.insert(0, vlans_txt); e_vlans.pack(side="left", padx=6)

        # individuele verwijderknop voor deze trunk
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_trunk_row(fr)).pack(side="left", padx=6)

        r.pack(anchor="w", pady=3, fill="x")
        self.trunk_rows.append({"frame": r, "ports": e_ports, "vlans": e_vlans})

    def remove_trunk_row(self, frame):
        for i, row in enumerate(self.trunk_rows):
            if row["frame"] is frame:
                row["frame"].destroy()
                self.trunk_rows.pop(i)
                break

    def remove_last_trunk(self):
        if not self.trunk_rows:
            return
        row = self.trunk_rows.pop()
        row["frame"].destroy()

    # ---------------- Interface ----------------
    def collect(self):
        vlans = []; trunks = []

        for row in self.vlan_rows:
            vid = row["vid"].get().strip()
            name = row["name"].get().strip() or (f"VLAN{vid}" if vid else "")
            access = row["access"].get().strip()
            # sla lege rijen over
            if not (vid or name or access):
                continue
            vlans.append({"vid": vid, "name": name, "access": access})

        for row in self.trunk_rows:
            ports = row["ports"].get().strip()
            vl = row["vlans"].get().strip()
            if not (ports or vl):
                continue
            trunks.append({"ports": ports, "vlans": vl})

        return {"vlans": vlans, "trunks": trunks}

    def validate(self):
        d = self.collect()
        errs = []; seen = set()

        for v in d["vlans"]:
            if v["vid"]:
                if not v["vid"].isdigit():
                    errs.append(f"VLAN '{v['vid']}' niet numeriek.")
                else:
                    n = int(v["vid"])
                    if n in seen:
                        errs.append(f"VLAN {n} dubbel.")
                    seen.add(n)
        return errs, []

    def build_config(self, d):
        out = []
        # VLAN definities
        for v in d["vlans"]:
            if v["vid"]:
                out.append(f"vlan {v['vid']} name {v['name']}")
        # Access-poorten per VLAN
        for v in d["vlans"]:
            if v["vid"] and v["access"]:
                out.append(f"vlan {v['vid']} port default {v['access']}")
        # Trunks (tagged VLANs op poorten)
        for t in d["trunks"]:
            ports = t["ports"].split()
            vlans = [x.strip() for x in (t["vlans"] or "").split(",") if x.strip()]
            for p in ports:
                for vid in vlans:
                    out.append(f"vlan {vid} {p}")
        return out
