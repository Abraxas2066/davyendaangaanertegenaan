# modules/planner.py
from tkinter import ttk, messagebox
import tkinter as tk
import ipaddress

from .base import ModuleBase  # verplicht


# -------- handige helpers --------
def _set_entry(e, val: str):
    try:
        e.delete(0, "end")
        e.insert(0, val or "")
    except Exception:
        pass


class ModPlanner(ModuleBase):
    key = "planner"
    title = "IP Planner (VLSM)"

    def build_ui(self):
        f = self.parent

        # ========================= Invoer (globaal) =========================
        frm_in = ttk.LabelFrame(f, text="Invoer")
        frm_in.pack(fill="x", padx=8, pady=6)

        self.e_super = ttk.Entry(frm_in, width=18); self.e_super.insert(0, "10.10.10.0/23")
        self.e_mvid  = ttk.Entry(frm_in, width=6);  self.e_mvid.insert(0, "99")
        self.e_mname = ttk.Entry(frm_in, width=14); self.e_mname.insert(0, "MGMT")

        ttk.Label(frm_in, text="Supernet (bv 10.10.10.0/23)").grid(row=0, column=0, sticky="w")
        self.e_super.grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(frm_in, text="Mgmt VLAN ID").grid(row=1, column=0, sticky="w")
        self.e_mvid.grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(frm_in, text="Mgmt naam").grid(row=1, column=2, sticky="w")
        self.e_mname.grid(row=1, column=3, sticky="w", padx=6)

        ttk.Label(frm_in, text="SVI-IP-positie (globaal)").grid(row=2, column=0, sticky="w")
        self.cb_svi_pos = ttk.Combobox(frm_in, width=18, state="readonly",
            values=["1e host", "2e host", "laatste host", "custom (index)"])
        self.cb_svi_pos.set("1e host")
        self.cb_svi_pos.grid(row=2, column=1, sticky="w", padx=6)

        self.e_svi_idx = ttk.Entry(frm_in, width=6)
        ttk.Label(frm_in, text="Index (1..n)").grid(row=2, column=2, sticky="w")
        self.e_svi_idx.grid(row=2, column=3, sticky="w", padx=6)
        self.e_svi_idx.configure(state="disabled")

        ttk.Label(frm_in, text="Default-GW-positie (globaal)").grid(row=3, column=0, sticky="w")
        self.cb_gw_pos = ttk.Combobox(frm_in, width=18, state="readonly",
            values=["1e host", "2e host", "laatste host", "custom (index)"])
        self.cb_gw_pos.set("2e host")
        self.cb_gw_pos.grid(row=3, column=1, sticky="w", padx=6)

        self.e_gw_idx = ttk.Entry(frm_in, width=6)
        ttk.Label(frm_in, text="Index (1..n)").grid(row=3, column=2, sticky="w")
        self.e_gw_idx.grid(row=3, column=3, sticky="w", padx=6)
        self.e_gw_idx.configure(state="disabled")

        def _toggle_customs(*_):
            self.e_svi_idx.configure(state=("normal" if "custom" in self.cb_svi_pos.get() else "disabled"))
            self.e_gw_idx.configure(state=("normal" if "custom" in self.cb_gw_pos.get() else "disabled"))
        self.cb_svi_pos.bind("<<ComboboxSelected>>", _toggle_customs)
        self.cb_gw_pos.bind("<<ComboboxSelected>>", _toggle_customs)

        # ================= VLAN-rollen + per-VLAN overrides =================
        frm_roles = ttk.LabelFrame(f, text="VLAN-rollen & host-aantallen (met per-VLAN overrides)")
        frm_roles.pack(fill="x", padx=8, pady=6)
        self.role_rows = []

        # kolomkoppen (mooie grid)
        hdr = ttk.Frame(frm_roles); hdr.pack(fill="x", padx=6, pady=(4, 2))
        labels = ["VLAN", "Naam", "Hosts", "SVI-pos", "Idx", "GW-pos", "Idx", ""]
        for i, lab in enumerate(labels):
            ttk.Label(hdr, text=lab).grid(row=0, column=i, sticky="w", padx=(6 if i else 0))
        self.roles_box = ttk.Frame(frm_roles); self.roles_box.pack(fill="x")

        ttk.Button(frm_roles, text="+ Rol/VLAN",
                   command=lambda: self._add_role("", "", "10")).pack(anchor="w", padx=6, pady=6)

        # voorbeelden
        for v, n, h in [("10", "USERS", "150"), ("20", "BOSSES", "30"),
                        ("30", "SERVERS", "30"), ("40", "IT", "15"), ("50", "PRINTERS", "10")]:
            self._add_role(v, n, h)

        # ========================= Actieknoppen =========================
        bar = ttk.Frame(f); bar.pack(fill="x", padx=8, pady=6)
        ttk.Button(bar, text="Validate plan", command=self._validate_plan).pack(side="left", padx=4)
        ttk.Button(bar, text="Bereken plan", command=self._compute_plan).pack(side="left", padx=4)
        ttk.Button(bar, text="Exporteer naar modules", command=self._export_popup).pack(side="left", padx=4)
        ttk.Button(bar, text="Pop-out", command=self._popout).pack(side="left", padx=4)

        # ========================= Resultaat tabel =========================
        self.tree = ttk.Treeview(
            f,
            columns=("vlan", "name", "cidr", "mask", "svi", "gw", "dhcp1", "dhcp2", "hosts"),
            show="headings"
        )
        for c, t, w in [
            ("vlan", "VLAN", 70), ("name", "Naam", 140), ("cidr", "CIDR", 140), ("mask", "Mask", 120),
            ("svi", "SVI", 130), ("gw", "Default GW", 130),
            ("dhcp1", "DHCP start", 130), ("dhcp2", "DHCP einde", 130), ("hosts", "Leases", 80)
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self._plan = []  # list van dicts

    # ---------- VLAN-rol rij toevoegen ----------
    def _add_role(self, vid, name, hosts):
        r = ttk.Frame(self.roles_box)
        # entries/combos
        e_vid   = ttk.Entry(r, width=6);  e_vid.insert(0, vid)
        e_name  = ttk.Entry(r, width=18); e_name.insert(0, name)
        e_hosts = ttk.Entry(r, width=8);  e_hosts.insert(0, hosts)

        cb_svi = ttk.Combobox(r, width=14, state="readonly",
                              values=["(globaal)", "1e host", "2e host", "laatste host", "custom (index)"])
        cb_svi.set("(globaal)")
        e_svi_idx = ttk.Entry(r, width=6, state="disabled")

        cb_gw = ttk.Combobox(r, width=14, state="readonly",
                             values=["(globaal)", "1e host", "2e host", "laatste host", "custom (index)"])
        cb_gw.set("(globaal)")
        e_gw_idx = ttk.Entry(r, width=6, state="disabled")

        def _toggle_row_customs(*_):
            e_svi_idx.configure(state=("normal" if "custom" in cb_svi.get() else "disabled"))
            e_gw_idx.configure(state=("normal" if "custom" in cb_gw.get() else "disabled"))
        cb_svi.bind("<<ComboboxSelected>>", _toggle_row_customs)
        cb_gw.bind("<<ComboboxSelected>>", _toggle_row_customs)

        btn_del = ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self._del_role(fr))

        # grid layout
        widgets = [e_vid, e_name, e_hosts, cb_svi, e_svi_idx, cb_gw, e_gw_idx, btn_del]
        for col, w in enumerate(widgets):
            w.grid(row=0, column=col, padx=(6 if col else 0), pady=2, sticky="w")

        r.pack(anchor="w", fill="x")
        self.role_rows.append((r, e_vid, e_name, e_hosts, cb_svi, e_svi_idx, cb_gw, e_gw_idx))

    def _del_role(self, frame):
        self.role_rows = [row for row in self.role_rows if row[0] is not frame]
        frame.destroy()

    # ========================= Validatie & berekening =========================
    def _validate_plan(self):
        try:
            sn = ipaddress.ip_network(self.e_super.get().strip(), strict=False)
        except Exception:
            messagebox.showerror("Planner", "Supernet ongeldig.")
            return
        total_needed = 0
        for _, _, _, cnt, *_ in self.role_rows:
            try:
                total_needed += int(cnt.get().strip()) + 4  # +4: net, bcast, SVI, GW
            except Exception:
                pass
        if total_needed > sn.num_addresses:
            messagebox.showwarning("Planner", f"Som hosts (~{total_needed}) > capaciteit {sn.num_addresses}.")
        else:
            messagebox.showinfo("Planner", "Basisvalidatie oké ✔️")

    def _pick_host(self, usable, mode, idx_txt):
        """Kies hostadres uit lijst usable op basis van mode/index (1-gebaseerd)."""
        if not usable:
            return None
        if mode == "1e host":
            return usable[0]
        if mode == "2e host":
            return usable[1] if len(usable) >= 2 else usable[-1]
        if mode == "laatste host":
            return usable[-1]
        if mode and mode.startswith("custom"):
            try:
                n = int(idx_txt)
            except Exception:
                n = 1
            n = max(1, min(n, len(usable)))
            return usable[n - 1]
        return None  # "(globaal)" of onbekend

    def _compute_plan(self):
        warns = []

        def hosts_to_prefix(n_hosts: int) -> int:
            # #leases + 4 (net/bcast/SVI/GW)
            needed = max(0, int(n_hosts)) + 4
            size = 1; bits = 0
            while size < needed and bits < 32:
                size <<= 1; bits += 1
            return max(0, 32 - bits)

        def split_vlsm(supernet: str, demands: list):
            sn = ipaddress.ip_network(supernet, strict=False)
            free = [sn]; plan = []

            def allocate(prefix: int):
                for i, blk in enumerate(free):
                    if blk.prefixlen > prefix:
                        continue
                    cur = blk
                    while cur.prefixlen < prefix:
                        a, b = list(cur.subnets(new_prefix=cur.prefixlen + 1))
                        free[i] = b
                        free.insert(i, a)
                        cur = a
                    free.pop(i)
                    return cur
                return None

            for d in sorted(demands, key=lambda x: int(x.get("hosts", 0)), reverse=True):
                req_hosts = max(0, int(d.get("hosts", 0)))
                pref = hosts_to_prefix(req_hosts)
                if pref < sn.prefixlen:
                    return [], [f"'{d['name']}' vereist /{pref}, groter (ruimer) dan supernet {sn}."]
                blk = allocate(pref)
                if not blk:
                    return [], [f"Geen ruimte meer voor '{d['name']}' (/{pref})."]

                usable = list(blk.hosts())
                if len(usable) < 2:
                    return [], [f"Subnet {blk} heeft te weinig bruikbare adressen."]

                # per-VLAN overrides of globaal
                svi_mode = d.get("svi_mode") or self.cb_svi_pos.get()
                svi_idx  = d.get("svi_idx")  or self.e_svi_idx.get()
                gw_mode  = d.get("gw_mode")  or self.cb_gw_pos.get()
                gw_idx   = d.get("gw_idx")   or self.e_gw_idx.get()

                svi = self._pick_host(usable, svi_mode, svi_idx) or self._pick_host(usable, self.cb_svi_pos.get(), self.e_svi_idx.get())
                gw  = self._pick_host(usable, gw_mode,  gw_idx)  or self._pick_host(usable, self.cb_gw_pos.get(),  self.e_gw_idx.get())

                if gw == svi:
                    i = usable.index(gw)
                    if i + 1 < len(usable):
                        gw = usable[i + 1]; warns.append(f"SVI en GW vielen samen in {blk}; GW verschoven naar {gw}.")
                    elif i - 1 >= 0:
                        gw = usable[i - 1]; warns.append(f"SVI en GW vielen samen in {blk}; GW verschoven naar {gw}.")
                    else:
                        warns.append(f"Kon GW niet scheiden van SVI in {blk}.")

                reserved = {svi, gw}
                free_hosts = [h for h in usable if h not in reserved]
                if len(free_hosts) < req_hosts:
                    warns.append(
                        f"DHCP-range voor '{d['name']}' in {blk} is te klein voor {req_hosts} leases; "
                        f"beschikbaar {len(free_hosts)}."
                    )
                    req_hosts = len(free_hosts)

                if req_hosts == 0:
                    d1 = d2 = str(free_hosts[0]) if free_hosts else str(svi)
                else:
                    d1 = str(free_hosts[0]); d2 = str(free_hosts[req_hosts - 1])

                plan.append({
                    "vlan": d.get("vlan_id") or "",
                    "name": d.get("name") or "VLAN",
                    "network": str(blk.network_address),
                    "prefix": blk.prefixlen,
                    "mask": str(blk.netmask),
                    "svi": str(svi),
                    "gw": str(gw),
                    "dhcp_start": d1,
                    "dhcp_end": d2,
                    "hosts": req_hosts,
                })
            return plan, []

        # input verzamelen
        demands = []
        for _, e_vid, e_name, e_hosts, cb_svi, e_svi_idx, cb_gw, e_gw_idx in self.role_rows:
            nm = e_name.get().strip() or "VLAN"
            try:
                h = int(e_hosts.get().strip())
            except Exception:
                h = 0
            svi_mode = cb_svi.get(); gw_mode = cb_gw.get()
            demands.append({
                "vlan_id": (e_vid.get().strip() or None),
                "name": nm,
                "hosts": max(0, h),
                "svi_mode": (None if svi_mode == "(globaal)" else svi_mode),
                "svi_idx":  e_svi_idx.get().strip(),
                "gw_mode":  (None if gw_mode == "(globaal)" else gw_mode),
                "gw_idx":   e_gw_idx.get().strip()
            })

        # mgmt toevoegen (indien niet aanwezig)
        mvid = self.e_mvid.get().strip()
        mname = self.e_mname.get().strip() or "MGMT"
        if not any((d.get("vlan_id") or "") == mvid for d in demands):
            demands.append({"vlan_id": mvid if mvid else None, "name": mname, "hosts": 5})

        # bereken
        try:
            plan, warns_calc = split_vlsm(self.e_super.get().strip(), demands)
        except Exception as ex:
            messagebox.showerror("Planner", f"Fout tijdens VLSM: {ex}")
            return

        # tabel vullen
        self.tree.delete(*self.tree.get_children())
        self._plan = plan
        for row in plan:
            cidr = f"{row['network']}/{row['prefix']}"
            self.tree.insert("", "end",
                             values=(row["vlan"], row["name"], cidr, row["mask"],
                                     row["svi"], row["gw"], row["dhcp_start"], row["dhcp_end"], row["hosts"]))

        all_warns = warns + (warns_calc or [])
        if all_warns:
            messagebox.showwarning("Planner", "\n".join(all_warns))
        elif not plan:
            messagebox.showerror("Planner", "Geen plan gegenereerd.")
        else:
            messagebox.showinfo("Planner", "Plan berekend ✔️")

    # ========================= Export-popup =========================
    def _export_popup(self):
        if not self._plan:
            self._compute_plan()
            if not self._plan:
                return

        win = tk.Toplevel(self.parent)
        win.title("Exporteer naar modules")

        # modules kiezen
        frm_mod = ttk.LabelFrame(win, text="Kies modules")
        frm_mod.pack(fill="x", padx=10, pady=6)
        self._vars_mod = {
            "mgmt":   tk.BooleanVar(value=True),
            "vlans":  tk.BooleanVar(value=True),
            "routing": tk.BooleanVar(value=True),
        }
        ttk.Checkbutton(frm_mod, text="Mgmt",   variable=self._vars_mod["mgmt"]).pack(anchor="w", padx=8)
        ttk.Checkbutton(frm_mod, text="VLANs",  variable=self._vars_mod["vlans"]).pack(anchor="w", padx=8)
        ttk.Checkbutton(frm_mod, text="Routing", variable=self._vars_mod["routing"]).pack(anchor="w", padx=8)

        # VLAN selectie: wordt gebruikt voor VLANs én (indien Routing) voor SVI's
        frm_svi = ttk.LabelFrame(win, text="VLAN-selectie voor export (gebruikt voor VLANs én voor Routing-SVI's)")
        frm_svi.pack(fill="both", padx=10, pady=6)
        self._svi_vars = {}
        for row in self._plan:
            v = tk.BooleanVar(value=True)
            ttk.Checkbutton(frm_svi, text=f"VLAN {row['vlan']} - {row['name']}", variable=v)\
                .pack(anchor="w", padx=8)
            self._svi_vars[row["vlan"]] = v

        def do_export():
            # BELANGRIJK: we geven ALTIJD de selectie door; VLANs zal dan ook filteren
            self._export_to_modules(self._vars_mod, self._svi_vars)
            win.destroy()

        ttk.Button(win, text="OK", command=do_export).pack(pady=8)

    # ========================= Export uitvoeren =========================
    def _export_to_modules(self, vars_mod, vlan_selection_vars):
        """
        vlan_selection_vars: dict { vlan_id(str) -> BooleanVar }, bepaalt
        welke VLANs geëxporteerd worden naar zowel VLANs-module als naar Routing.
        """
        # maak een set met geselecteerde VLAN-IDs (strings)
        selected_vlans = {
            vid for vid, v in vlan_selection_vars.items() if v.get()
        }
        # als er om wat voor reden geen selectie-object is meegegeven -> exporteer alles
        if not selected_vlans:
            selected_vlans = {row["vlan"] for row in self._plan}

        app = self.parent.winfo_toplevel()
        modules = getattr(app, "modules", {})

        # ---- Mgmt (SVI-naam = VLAN-naam) ----
        if vars_mod.get("mgmt").get() and "mgmt" in modules:
            mod = modules["mgmt"]
            mvid = self.e_mvid.get().strip()
            mname = self.e_mname.get().strip() or "MGMT"

            svi_ip = ""; mask = ""; def_gw = ""
            for row in self._plan:
                if (row["vlan"] or "") == mvid:
                    svi_ip = row["svi"]; mask = row["mask"]; def_gw = row["gw"]; break

            _set_entry(mod.e_vid,  mvid)
            _set_entry(mod.e_vn,   mname)
            # SVI-naam gelijk aan VLAN-naam:
            if hasattr(mod, "e_svi"):
                _set_entry(mod.e_svi, mname)
            _set_entry(mod.e_ip,   svi_ip)
            _set_entry(mod.e_mask, mask)
            _set_entry(mod.e_gw,   def_gw)

        # ---- VLANs (alleen geselecteerde VLANs) ----
        if vars_mod.get("vlans").get() and "vlans" in modules:
            mod = modules["vlans"]

            def _fill_last_vlan_row(vid, name):
                """Compatibel vullen (tuple of dict in vlan_rows)."""
                try:
                    row = mod.vlan_rows[-1]
                except Exception:
                    return
                # dict-variant
                if isinstance(row, dict):
                    _set_entry(row.get("e_vid"),  vid)
                    _set_entry(row.get("e_name"), name)
                    return
                # tuple-varianten
                try:
                    # (e_vid, e_name, e_acc) of (frame, e_vid, e_name, e_acc)
                    if len(row) >= 3:
                        e_vid = row[-3]; e_name = row[-2]
                        _set_entry(e_vid, vid); _set_entry(e_name, name)
                except Exception:
                    pass

            for row in self._plan:
                if row["vlan"] not in selected_vlans:
                    continue
                try:
                    mod.add_vlan(vid_txt=row["vlan"], name_txt=row["name"], access_txt="")
                except TypeError:
                    mod.add_vlan()
                _fill_last_vlan_row(row["vlan"], row["name"])

        # ---- Routing (alleen geselecteerde VLANs krijgen SVI) ----
        if vars_mod.get("routing").get() and "routing" in modules:
            mod = modules["routing"]

            def _fill_last_svi_row(vid, vname, svi_ip, mask):
                """Compatibel vullen voor verschillende routing-modules."""
                try:
                    row = mod.svi_rows[-1]
                except Exception:
                    return
                # dict?
                if isinstance(row, dict):
                    _set_entry(row.get("vid"), vid)
                    _set_entry(row.get("vname"), vname)
                    if "sviname" in row:
                        _set_entry(row.get("sviname"), vname)
                    _set_entry(row.get("ip"), svi_ip)
                    _set_entry(row.get("mask"), mask)
                    return
                # tuple varianten
                try:
                    if len(row) >= 6:
                        # (frame, vid, vname, sviname, ip, mask)
                        _, e_vid, e_vname, e_sviname, e_ip, e_mask = row[:6]
                        _set_entry(e_vid, vid); _set_entry(e_vname, vname)
                        _set_entry(e_sviname, vname)
                        _set_entry(e_ip, svi_ip); _set_entry(e_mask, mask)
                    elif len(row) >= 5:
                        # (frame, vid, vname, ip, mask)
                        _, e_vid, e_vname, e_ip, e_mask = row[:5]
                        _set_entry(e_vid, vid); _set_entry(e_vname, vname)
                        _set_entry(e_ip, svi_ip); _set_entry(e_mask, mask)
                    else:
                        # (vid, vname, ip, mask) of iets dergelijks
                        e_vid, e_vname, e_ip, e_mask = row[-4:]
                        _set_entry(e_vid, vid); _set_entry(e_vname, vname)
                        _set_entry(e_ip, svi_ip); _set_entry(e_mask, mask)
                except Exception:
                    pass

            for row in self._plan:
                if row["vlan"] not in selected_vlans:
                    continue
                try:
                    mod.add_svi()
                except Exception:
                    continue
                _fill_last_svi_row(row["vlan"], row["name"], row["svi"], row["mask"])

        messagebox.showinfo("Planner", "Geëxporteerd volgens je selectie.")

    # ========================= Pop-out =========================
    def _popout(self):
        if not self._plan:
            self._compute_plan()
            if not self._plan:
                return
        win = tk.Toplevel(self.parent); win.title("IP Planner (los venster)")
        tree = ttk.Treeview(
            win,
            columns=("vlan", "name", "cidr", "mask", "svi", "gw", "dhcp1", "dhcp2", "hosts"),
            show="headings"
        )
        for c, t, w in [
            ("vlan", "VLAN", 70), ("name", "Naam", 140), ("cidr", "CIDR", 140), ("mask", "Mask", 120),
            ("svi", "SVI", 130), ("gw", "Default GW", 130),
            ("dhcp1", "DHCP start", 130), ("dhcp2", "DHCP einde", 130), ("hosts", "Leases", 80)
        ]:
            tree.heading(c, text=t); tree.column(c, width=w, anchor="w")
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        for row in self._plan:
            cidr = f"{row['network']}/{row['prefix']}"
            tree.insert("", "end",
                        values=(row["vlan"], row["name"], cidr, row["mask"],
                                row["svi"], row["gw"], row["dhcp_start"], row["dhcp_end"], row["hosts"]))

    # interface (planner zelf schrijft geen config)
    def collect(self): return {"super": self.e_super.get().strip()}
    def validate(self): return [], []
    def build_config(self, _data): return []
