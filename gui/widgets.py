"""可复用 GUI 组件"""

import tkinter as tk
from tkinter import ttk


class ListEditor(ttk.Frame):
    """可编辑列表组件：支持添加、删除、上下移动"""

    def __init__(self, parent, label="", items=None):
        super().__init__(parent)
        self.items = list(items or [])

        if label:
            ttk.Label(self, text=label).pack(anchor="w")

        # 列表框 + 滚动条
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, pady=(2, 0))

        self.listbox = tk.Listbox(list_frame, height=6,
                                  selectmode="extended")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in self.items:
            self.listbox.insert("end", item)

        # 输入框 + 按钮
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", pady=(4, 0))

        self.entry = ttk.Entry(input_frame)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry.bind("<Return>", lambda e: self._add())

        ttk.Button(input_frame, text="添加", width=6,
                   command=self._add).pack(side="left", padx=2)
        ttk.Button(input_frame, text="删除", width=6,
                   command=self._remove).pack(side="left", padx=2)

    def _add(self):
        text = self.entry.get().strip()
        if text:
            self.listbox.insert("end", text)
            self.entry.delete(0, "end")

    def _remove(self):
        for idx in reversed(self.listbox.curselection()):
            self.listbox.delete(idx)

    def get_items(self) -> list:
        return list(self.listbox.get(0, "end"))

    def set_items(self, items: list):
        self.listbox.delete(0, "end")
        for item in items:
            self.listbox.insert("end", item)
