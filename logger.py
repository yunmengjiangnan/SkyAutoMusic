import tkinter as tk
from tkinter import ttk

class LogWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.log_frame = ttk.Frame(self.root)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.text_widget = tk.Text(self.log_frame, state='disabled', wrap='word')
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.setup_styles()

    def setup_styles(self):
        """设置样式"""
        self.text_widget.tag_configure('log', foreground='black')
        self.text_widget.tag_configure('error', foreground='red')

    def log(self, message, level='log'):
        """记录日志"""
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, message + '\n', level)
        self.text_widget.config(state='disabled')
        self.text_widget.yview(tk.END)

    def close(self):
        """关闭日志窗口"""
        self.root.destroy()

def show_log_window():
    """显示日志窗口"""
    root = tk.Tk()
    root.title("日志")
    log_window = LogWindow(root)
    return root, log_window