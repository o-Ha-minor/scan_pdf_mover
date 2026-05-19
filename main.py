# ライブラリのインポート
import logging
import os
import shutil
import subprocess
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox


# ログ設定
logging.basicConfig(
    filename="pdf_copy.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


def open_copied_file(destination_path: Path) -> None:
    """コピー後のPDFファイルを開く。"""
    try:
        if os.name == "nt":
            os.startfile(destination_path)
        elif os.name == "posix":
            if sys_platform_is_mac():
                subprocess.run(["open", str(destination_path)], check=False)
            else:
                subprocess.run(["xdg-open", str(destination_path)], check=False)
    except Exception as error:
        logging.error(f"コピー先ファイルを開けませんでした: {destination_path} / {error}")


def sys_platform_is_mac() -> bool:
    """実行環境がMacかどうかを判定する。"""
    return subprocess.run(
        ["uname"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip() == "Darwin"


def copy_pdf(source_path: Path, destination_folder: Path, days_ago: int):
    """PDFを日付付きファイル名でコピーする。"""
    if not source_path.exists():
        return False, f"ファイルが見つかりません：{source_path}", None

    if not source_path.is_file():
        return False, f"ファイルではありません：{source_path}", None

    if source_path.suffix.lower() != ".pdf":
        return False, f"PDFファイルではありません：{source_path}", None

    target_date = date.today() - timedelta(days=days_ago)
    date_text = target_date.strftime("%Y%m%d")
    new_name = f"{date_text}_{source_path.name}"

    destination_folder.mkdir(parents=True, exist_ok=True)
    destination_path = destination_folder / new_name

    if destination_path.exists():
        return False, f"同名ファイルが既に存在します: {destination_path}", None

    shutil.copy2(source_path, destination_path)
    logging.info(f"コピー成功: {source_path} -> {destination_path}")

    return True, f"コピーしました：\n{destination_path}", destination_path


class App:
    """PDFコピー用GUIアプリ。"""

    def __init__(self, root):
        self.root = root
        self.root.title("PDFコピーツール")
        self.root.geometry("1400x500")

        self.rows = []
        self.next_row_index = 1
        self.days_ago = tk.StringVar(value="0")

        self.frame = tk.Frame(root)
        self.frame.pack(anchor="w", padx=10, pady=10)

        tk.Label(self.frame, text="PDFファイル").grid(row=0, column=0)
        tk.Label(self.frame, text="出力先").grid(row=0, column=2)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)

        tk.Button(
            bottom_frame,
            text="ファイル追加",
            command=self.add_row,
        ).pack(pady=5)

        tk.Label(
            bottom_frame,
            text="何日前の日付を付けるか",
        ).pack()

        tk.Spinbox(
            bottom_frame,
            from_=0,
            to=365,
            textvariable=self.days_ago,
            width=10,
        ).pack()

        tk.Button(
            bottom_frame,
            text="コピー実行",
            command=self.execute,
        ).pack(pady=10)

        self.add_row()

    def add_row(self) -> None:
        """入力行を追加する。"""
        source_var = tk.StringVar()
        dest_var = tk.StringVar()
        row_index = self.next_row_index
        self.next_row_index += 1

        if self.rows:
            dest_var.set(self.rows[0]["dest"].get())
            
        tk.Entry(
            self.frame,
            textvariable=source_var,
            width=60,
        ).grid(row=row_index, column=0, padx=5, pady=5)

        tk.Button(
            self.frame,
            text="選択",
            command=lambda: self.select_file(source_var),
        ).grid(row=row_index, column=1, padx=5)

        tk.Entry(
            self.frame,
            textvariable=dest_var,
            width=60,
        ).grid(row=row_index, column=2, padx=5, pady=5)

        tk.Button(
            self.frame,
            text="選択",
            command=lambda: self.select_folder(dest_var),
        ).grid(row=row_index, column=3, padx=5)

        row_data = {
            "source": source_var,
            "dest": dest_var,
            "row": row_index,
        }

        self.rows.append(row_data)

        tk.Button(
            self.frame,
            text="削除",
            command=lambda: self.remove_row(row_data),
        ).grid(row=row_index, column=4, padx=5)

    def remove_row(self, row_data) -> None:
        """指定行を削除する。"""
        remove_index = row_data["row"]

        for widget in self.frame.grid_slaves():
            if int(widget.grid_info()["row"]) == remove_index:
                widget.destroy()

        self.rows.remove(row_data)

    def select_file(self, var: tk.StringVar) -> None:
        """PDFファイルを選択する。"""
        path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDFファイル", "*.pdf")],
        )

        if path:
            var.set(path)

    def select_folder(self, var: tk.StringVar) -> None:
        """出力先フォルダを選択する。"""
        path = filedialog.askdirectory()

        if path:
            var.set(path)

    def execute(self) -> None:
        """コピー処理を実行する。"""
        try:
            days = int(self.days_ago.get())
        except ValueError:
            messagebox.showerror("エラー", "日付には整数を入力してください")
            return

        if days < 0 or days > 365:
            messagebox.showerror("エラー", "日付は0以上365以下で入力してください")
            return

        copied_files = []
        copied_sources = []

        for row in self.rows:
            source_text = row["source"].get()
            dest_text = row["dest"].get()

            if not source_text:
                continue

            if not dest_text:
                messagebox.showerror("エラー", "出力先未指定の行があります")
                return

            source = Path(source_text)
            destination = Path(dest_text)

            success, message, copied_path = copy_pdf(source, destination, days)

            if not success:
                messagebox.showerror("エラー", message)
                return

            copied_files.append(copied_path)
            copied_sources.append(source)

        if not copied_files:
            messagebox.showerror("エラー", "コピー対象がありません")
            return

        messagebox.showinfo("成功", "コピーが完了しました")

        for copied_file in copied_files:
            open_copied_file(copied_file)

        should_delete = messagebox.askyesno(
            "確認",
            "コピー先を確認したあと、元ファイルを削除しますか？",
        )

        if should_delete:
            self.delete_original_files(copied_sources)

    def delete_original_files(self, copied_sources: list[Path]) -> None:
        """コピー元ファイルを削除する。"""
        deleted_count = 0

        for source in copied_sources:
            if not source.exists():
                continue

            try:
                source.unlink()
                deleted_count += 1
                logging.info(f"元ファイル削除成功: {source}")
            except Exception as error:
                logging.error(f"元ファイル削除失敗: {source} / {error}")
                messagebox.showerror(
                    "削除エラー",
                    f"元ファイルを削除できませんでした：\n{source}\n\n{error}",
                )

        messagebox.showinfo(
            "削除完了",
            f"元ファイルを{deleted_count}件削除しました",
        )


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()