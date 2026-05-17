# ライブラリのインポート
from pathlib import Path
import shutil
from datetime import date, timedelta
import logging

scan_folder = Path("ScanShare")
source_name = "test.pdf"
destination_folder = Path("output")
new_name = "test.pdf"
days_ago = 0

target_date = date.today() - timedelta(days=days_ago)
date_text = target_date.strftime("%Y%m%d")
dated_name = f"{date_text}_{new_name}"

source_path = scan_folder / source_name
destination_path = destination_folder / dated_name

destination_folder.mkdir(exist_ok=True)

if source_path.exists():
    shutil.move (source_path, destination_path)
    print(f"移動しました: {source_path} から {destination_path}")
else:
    print(f"ファイルが見つかりません: {source_path}")