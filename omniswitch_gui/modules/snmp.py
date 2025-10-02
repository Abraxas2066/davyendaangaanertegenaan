from tkinter import ttk
from .base import ModuleBase
from .utils import ip

class ModSNMP(ModuleBase):
    key="snmp"; title="SNMPv3"

    def build_ui(self):
        f=self.parent
        self.e_user=ttk.Entry(f, width=12)
        self.e_auth=ttk.Entry(f, width=12)
        self.e_enc =ttk.Entry(f, width=12)
        self.e_trap=ttk.Entry(f, width=16)
        ttk.Label(f, text="User").grid(row=0, column=0, sticky='w'); self.e_user.grid(row=0, column=1, sticky='w')
        ttk.Label(f, text="Auth (MD5)").grid(row=1, column=0, sticky='w'); self.e_auth.grid(row=1, column=1, sticky='w')
        ttk.Label(f, text="Encrypt (AES)").grid(row=2, column=0, sticky='w'); self.e_enc.grid(row=2, column=1, sticky='w')
        ttk.Label(f, text="Trap target IP").grid(row=3, column=0, sticky='w'); self.e_trap.grid(row=3, column=1, sticky='w')

    def collect(self):
        return {"user": self.e_user.get().strip(), "auth": self.e_auth.get().strip(), "enc": self.e_enc.get().strip(), "trap": self.e_trap.get().strip()}

    def build_config(self, d):
        out=[]
        if d["user"] and d["auth"] and d["enc"]:
            out += [
                f"snmpv3 user {d['user']} auth md5 {d['auth']} encrypt aes {d['enc']}",
                "snmpv3 group monitor read netmon write none notify netmon",
                "snmpv3 view all included .1",
                "snmpv3 access monitor netmon exact all all none",
            ]
        if ip(d["trap"]):
            out.append(f"snmp target-addr {d['trap']} netmon")
        return out
