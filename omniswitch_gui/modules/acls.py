from tkinter import ttk
from .base import ModuleBase

class ModACLs(ModuleBase):
    key="acls"; title="ACLs"

    def build_ui(self):
        f=self.parent
        self.blocks=[]
        self.container=ttk.Frame(f); self.container.pack(fill="both", expand=True)
        bar=ttk.Frame(f); bar.pack(fill="x", pady=4)
        ttk.Button(bar, text="+ ACL", command=self.add_block).pack(side="left")
        ttk.Button(bar, text="🗑 Laatste ACL", command=self.remove_last_acl).pack(side="left", padx=6)
        self.add_block()

    def add_block(self):
        block=ttk.LabelFrame(self.container, text="ACL")
        block.pack(fill="x", padx=6, pady=6)
        name=ttk.Entry(block, width=14)
        bind_vlan=ttk.Entry(block, width=6)
        direction=ttk.Combobox(block, values=["in","out"], width=6)
        ttk.Label(block, text="Naam").grid(row=0, column=0, sticky='w'); name.grid(row=0, column=1)
        ttk.Label(block, text="Bind VLAN").grid(row=0, column=2, sticky='w'); bind_vlan.grid(row=0, column=3)
        ttk.Label(block, text="Richting").grid(row=0, column=4, sticky='w'); direction.grid(row=0, column=5)
        rules=[]
        rc=ttk.Frame(block); rc.grid(row=1, column=0, columnspan=6, sticky='w')
        def add_rule():
            rf=ttk.Frame(rc)
            seq=ttk.Entry(rf, width=4)
            act=ttk.Combobox(rf, values=["permit","deny"], width=6)
            proto=ttk.Entry(rf, width=6)
            src=ttk.Entry(rf, width=18)
            dst=ttk.Entry(rf, width=18)
            opt=ttk.Entry(rf, width=10)
            for label,w in [("seq",seq),("act",act),("proto",proto),("src",src),("dst",dst),("opt",opt)]:
                ttk.Label(rf, text=label).pack(side="left"); w.pack(side="left", padx=4)
            ttk.Button(rf, text="🗑", width=3, command=lambda fr=rf: (fr.destroy(), rules.remove((seq,act,proto,src,dst,opt)))).pack(side="left", padx=6)
            rf.pack(anchor="w", pady=2); rules.append((seq,act,proto,src,dst,opt))
        ttk.Button(block, text="+ Regel", command=add_rule).grid(row=2, column=0, sticky='w', padx=6, pady=6)
        add_rule()
        self.blocks.append((block, name, bind_vlan, direction, rules))

    def remove_last_acl(self):
        if not self.blocks: return
        block,*_ = self.blocks.pop()
        block.destroy()

    def collect(self):
        acls=[]
        for block, name, bind_vlan, direction, rules in self.blocks:
            rlist=[]
            for seq,act,proto,src,dst,opt in rules:
                if seq.get().strip():
                    rlist.append({"seq": seq.get().strip(),
                                  "act": act.get().strip() or "permit",
                                  "proto": proto.get().strip() or "ip",
                                  "src": src.get().strip() or "any",
                                  "dst": dst.get().strip() or "any",
                                  "opt": opt.get().strip()})
            acls.append({"name": name.get().strip(),
                         "bind_vlan": bind_vlan.get().strip(),
                         "dir": direction.get().strip(),
                         "rules": rlist})
        return {"acls": acls}

    def build_config(self, d):
        out=[]
        for a in d["acls"]:
            if not a["name"]: continue
            out.append(f"ip access-list create {a['name']}")
            for r in a["rules"]:
                line=f"ip access-list {a['name']} seq {r['seq']} {r['act']} {r['proto']} {r['src']} {r['dst']} {r['opt']}".strip()
                out.append(line)
            if a["bind_vlan"] and a["dir"]:
                out.append(f"interface vlan {a['bind_vlan']}")
                out.append(f"ip access-group {a['name']} {a['dir']}")
        return out
