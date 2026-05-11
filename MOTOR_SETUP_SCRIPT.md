# Motor Setup Selective Script

新しい `lerobot-setup-motors-selective` スクリプトを追加しました。既設定済みのモーターをスキップしたり、特定のモーターのみ設定できます。

## 概要

### ファイル構成

```
src/lerobot/scripts/
  └── lerobot_setup_motors_selective.py    # メインスクリプト（新規）
pyproject.toml                              # 修正: lerobot-setup-motors-selective エントリ追加
docs/source/
  └── setup_motors_selective.md            # ドキュメント（新規）
tests/scripts/
  └── test_setup_motors_selective.py       # テスト（新規）
```

## 機能

### 1. **対話的スキップモード** (デフォルト)

各モーターごとに対話的にプロンプトが出ます：

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0
```

各モーターで選択:
- `y` / Enter → 設定する
- `s` → スキップ
- `q` → 終了

### 2. **選別モード** (特定モーターのみ設定)

特定のモーターだけを指定:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=shoulder,elbow,gripper
```

この場合、shoulder, elbow, gripper の3つだけ設定され、対話なしで処理されます。

### 3. **スキャンのみモード** (設定なし)

現在ポートに接続されているモーターを検索するだけ:

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --scan-only
```

既設定のモーターの状態を確認できます。

## 実装の詳細

### メイン関数: `setup_motors_selective()`

```python
def setup_motors_selective(
    device,
    motors_to_setup: list[str] | None = None,
    scan_only: bool = False,
) -> None
```

- `device`: Robot / Teleoperator インスタンス
- `motors_to_setup`: 設定するモーター名リスト（Noneなら対話モード）
- `scan_only`: Trueならスキャンのみで設定しない

### フロー

```
SetupConfig (draccus でパース)
    ↓
setup_motors() (修飾子で CLI 引数を処理)
    ↓
make_robot_from_config() または make_teleoperator_from_config()
    ↓
setup_motors_selective(device, motors_to_setup, scan_only)
    ├─ scan_only=True の場合:
    │   └─ broadcast_ping() で各ボーレートを走査して報告
    │
    └─ scan_only=False の場合:
        ├─ motors_to_setup が指定されている:
        │   └─ 指定モーターだけ bus.setup_motor() で設定
        │
        └─ motors_to_setup が None:
            └─ 各モーターに対して対話的に設定/スキップ判定

                対話プロンプト: (y)es / (s)kip / (q)uit?
                ├─ y → bus.setup_motor(motor)
                ├─ s → スキップして次へ
                └─ q → 中止して終了
```

### SetupConfig の構造

```python
@dataclass
class SetupConfig:
    robot: RobotConfig | None = None
    teleop: TeleoperatorConfig | None = None
    motors: list[str] = field(default_factory=list)  # モーター名リスト
    scan_only: bool = False                           # スキャンのみ

    def __post_init__(self):
        if bool(self.teleop) == bool(self.robot):
            raise ValueError("Choose either a teleop or a robot.")
        self.device = self.robot if self.robot else self.teleop
```

draccus の `@wrap()` により、CLI引数から自動変換されます。

## 使用例

### 例1: 既設定モーターをスキップして新しいモーターだけ設定

```bash
# 対話的に「新しい gripper だけ設定」
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0

# 各モーターで:
# shoulder → (s)kip
# elbow → (s)kip
# wrist → (s)kip
# gripper → (y)es
```

### 例2: gripper だけ再設定

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=gripper
```

### 例3: 複数モーターを一気に設定

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=shoulder,elbow,wrist,gripper
```

### 例4: 現在のモーター状態確認

```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --scan-only

# 出力例:
# Scanning baudrates: [57600, 115200, ...]
#   Baudrate 57600: Found IDs [1, 2, 3, 10]
#   Baudrate 115200: Found IDs [4, 5]
```

## テスト

```bash
# SetupConfig の検証テスト
pytest -sv tests/scripts/test_setup_motors_selective.py

# より詳細なテスト（実際のハードウェアが必要）
# lerobot-setup-motors-selective --robot.type=so100_follower --robot.port=/dev/ttyUSB0 --scan-only
```

## インストール

既に `pyproject.toml` に登録済みなので、インストール後に以下で使用可能:

```bash
# 開発インストール
pip install -e .

# または uv を使用
uv sync

# 確認
lerobot-setup-motors-selective --help
```

## 既存スクリプトとの違い

| 機能 | `lerobot-setup-motors` | `lerobot-setup-motors-selective` |
|------|------------------------|----------------------------------|
| 対話的プロンプト | ✓ (全モーター) | ✓ (スキップ可能) |
| モーター指定 | ✗ | ✓ (`--motors=...`) |
| スキップ機能 | ✗ | ✓ (対話モードで `s` キー) |
| スキャンのみ | ✗ | ✓ (`--scan-only`) |
| エラーリトライ | ✗ | ✓ (対話的に提示) |

## トラブルシューティング

### `motors` 引数が認識されない

モーター名はカンマ区切りで、スペースを入れない:
```bash
--motors=shoulder,elbow  # OK
--motors=shoulder, elbow # NG (スペース含む)
```

### `--motors` 指定時に存在しないモーター名を指定

```bash
$ lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=nonexistent

ValueError: Motor 'nonexistent' not found. Available motors: ['shoulder', 'elbow', 'wrist', 'gripper']
```

`--scan-only` で使用可能なモーター名を確認:
```bash
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --scan-only
```

### デバイス指定エラー

```bash
$ lerobot-setup-motors-selective --robot.type=unknown_robot --robot.port=/dev/ttyUSB0

ValueError: Choose either a teleop or a robot.
```

`--robot` または `--teleop` のいずれか一方を指定してください。

## 将来の改善案

1. **モーター名マッピング**: IDベースの指定も可能にする (`--motors=1,2,3`)
2. **リカバリー**: セットアップ失敗時に現在状態をログ出力
3. **バッチ設定**: 複数ポート/デバイスを一括処理
