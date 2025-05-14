## そのまま使いたい人
- Windows
  - `installer`の中のexeを使ってください
    - [RS01.exe](installer/RS01.exe)
- Mac
  - そのうちビルドする予定です
  - 現状は、下記手順で自分でビルドしてください。

## 自分でビルドする人

### 環境構築
- venv起動
  - 例 (Windows)
    - `python3 -m venv .venv`
    - `./.venv/Scripts/activate`
- モジュールのインストール
  - 例 (Windows)
    - `pip installer -r requirements.txt`

### インストーラーの作成
- Windows
  - `pyinstaller --onefile --noconsole --icon=.\assets\leaf.ico --add-data "assets\leaf.ico;assets" .\RemoteSpecial01.py`

- Mac
  - `pyinstaller --onefile --noconsole --icon=./assets/leaf.ico --add-data "assets/leaf.ico:assets" ./RemoteSpecial01.py`