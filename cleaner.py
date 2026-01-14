import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import re

class TextCleaningTool:
    def __init__(self, root):
        self.root = root
        self.root.title("文本清洗专家 v6.0 (含字数统计)")
        self.root.geometry("950x900")
        
        self.bracket_data = [] 

        # --- 1. 顶部工具栏 ---
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill=tk.X, padx=20)

        tk.Button(top_frame, text="📋 粘贴文本", command=self.paste_from_clipboard,
                  bg="#FF9800", fg="white", font=("Arial", 10), width=12).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="🗑️ 清空重置", command=self.reset_all,
                  bg="#F44336", fg="white", font=("Arial", 10), width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Label(top_frame, text="(重置后可粘贴新文本)", fg="gray").pack(side=tk.LEFT, padx=5)

        # --- 2. 文本输入区 ---
        self.input_text_area = scrolledtext.ScrolledText(root, height=12, width=100, font=("SimHei", 10))
        self.input_text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # --- 3. 功能按钮区 ---
        btn_frame = tk.Frame(root, pady=10, bg="#f0f0f0", bd=1, relief=tk.RAISED)
        btn_frame.pack(fill=tk.X, padx=10)

        # 按钮A: 去除星号
        tk.Button(btn_frame, text="① 去除星号 (*)", command=self.remove_stars,
                  bg="#009688", fg="white", font=("Arial", 11, "bold"), padx=15).pack(side=tk.LEFT, padx=20, pady=10)

        # 按钮B: 分析括号
        self.btn_analyze = tk.Button(btn_frame, text="② 分析括号 (生成列表)", command=self.analyze_brackets,
                                     bg="#2196F3", fg="white", font=("Arial", 11, "bold"), padx=15)
        self.btn_analyze.pack(side=tk.LEFT, padx=20, pady=10)

        # 按钮C: 保存结果
        tk.Button(btn_frame, text="③ 保存最终结果 (txt)", command=self.save_result,
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=15).pack(side=tk.RIGHT, padx=20, pady=10)

        # --- 4. 交互式列表区域 ---
        lbl_list = tk.Label(root, text="▼ 括号内容待删除列表 (勾选「恢复」可保留该内容，否则默认删除):", 
                            font=("Arial", 10, "bold"), fg="#D32F2F", anchor="w")
        lbl_list.pack(fill=tk.X, padx=15, pady=(10, 0))

        self.list_area = scrolledtext.ScrolledText(root, height=20, width=100, font=("Consolas", 10), bg="#FFFAFA")
        self.list_area.pack(padx=10, pady=(5, 20), fill=tk.BOTH, expand=True)
        
        self.list_area.tag_config("deleted_content", background="#FFEBEE", foreground="#B71C1C", font=("SimHei", 10, "bold"))
        self.list_area.tag_config("context", foreground="#666666", font=("SimHei", 9))
        self.list_area.tag_config("sep", foreground="#EEEEEE")

    # --- 功能函数 ---

    def paste_from_clipboard(self):
        try:
            content = self.root.clipboard_get()
            self.input_text_area.insert(tk.INSERT, content)
        except:
            pass

    def reset_all(self):
        self.input_text_area.config(state='normal')
        self.input_text_area.delete("1.0", tk.END)
        self.list_area.config(state='normal')
        self.list_area.delete("1.0", tk.END)
        self.list_area.config(state='disabled')
        self.bracket_data = []
        self.btn_analyze.config(state='normal')

    def remove_stars(self):
        if self.bracket_data:
            messagebox.showwarning("操作顺序提示", "您已经分析了括号，请先【清空重置】后再重新操作，\n否则会导致位置索引错乱。")
            return

        current_text = self.input_text_area.get("1.0", tk.END)
        if "*" not in current_text:
            messagebox.showinfo("提示", "文本中没有发现星号 (*)。")
            return
            
        new_text = current_text.replace("*", "")
        self.input_text_area.delete("1.0", tk.END)
        self.input_text_area.insert(tk.END, new_text)
        messagebox.showinfo("完成", "所有的星号 (*) 已被移除。")

    def analyze_brackets(self):
        raw_text = self.input_text_area.get("1.0", "end-1c")
        if not raw_text.strip():
            messagebox.showwarning("提示", "文本框是空的！")
            return

        self.input_text_area.config(state='disabled')
        self.btn_analyze.config(state='disabled')
        
        self.list_area.config(state='normal')
        self.list_area.delete("1.0", tk.END)
        self.bracket_data = []

        pattern = re.compile(r'(\(.*?\)|\（.*?\）)', re.DOTALL)
        
        count = 0
        for match in pattern.finditer(raw_text):
            count += 1
            start = match.start()
            end = match.end()
            content = match.group(0)

            ctx_start = max(0, start - 15)
            ctx_end = min(len(raw_text), end + 15)
            prefix = raw_text[ctx_start:start].replace('\n', ' ')
            suffix = raw_text[end:ctx_end].replace('\n', ' ')

            is_restore_var = tk.BooleanVar(value=False)
            
            self.bracket_data.append({
                "start": start,
                "end": end,
                "content": content,
                "var": is_restore_var
            })

            cb = tk.Checkbutton(self.list_area, text="恢复此项", variable=is_restore_var, 
                                bg="#E8F5E9", fg="#2E7D32", font=("Arial", 9, "bold"), cursor="hand2")
            self.list_area.window_create(tk.END, window=cb)
            
            self.list_area.insert(tk.END, f"  内容: {content}\n", "deleted_content")
            self.list_area.insert(tk.END, f"       位置: ...{prefix} [此处] {suffix}...\n", "context")
            self.list_area.insert(tk.END, "-"*80 + "\n", "sep")

        if count == 0:
            self.list_area.insert(tk.END, "未发现任何括号内容。\n")
        
        self.list_area.config(state='disabled')

    def get_safe_filename(self, text_content):
        lines = text_content.splitlines()
        first_line = "processed_text"
        for line in lines:
            if line.strip():
                first_line = line.strip()
                break
        safe_name = re.sub(r'[\\/:*?"<>|]', '', first_line)
        return safe_name[:30] if safe_name else "processed_text"

    def save_result(self):
        # 核心修改：计算逻辑
        if not self.bracket_data:
             final_text = self.input_text_area.get("1.0", "end-1c") # 精确获取不带最后换行符
        else:
            raw_text = self.input_text_area.get("1.0", "end-1c")
            final_text = ""
            current_idx = 0
            for item in self.bracket_data:
                final_text += raw_text[current_idx : item['start']]
                if item['var'].get() == True:
                    final_text += item['content']
                current_idx = item['end']
            final_text += raw_text[current_idx:]

        # --- 新增：计算字数 ---
        char_count = len(final_text)
        no_space_count = len(final_text.replace(" ", "").replace("\n", "").replace("\r", ""))

        default_name = self.get_safe_filename(final_text)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="保存处理结果"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_text)
                
                restored_count = sum(1 for item in self.bracket_data if item['var'].get())
                deleted_count = len(self.bracket_data) - restored_count
                
                # --- 修改：在弹窗中显示字数 ---
                msg = (f"✅ 文件已保存！\n\n"
                       f"📊 字数统计：\n"
                       f"   - 总字符数: {char_count}\n"
                       f"   - 纯字符数(去空): {no_space_count}\n\n"
                       f"📋 操作详情：\n"
                       f"   - 确认删除括号: {deleted_count} 处\n"
                       f"   - 恢复保留括号: {restored_count} 处")
                
                messagebox.showinfo("处理完成", msg)
                
                if messagebox.askyesno("下一步", "保存成功。是否清空并准备处理下一段？"):
                    self.reset_all()
                    
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextCleaningTool(root)
    root.mainloop()