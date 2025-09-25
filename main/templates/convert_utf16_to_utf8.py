# convert_utf16_to_utf8.py
import io
import os

src = r"fixtures/taskpresets.json"          # 元のUTF-16ファイル
dst = r"fixtures/taskpresets_utf8.json"     # UTF-8で出力するファイル

# UTF-16 で読み込んで UTF-8 で書き出す
with io.open(src, "r", encoding="utf-16") as f:
    data = f.read()

with io.open(dst, "w", encoding="utf-8") as f:
    f.write(data)

print("変換完了！書き出したファイル:", dst)
print("サイズ:", os.path.getsize(dst), "bytes")
