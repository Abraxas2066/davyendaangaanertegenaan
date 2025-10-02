from tkinter import ttk
from .base import ModuleBase
from .utils import ip

class ModAAA(ModuleBase):
    key="aaa"; title="AAA / SSH"

    def build_ui(self):
        f=self.parent
        self.e_meth=ttk.Combobox(f, values=["radius","tacacs"], width=10)
        self.e_r1  =ttk.Entry(f, width=14)
        self.e_r2  =ttk.Entry(f, width=14)
        self.e_rk  =ttk.Entry(f, width=14)
        self.e_t1  =ttk.Entry(f, width=14)
        self.e_tk  =ttk.Entry(f, width=14)
        self.v_ssh =tk.BooleanVar(value=True)
        self.v_notn=tk.BooleanVar(value=True)
        ttk.Label(f, text="Methode").grid(row=0, column=0, sticky='w'); self.e_meth.grid(row=0, column=1)
        ttk.Label(f, text="RADIUS 1").grid(row=1, column=0, sticky='w'); self.e_r1.grid(row=1, column=1)
        ttk.Label(f, text="RADIUS 2").grid(row=2, column=0, sticky='w'); self.e_r2.grid(row=2, column=1)
        ttk.Label(f, text="Radius key").grid(row=3, column=0, sticky='w'); self.e_rk.grid(row=3, column=1)
        ttk.Label(f, text="TACACS").grid(row=1, column=2, sticky='w'); self.e_t1.grid(row=1, column=3)
        ttk.Label(f, text="Tacacs key").grid(row=2, column=2, sticky='w'); self.e_tk.grid(row=2, column=3)
        ttk.Checkbutton(f, text="SSH aan", variable=self.v_ssh).grid(row=4, column=0, sticky='w')
        ttk.Checkbutton(f, text="Telnet uit", variable=self.v_notn).grid(row=4, column=1, sticky='w')

    def collect(self):
        return {
            "method": self.e_meth.get().strip(),
            "r1": self.e_r1.get().strip(),
            "r2": self.e_r2.get().strip(),
            "rk": self.e_rk.get().strip(),
            "t1": self.e_t1.get().strip(),
            "tk": self.e_tk.get().strip(),
            "ssh": self.v_ssh.get(),
            "no_telnet": self.v_notn.get()
        }

    def build_config(self, d):
        out=[]
        if d["method"]=="radius":
            out.append("aaa authentication login default radius")
            if ip(d["r1"]): out.append(f"radius server host {d['r1']} key {d['rk'] or 'RadiusSecret'}")
            if ip(d["r2"]): out.append(f"radius server host {d['r2']} key {d['rk'] or 'RadiusSecret'}")
        elif d["method"]=="tacacs":
            out.append("aaa authentication login default tacacs")
            if ip(d["t1"]): out.append(f"tacacs server host {d['t1']} key {d['tk'] or 'TacacsKey'}")
        if d["ssh"]: out.append("ip ssh server enable")
        if d["no_telnet"]: out.append("ip telnet server disable")
        return out

import tkinter as tk
tk.BooleanVar
