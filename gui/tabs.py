"""各标签页定义"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .widgets import ListEditor


class GeneralTab(ttk.Frame):
    """通用设置标签页"""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        row = 0

        ttk.Label(self, text="输出路径:").grid(row=row, column=0, sticky="w", pady=4)
        self.output_path = ttk.Entry(self, width=40)
        self.output_path.grid(row=row, column=1, sticky="ew", padx=4)
        ttk.Button(self, text="浏览...", command=self._browse
                   ).grid(row=row, column=2, padx=4)
        row += 1

        ttk.Label(self, text="子文件夹名:").grid(row=row, column=0, sticky="w", pady=4)
        self.output_folder = ttk.Entry(self, width=40)
        self.output_folder.grid(row=row, column=1, sticky="ew", padx=4)
        row += 1

        ttk.Label(self, text="回溯天数:").grid(row=row, column=0, sticky="w", pady=4)
        self.lookback = ttk.Spinbox(self, from_=1, to=90, width=10)
        self.lookback.grid(row=row, column=1, sticky="w", padx=4)
        row += 1

        ttk.Label(self, text="最大结果数:").grid(row=row, column=0, sticky="w", pady=4)
        self.max_results = ttk.Spinbox(self, from_=10, to=1000, width=10)
        self.max_results.grid(row=row, column=1, sticky="w", padx=4)

        self.columnconfigure(1, weight=1)

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, path)

    def load(self, cfg):
        self.output_path.delete(0, "end")
        self.output_path.insert(0, cfg.get("output_path", ""))
        self.output_folder.delete(0, "end")
        self.output_folder.insert(0, cfg.get("output_folder", "文献简报"))
        self.lookback.delete(0, "end")
        self.lookback.insert(0, str(cfg.get("default_lookback_days", 7)))
        self.max_results.delete(0, "end")
        self.max_results.insert(0, str(cfg.get("max_results", 200)))

    def save(self, cfg):
        cfg["output_path"] = self.output_path.get().strip()
        cfg["output_folder"] = self.output_folder.get().strip() or "文献简报"
        cfg["default_lookback_days"] = int(self.lookback.get() or 7)
        cfg["max_results"] = int(self.max_results.get() or 200)


class SourcesTab(ttk.Frame):
    """文献源设置标签页"""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # PubMed 子标签
        pm_frame = ttk.Frame(notebook, padding=8)
        notebook.add(pm_frame, text="PubMed")

        self.pm_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(pm_frame, text="启用 PubMed",
                        variable=self.pm_enabled).pack(anchor="w")

        ttk.Label(pm_frame, text="PubMed API Key:").pack(anchor="w", pady=(8, 0))
        self.pm_api_key = ttk.Entry(pm_frame, width=50, show="*")
        self.pm_api_key.pack(fill="x")

        self.pm_core = ListEditor(pm_frame, "核心期刊:")
        self.pm_core.pack(fill="both", expand=True, pady=4)

        self.pm_extended = ListEditor(pm_frame, "扩展期刊:")
        self.pm_extended.pack(fill="both", expand=True, pady=4)

        self.pm_keywords = ListEditor(pm_frame, "关键词:")
        self.pm_keywords.pack(fill="both", expand=True, pady=4)

        self.pm_species = ListEditor(pm_frame, "物种过滤:")
        self.pm_species.pack(fill="both", expand=True, pady=4)

        # arXiv 子标签
        ax_frame = ttk.Frame(notebook, padding=8)
        notebook.add(ax_frame, text="arXiv")

        self.ax_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(ax_frame, text="启用 arXiv",
                        variable=self.ax_enabled).pack(anchor="w")

        self.ax_categories = ListEditor(ax_frame, "分类 (如 cs.AI, q-bio.NC):")
        self.ax_categories.pack(fill="both", expand=True, pady=4)

        self.ax_keywords = ListEditor(ax_frame, "关键词:")
        self.ax_keywords.pack(fill="both", expand=True, pady=4)

    def load(self, cfg):
        pm = cfg.get("sources", {}).get("pubmed", {})
        self.pm_enabled.set(pm.get("enabled", True))
        self.pm_api_key.delete(0, "end")
        self.pm_api_key.insert(0, pm.get("api_key", ""))
        self.pm_core.set_items(pm.get("core_journals", []))
        self.pm_extended.set_items(pm.get("extended_journals", []))
        self.pm_keywords.set_items(pm.get("keywords", []))
        self.pm_species.set_items(pm.get("species_filter", []))

        ax = cfg.get("sources", {}).get("arxiv", {})
        self.ax_enabled.set(ax.get("enabled", False))
        self.ax_categories.set_items(ax.get("categories", []))
        self.ax_keywords.set_items(ax.get("keywords", []))

    def save(self, cfg):
        cfg["sources"]["pubmed"]["enabled"] = self.pm_enabled.get()
        cfg["sources"]["pubmed"]["api_key"] = self.pm_api_key.get().strip()
        cfg["sources"]["pubmed"]["core_journals"] = self.pm_core.get_items()
        cfg["sources"]["pubmed"]["extended_journals"] = self.pm_extended.get_items()
        cfg["sources"]["pubmed"]["keywords"] = self.pm_keywords.get_items()
        cfg["sources"]["pubmed"]["species_filter"] = self.pm_species.get_items()

        cfg["sources"]["arxiv"]["enabled"] = self.ax_enabled.get()
        cfg["sources"]["arxiv"]["categories"] = self.ax_categories.get_items()
        cfg["sources"]["arxiv"]["keywords"] = self.ax_keywords.get_items()


class AITab(ttk.Frame):
    """AI 设置标签页"""

    PROVIDERS = ["openrouter", "openai", "gemini", "claude"]

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        row = 0

        ttk.Label(self, text="提供商:").grid(row=row, column=0, sticky="w", pady=4)
        self.provider = ttk.Combobox(self, values=self.PROVIDERS,
                                     state="readonly", width=20)
        self.provider.grid(row=row, column=1, sticky="w", padx=4)
        row += 1

        ttk.Label(self, text="API Key:").grid(row=row, column=0, sticky="w", pady=4)
        self.api_key = ttk.Entry(self, width=50, show="*")
        self.api_key.grid(row=row, column=1, columnspan=2, sticky="ew", padx=4)
        row += 1

        ttk.Label(self, text="模型:").grid(row=row, column=0, sticky="w", pady=4)
        self.model = ttk.Entry(self, width=40)
        self.model.grid(row=row, column=1, sticky="ew", padx=4)
        row += 1

        ttk.Label(self, text="温度:").grid(row=row, column=0, sticky="w", pady=4)
        self.temperature = ttk.Scale(self, from_=0.0, to=1.0, orient="horizontal")
        self.temperature.grid(row=row, column=1, sticky="ew", padx=4)
        self.temp_label = ttk.Label(self, text="0.1")
        self.temp_label.grid(row=row, column=2, padx=4)
        self.temperature.configure(command=self._update_temp_label)
        row += 1

        self.enable_translation = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="启用翻译",
                        variable=self.enable_translation
                        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        row += 1

        self.enable_highlights = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="启用亮点生成",
                        variable=self.enable_highlights
                        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        row += 1

        ttk.Button(self, text="测试连接", command=self._test_connection
                   ).grid(row=row, column=0, columnspan=2, sticky="w", pady=8)

        self.columnconfigure(1, weight=1)

    def _update_temp_label(self, val):
        self.temp_label.config(text=f"{float(val):.2f}")

    def _test_connection(self):
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from literature_briefing.llm import get_provider
            cfg_llm = {
                "provider": self.provider.get(),
                "api_key": self.api_key.get().strip(),
                "model": self.model.get().strip(),
                "temperature": self.temperature.get(),
            }
            llm = get_provider(cfg_llm)
            result = llm.call("Say 'OK' in one word.", max_tokens=10)
            messagebox.showinfo("测试成功", f"连接正常！回复: {result}")
        except Exception as e:
            messagebox.showerror("测试失败", str(e))

    def load(self, cfg):
        llm = cfg.get("llm", {})
        self.provider.set(llm.get("provider", "openrouter"))
        self.api_key.delete(0, "end")
        self.api_key.insert(0, llm.get("api_key", ""))
        self.model.delete(0, "end")
        self.model.insert(0, llm.get("model", ""))
        self.temperature.set(llm.get("temperature", 0.1))
        self._update_temp_label(llm.get("temperature", 0.1))
        self.enable_translation.set(llm.get("enable_translation", True))
        self.enable_highlights.set(llm.get("enable_highlights", True))

    def save(self, cfg):
        cfg["llm"]["provider"] = self.provider.get()
        cfg["llm"]["api_key"] = self.api_key.get().strip()
        cfg["llm"]["model"] = self.model.get().strip()
        cfg["llm"]["temperature"] = round(self.temperature.get(), 2)
        cfg["llm"]["enable_translation"] = self.enable_translation.get()
        cfg["llm"]["enable_highlights"] = self.enable_highlights.get()


class ScheduleTab(ttk.Frame):
    """定时任务标签页"""

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        row = 0

        ttk.Label(self, text="登录后延迟（分钟）:").grid(row=row, column=0, sticky="w", pady=4)
        self.delay = ttk.Spinbox(self, from_=0, to=120, width=10)
        self.delay.grid(row=row, column=1, sticky="w", padx=4)
        row += 1

        self.show_popup = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="启动时显示确认弹窗",
                        variable=self.show_popup
                        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        row += 1

        ttk.Label(self, text="弹窗超时（秒）:").grid(row=row, column=0, sticky="w", pady=4)
        self.timeout = ttk.Spinbox(self, from_=5, to=120, width=10)
        self.timeout.grid(row=row, column=1, sticky="w", padx=4)
        row += 1

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=12)
        ttk.Button(btn_frame, text="安装定时任务",
                   command=self._install).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="卸载定时任务",
                   command=self._uninstall).pack(side="left")

        self.columnconfigure(1, weight=1)

    def _install(self):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bat = os.path.join(script_dir, "run_briefing.bat")
        delay = int(self.delay.get() or 20)
        delay_str = f"{delay // 60:04d}:{delay % 60:02d}"
        cmd = f'schtasks /create /tn "LiteratureBriefing" /tr "\\"{bat}\\"" /sc onlogon /delay {delay_str} /f /rl limited'
        ret = os.system(cmd)
        if ret == 0:
            messagebox.showinfo("成功", "定时任务已安装")
        else:
            messagebox.showerror("失败", "安装失败，请尝试以管理员身份运行")

    def _uninstall(self):
        ret = os.system('schtasks /delete /tn "LiteratureBriefing" /f')
        if ret == 0:
            messagebox.showinfo("成功", "定时任务已卸载")
        else:
            messagebox.showerror("失败", "卸载失败")

    def load(self, cfg):
        sch = cfg.get("schedule", {})
        self.delay.delete(0, "end")
        self.delay.insert(0, str(sch.get("delay_minutes", 20)))
        self.show_popup.set(sch.get("show_popup", True))
        self.timeout.delete(0, "end")
        self.timeout.insert(0, str(sch.get("popup_timeout_sec", 30)))

    def save(self, cfg):
        cfg["schedule"]["delay_minutes"] = int(self.delay.get() or 20)
        cfg["schedule"]["show_popup"] = self.show_popup.get()
        cfg["schedule"]["popup_timeout_sec"] = int(self.timeout.get() or 30)


class AboutTab(ttk.Frame):
    """关于标签页"""

    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(self, text="文献简报生成器",
                  font=("Microsoft YaHei", 14, "bold")).pack(pady=(0, 8))
        ttk.Label(self, text="v2.0.0").pack()
        ttk.Label(self, text="自动从 PubMed / arXiv 获取最新文献并生成简报").pack(pady=8)

        link = ttk.Label(self, text="GitHub: literature_briefing",
                         foreground="blue", cursor="hand2")
        link.pack(pady=4)

        ttk.Label(self, text="License: MIT").pack(pady=8)
