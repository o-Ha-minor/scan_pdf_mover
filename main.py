# ライブラリのインポート
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
import os
import subprocess
from datetime import date, timedelta
import logging

logging.basicConfig(
    filename="pdf_copy.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8"
)

def open_copied_file(destination_path: Path):
    try:
        if os.name == "nt":
            os.startfile(destination_path)
        elif os.name == "posix":
            subprocess.run(["open", destination_path], check=False)
    except Exception as error:
        logging.error(f"コピー先ファイルを開けませんでした: {destination_path} / {error}")

def copy_pdf(source_path: Path, destination_folder: Path, days_ago: int):
    if not source_path.exists():
        return False, f"ファイルが見つかりません：{source_path}", None

    target_date = date.today() - timedelta(days=days_ago)
    date_text = target_date.strftime("%Y%m%d")

    new_name = f"{date_text}_{source_path.name}"

    destination_folder.mkdir(parents=True, exist_ok=True)

    destination_path = destination_folder / new_name

    if destination_path.exists():
        return False, f"移動先に同じ名前のファイルが既に存在します: {destination_path}"


    shutil.copy2(source_path, destination_path)
    logging.info(f"コピー成功: {source_path}から{destination_path}")
    return True, f"コピーしました： {source_path}から{destination_path}", destination_path

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("pdf移動ツール")

        self.source_path = tk.StringVar()
        self.destination_path = tk.StringVar()
        self.days_ago = tk.StringVar(value="0")

        tk.Label(root, text= "PDFファイル").pack(padx=10, pady=(10, 0))
        tk.Entry(root, textvariable=self.source_path, width=50).pack(padx=10)
        tk.Button(root, text="対象ファイルを選択", command=self.select_file).pack(pady=5)

        tk.Label(root, text="出力フォルダ").pack(padx=10, pady=(10, 0))
        tk.Entry(root, textvariable=self.destination_path, width=50).pack(padx=10)
        tk.Button(root, text="出力フォルダを選択", command=self.select_folder).pack(pady=5)

        tk.Label(root, text= "何日前の日付を付けるか").pack(padx=10, pady=(10, 0))
        tk.Spinbox(root, from_=0, to=365, textvariable=self.days_ago, width=10).pack(padx=10)


        tk.Button(root, text="コピー実行", command=self.execute).pack(pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(
        title="PDFファイルを選択",
        filetypes=[("PDFファイル", "*.pdf")]
        )
        if path:
            self.source_path.set(path)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.destination_path.set(path)

    def execute(self):
        source_text = self.source_path.get()
        destination_text = self.destination_path.get()
        days_ago_text = self.days_ago.get()

        if not source_text:
            messagebox.showerror("エラー", "ファイルを選択してください")
            return

        if not destination_text:
            messagebox.showerror("エラー", "出力フォルダを選択してください")
            return

        try:
            days_ago = int(days_ago_text)
        except ValueError:
            messagebox.showerror("エラー", "日付には整数を入力してください")
            return

        if days_ago < 0:
            messagebox.showerror("エラー","０以上の整数を入力してください")
            return

        source = Path(source_text)
        destination = Path(destination_text)

        success, message, copied_path = copy_pdf(source, destination, days_ago)

        if success:
            messagebox.showinfo("成功", message)
            
            if copied_path is not None:
                open_copied_file(copied_path)
                
            should_delete = messagebox.askyesno(
                "元ファイルの削除確認",
                "コピー先を確認したあと、元のPDFファイルを削除しますか？\n"
                f"削除対象:{source}"
            )
            
            if should_delete:
                try:
                    source.unlink()
                    logging.info(f"元ファイル削除成功:{source}")
                    messagebox.showinfo("削除完了", f"元ファイルを削除しました: {source}")
                    
                except Exception as error:
                    logging.error(f"元ファイル削除失敗: {source}")
                    messagebox.showerror("削除エラー", "元ファイルを削除できませんでした:\n{error}")
        else:
            messagebox.showerror("エラー", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
