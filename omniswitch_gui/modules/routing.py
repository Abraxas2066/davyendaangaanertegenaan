from tkinter import ttk
from .base import ModuleBase
from .utils import ip, mask_ok
import ipaddress

class ModRouting(ModuleBase):
    key="routing"; title="Routing"

    def build_ui(self):
        f=self.parent
        # SVIs
        self.svi_rows=[]
        sbox=ttk.LabelFrame(f, text="SVIs"); sbox.pack(fill="x", padx=6, pady=6)
        self.svi_box=ttk.Frame(sbox); self.svi_box.pack(fill="x")
        bar1=ttk.Frame(sbox); bar1.pack(fill="x", pady=4)
        ttk.Button(bar1, text="+ SVI", command=self.add_svi).pack(side="left")
        ttk.Button(bar1, text="🗑 Laatste SVI", command=self.remove_last_svi).pack(side="left", padx=6)
        self.add_svi()
        # Static routes
        self.rt_rows=[]
        rbox=ttk.LabelFrame(f, text="Static routes"); rbox.pack(fill="x", padx=6, pady=6)
        self.rt_box=ttk.Frame(rbox); self.rt_box.pack(fill="x")
        bar2=ttk.Frame(rbox); bar2.pack(fill="x", pady=4)
        ttk.Button(bar2, text="+ Route", command=self.add_rt).pack(side="left")
        ttk.Button(bar2, text="🗑 Laatste route", command=self.remove_last_rt).pack(side="left", padx=6)
        self.add_rt()
        # OSPF
        obox=ttk.LabelFrame(f, text="OSPF"); obox.pack(fill="x", padx=6, pady=6)
        self.v_ospf=tk.BooleanVar(value=False)
        self.e_area=ttk.Entry(obox, width=6)
        self.ospf_rows=[]
        ttk.Checkbutton(obox, text="OSPF aan", variable=self.v_ospf).pack(anchor='w')
        row=ttk.Frame(obox); row.pack(anchor='w')
        ttk.Label(row, text="Area").pack(side="left"); self.e_area.pack(side="left", padx=6)
        self.obox=obox
        bar3=ttk.Frame(obox); bar3.pack(fill="x", pady=4)
        ttk.Button(bar3, text="+ OSPF network", command=self.add_ospf).pack(side="left")
        ttk.Button(bar3, text="🗑 Laatste network", command=self.remove_last_ospf).pack(side="left", padx=6)
        self.add_ospf()
        # VRRP
        vbox=ttk.LabelFrame(f, text="VRRP"); vbox.pack(fill="x", padx=6, pady=6)
        self.vrrp_rows=[]
        self.vbox=vbox
        bar4=ttk.Frame(vbox); bar4.pack(fill="x", pady=4)
        ttk.Button(bar4, text="+ VRRP group", command=self.add_vrrp).pack(side="left")
        ttk.Button(bar4, text="🗑 Laatste VRRP", command=self.remove_last_vrrp).pack(side="left", padx=6)
        self.add_vrrp()

    def add_svi(self):
        r=ttk.Frame(self.svi_box)
        vid=ttk.Entry(r, width=6); vname=ttk.Entry(r, width=12); ip_e=ttk.Entry(r, width=14); mask=ttk.Entry(r, width=14)
        for label,w in [("VLAN",vid),("VLAN naam",vname),("SVI IP",ip_e),("Mask",mask)]:
            ttk.Label(r, text=label).pack(side="left"); w.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_svi_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3); self.svi_rows.append((r,vid,vname,ip_e,mask))

    def remove_svi_row(self, frame):
        for i,row in enumerate(self.svi_rows):
            if row[0] is frame:
                row[0].destroy(); self.svi_rows.pop(i); break

    def remove_last_svi(self):
        if not self.svi_rows: return
        fr,*_ = self.svi_rows.pop(); fr.destroy()

    def add_rt(self):
        r=ttk.Frame(self.rt_box)
        dst=ttk.Entry(r, width=14); mask=ttk.Entry(r, width=14); nh=ttk.Entry(r, width=14)
        for label,w in [("Bestemming",dst),("Mask",mask),("Next-hop",nh)]:
            ttk.Label(r, text=label).pack(side="left"); w.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_rt_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3); self.rt_rows.append((r,dst,mask,nh))

    def remove_rt_row(self, frame):
        for i,row in enumerate(self.rt_rows):
            if row[0] is frame:
                row[0].destroy(); self.rt_rows.pop(i); break

    def remove_last_rt(self):
        if not self.rt_rows: return
        fr,*_ = self.rt_rows.pop(); fr.destroy()

    def add_ospf(self):
        r=ttk.Frame(self.obox)
        net=ttk.Entry(r, width=16); wild=ttk.Entry(r, width=16)
        ttk.Label(r, text="Network").pack(side="left"); net.pack(side="left", padx=6)
        ttk.Label(r, text="Wildcard").pack(side="left"); wild.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_ospf_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3); self.ospf_rows.append((r,net,wild))

    def remove_ospf_row(self, frame):
        for i,row in enumerate(self.ospf_rows):
            if row[0] is frame:
                row[0].destroy(); self.ospf_rows.pop(i); break

    def remove_last_ospf(self):
        if not self.ospf_rows: return
        fr,*_ = self.ospf_rows.pop(); fr.destroy()

    def add_vrrp(self):
        r=ttk.Frame(self.vbox)
        vrid=ttk.Entry(r, width=4); vip=ttk.Entry(r, width=14); intf=ttk.Entry(r, width=12); ip_e=ttk.Entry(r, width=14); m=ttk.Entry(r, width=14); pr=ttk.Entry(r, width=6)
        for label,w in [("VRID",vrid),("VIP",vip),("SVI naam",intf),("SVI IP",ip_e),("SVI mask",m),("Priority",pr)]:
            ttk.Label(r, text=label).pack(side="left"); w.pack(side="left", padx=6)
        ttk.Button(r, text="🗑", width=3, command=lambda fr=r: self.remove_vrrp_row(fr)).pack(side="left", padx=6)
        r.pack(anchor="w", pady=3); self.vrrp_rows.append((r,vrid,vip,intf,ip_e,m,pr))

    def remove_vrrp_row(self, frame):
        for i,row in enumerate(self.vrrp_rows):
            if row[0] is frame:
                row[0].destroy(); self.vrrp_rows.pop(i); break

    def remove_last_vrrp(self):
        if not self.vrrp_rows: return
        fr,*_ = self.vrrp_rows.pop(); fr.destroy()

    def collect(self):
        svis=[]; routes=[]; ospf=[]; vrrp=[]
        for _,vid,vname,ip_e,mask in self.svi_rows:
            svis.append({"vid": vid.get().strip(), "vname": vname.get().strip(), "ip": ip_e.get().strip(), "mask": mask.get().strip()})
        for _,dst,mask,nh in self.rt_rows:
            routes.append({"dst": dst.get().strip(), "mask": mask.get().strip(), "nh": nh.get().strip()})
        for _,n,w in self.ospf_rows:
            if n.get().strip(): ospf.append({"network": n.get().strip(), "wild": w.get().strip()})
        for _,vrid, vip, intf, ip_e, m, pr in self.vrrp_rows:
            vrrp.append({"vrid": vrid.get().strip(), "vip": vip.get().strip(), "intf": intf.get().strip(),
                         "ip": ip_e.get().strip(), "mask": m.get().strip(), "prio": pr.get().strip()})
        return {"svis": svis, "routes": routes, "ospf_on": self.v_ospf.get(), "area": self.e_area.get().strip() or "0",
                "ospf": ospf, "vrrp": vrrp}

    def validate(self):
        d=self.collect(); errs=[]
        for s in d["svis"]:
            if s["ip"] and not ip(s["ip"]): errs.append(f"SVI {s['vid']}: IP ongeldig.")
            if s["mask"] and not mask_ok(s["mask"]): errs.append(f"SVI {s['vid']}: mask ongeldig.")
        nets=[]
        for s in d["svis"]:
            if s["ip"] and s["mask"]:
                try: nets.append((s['vid'], ipaddress.ip_network(f"{s['ip']}/{s['mask']}", strict=False)))
                except Exception: errs.append(f"SVI {s['vid']}: netwerk ongeldig.")
        for i in range(len(nets)):
            for j in range(i+1, len(nets)):
                vi, ni = nets[i]; vj, nj = nets[j]
                if ni.overlaps(nj): errs.append(f"Overlap: VLAN {vi} {ni} ↔ VLAN {vj} {nj}")
        return errs, []

    def build_config(self, d):
        out=["ip routing"]
        for s in d["svis"]:
            vid=s["vid"]; vname=s["vname"] or (f"VLAN{vid}" if vid else "")
            if vid: out.append(f"vlan {vid} name {vname}")
            if vid and s["ip"] and s["mask"]:
                out.append(f"ip interface vlan{vid}ip address {s['ip']} mask {s['mask']} vlan {vid}")
        for r in d["routes"]:
            if r["dst"] and r["mask"] and ip(r["nh"]):
                out.append(f"ip route {r['dst']} {r['mask']} {r['nh']}")
        if d["ospf_on"]:
            out.append("router ospf")
            out.append(f"area {d['area']}")
            for n in d["ospf"]:
                if n["network"] and n["wild"]:
                    out.append(f"network {n['network']} {n['wild']} area {d['area']}")
        for g in d["vrrp"]:
            if g["vrid"] and ip(g["vip"]) and g["intf"]:
                if ip(g["ip"]) and g["mask"]:
                    out.append(f"ip interface {g['intf']} address {g['ip']} mask {g['mask']}")
                out.append(f"vrrp {g['vrid']} address {g['vip']}")
                if g["prio"]: out.append(f"vrrp {g['vrid']} priority {g['prio']}")
                out.append(f"vrrp {g['vrid']} enable")
        return out

import tkinter as tk
tk.BooleanVar
