from tkinter import ttk
from .base import ModuleBase

class ModBasic(ModuleBase):
    key = "basic"; title = "Basic"

    def build_ui(self):
        f = self.parent
        self.e_name    = ttk.Entry(f, width=28)
        self.e_loc     = ttk.Entry(f, width=28)
        self.e_contact = ttk.Entry(f, width=28)
        self.e_prompt  = ttk.Entry(f, width=28)
        self.e_timeout = ttk.Entry(f, width=10)
        r=0
        ttk.Label(f, text="System name").grid(row=r, column=0, sticky='w'); self.e_name.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="Location").grid(row=r, column=0, sticky='w'); self.e_loc.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="Contact").grid(row=r, column=0, sticky='w'); self.e_contact.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="Session prompt").grid(row=r, column=0, sticky='w'); self.e_prompt.grid(row=r, column=1, sticky='w'); r+=1
        ttk.Label(f, text="CLI timeout (s)").grid(row=r, column=0, sticky='w'); self.e_timeout.grid(row=r, column=1, sticky='w'); r+=1

    def collect(self):
        return {
            "name": self.e_name.get().strip(),
            "loc": self.e_loc.get().strip(),
            "contact": self.e_contact.get().strip(),
            "prompt": self.e_prompt.get().strip(),
            "timeout": self.e_timeout.get().strip(),
        }

    def build_config(self, d):
        out=[]
        if d["name"]:    out.append(f'system name "{d["name"]}"')
        if d["loc"]:     out.append(f'system location "{d["loc"]}"')
        if d["contact"]: out.append(f'system contact "{d["contact"]}"')
        if d["prompt"]:  out.append(f'session prompt default "{d["prompt"]}"')
        if d["timeout"]: out.append(f'session cli timeout {d["timeout"]}')
        return out
