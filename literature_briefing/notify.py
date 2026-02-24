"""弹窗通知（Windows，不抢焦点）"""

import os
import logging
import tkinter as tk

log = logging.getLogger(__name__)

try:
    import ctypes
    _HAS_CTYPES = True
except ImportError:
    _HAS_CTYPES = False


def _make_popup(title_text, body_text, buttons=None, countdown_sec=0):
    result = {"clicked": None}
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.configure(bg="#1e1e2e")

    w, h = 400, 150
    sx, sy = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = sx - w - 16, sy - h - 50
    root.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(root, text=title_text, font=("Microsoft YaHei", 12, "bold"),
             bg="#1e1e2e", fg="#cdd6f4").pack(pady=(12, 4))
    msg_label = tk.Label(root, text=body_text, font=("Microsoft YaHei", 10),
                         bg="#1e1e2e", fg="#a6adc8", wraplength=370)
    msg_label.pack(pady=4)

    if buttons:
        bf = tk.Frame(root, bg="#1e1e2e")
        bf.pack(pady=10)
        for name, label in buttons:
            def _click(n=name):
                result["clicked"] = n
                root.destroy()
            tk.Button(bf, text=label, command=_click,
                      font=("Microsoft YaHei", 9), width=10,
                      relief="flat", bg="#313244", fg="#cdd6f4",
                      activebackground="#45475a",
                      activeforeground="#cdd6f4",
                      cursor="hand2").pack(side="left", padx=8)

    remaining = [countdown_sec]

    def _tick():
        if remaining[0] <= 0:
            if result["clicked"] is None:
                result["clicked"] = "timeout"
            root.destroy()
            return
        remaining[0] -= 1
        if countdown_sec > 0:
            msg_label.config(text=f"{body_text}（{remaining[0]}s）")
        root.after(1000, _tick)

    if countdown_sec > 0:
        root.after(1000, _tick)

    root.deiconify()
    root.update_idletasks()
    if _HAS_CTYPES:
        try:
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, x, y, w, h, 0x0010)
        except Exception:
            root.attributes("-topmost", True)
    else:
        root.attributes("-topmost", True)
    root.mainloop()
    return result["clicked"]


def notify_start(cfg_schedule: dict) -> bool:
    if not cfg_schedule.get("show_popup", True):
        return True
    timeout = cfg_schedule.get("popup_timeout_sec", 30)
    clicked = _make_popup(
        "文献简报", "即将开始检索最新文献，如需取消请点击「取消」",
        buttons=[("go", "开始检索"), ("cancel", "取消")],
        countdown_sec=timeout,
    )
    return clicked != "cancel"


def notify_done(total, filepath):
    fname = os.path.basename(filepath)
    _make_popup("文献简报完成", f"共检索到 {total} 篇新文献，已保存至 {fname}",
                buttons=[("ok", "知道了")], countdown_sec=10)
