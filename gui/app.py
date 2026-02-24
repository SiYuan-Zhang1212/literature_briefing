"""设置界面主窗口"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox

# 确保能导入 literature_briefing 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_briefing.config import load_config, save_config
from gui.tabs import GeneralTab, SourcesTab, AITab, ScheduleTab, AboutTab


class SettingsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文献简报 - 设置")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)

        self.cfg = load_config()

        # 标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        self.general = GeneralTab(notebook)
        self.sources = SourcesTab(notebook)
        self.ai = AITab(notebook)
        self.schedule = ScheduleTab(notebook)
        self.about = AboutTab(notebook)

        notebook.add(self.general, text="通用")
        notebook.add(self.sources, text="文献源")
        notebook.add(self.ai, text="AI 设置")
        notebook.add(self.schedule, text="定时任务")
        notebook.add(self.about, text="关于")

        # 底部按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=8, pady=8)

        ttk.Button(btn_frame, text="保存", command=self._save).pack(side="right", padx=4)
        ttk.Button(btn_frame, text="取消", command=self.root.destroy).pack(side="right", padx=4)

        self._load_all()

    def _load_all(self):
        self.general.load(self.cfg)
        self.sources.load(self.cfg)
        self.ai.load(self.cfg)
        self.schedule.load(self.cfg)

    def _save(self):
        try:
            self.general.save(self.cfg)
            self.sources.save(self.cfg)
            self.ai.save(self.cfg)
            self.schedule.save(self.cfg)
            save_config(self.cfg)
            messagebox.showinfo("保存成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def run(self):
        self.root.mainloop()


def main():
    app = SettingsApp()
    app.run()


if __name__ == "__main__":
    main()
