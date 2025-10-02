import tkinter as tk
from tkinter import ttk, messagebox

# import de modules die we nu beschikbaar maken
from modules import (
    ModBasic, ModTime, ModMgmt, ModVlans, ModSTP, ModLACP, ModLLDP,
    ModLoopback, ModQoS, ModACLs, ModAAA, ModRouting, ModDHCP,
    ModSNMP, ModBackup, ModPlanner
)

MODULES = [
    ("basic",   ModBasic),
    ("time",    ModTime),
    ("mgmt",    ModMgmt),
    ("vlans",   ModVlans),
    ("stp",     ModSTP),
    ("lacp",    ModLACP),
    ("lldp",    ModLLDP),
    ("loop",    ModLoopback),
    ("qos",     ModQoS),
    ("acls",    ModACLs),
    ("aaa",     ModAAA),
    ("routing", ModRouting),
    ("dhcp",    ModDHCP),
    ("snmp",    ModSNMP),
    ("backup",  ModBackup),
    ("planner", ModPlanner),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OmniSwitch Configurator (Modulair)")
        self.geometry("1200x800")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}      # key -> frame
        self.modules = {}   # key -> module instance

        self._build_modules_tab()
        self._build_output_tab()

    def _build_modules_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="☰ Modules")

        ttk.Label(f, text="Vink aan wat je wil configureren. De tabbladen verschijnen/verdwijnen dynamisch.").pack(anchor='w', padx=10, pady=8)
        grid = ttk.LabelFrame(f, text="Beschikbare modules"); grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.vars = {}
        defaults_on = set()  # standaard UIT
        r=c=0
        for key, cls in MODULES:
            var = tk.BooleanVar(value=(key in defaults_on))
            self.vars[key] = var
            def on_toggle(k=key, klass=cls, v=var):
                if v.get():
                    self._add_module_tab(k, klass)
                else:
                    self._remove_module_tab(k)
            ttk.Checkbutton(grid, text=cls.title, variable=var, command=on_toggle).grid(row=r, column=c, sticky='w', padx=10, pady=6)
            c+=1
            if c==2: c=0; r+=1

    def _add_module_tab(self, key, Klass):
        if key in self.tabs: return
        frame = ttk.Frame(self.notebook)
        # Voeg tab toe vóór "Uitvoer"
        self.notebook.insert(len(self.notebook.tabs())-1, frame, text=Klass.title)
        mod = Klass(frame); mod.build_ui()
        self.tabs[key] = frame
        self.modules[key] = mod

    def _remove_module_tab(self, key):
        if key not in self.tabs: return
        frame = self.tabs.pop(key)
        self.modules.pop(key, None)
        try:
            idx = self.notebook.tabs().index(str(frame))
            self.notebook.forget(idx)
        except Exception:
            pass

    def _build_output_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="Uitvoer")
        self.tOut = tk.Text(f)
        self.tOut.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        bar = ttk.Frame(f); bar.pack(fill=tk.X)
        ttk.Button(bar, text="Validate", command=self.do_validate).pack(side=tk.LEFT, padx=6, pady=6)
        ttk.Button(bar, text="Genereer Config", command=self.do_generate).pack(side=tk.LEFT, padx=6, pady=6)
        ttk.Button(bar, text="Kopieer", command=self.copy_clip).pack(side=tk.LEFT, padx=6, pady=6)

    def do_validate(self):
        errs=[]; warns=[]
        for key, mod in self.modules.items():
            e,w = mod.validate()
            errs += [f"[{mod.title}] {x}" for x in e]
            warns+= [f"[{mod.title}] {x}" for x in w]
        if not errs and not warns:
            messagebox.showinfo("Validate", "Alles ziet er goed uit ✅")
        else:
            msg=""
            if errs:  msg += "Fouten:\n- " + "\n- ".join(errs)
            if warns: msg += ("\n\n" if msg else "") + "Waarschuwingen:\n- " + "\n- ".join(warns)
            messagebox.showwarning("Validate resultaat", msg)

    def do_generate(self):
        # optioneel: eerst validatie laten zien
        self.do_validate()
        lines=[]
        for key, mod in self.modules.items():
            d = mod.collect()
            lines += mod.build_config(d)
        lines.append("write memory")
        self.tOut.delete("1.0", "end")
        self.tOut.insert("end", "\n".join(lines) + "\n")
        messagebox.showinfo("Klaar", "Configuratie gegenereerd.")

    def copy_clip(self):
        data = self.tOut.get("1.0", "end")
        self.clipboard_clear(); self.clipboard_append(data)
        messagebox.showinfo("Gekopieerd", "Config staat op het klembord.")

if __name__ == "__main__":
    App().mainloop()
