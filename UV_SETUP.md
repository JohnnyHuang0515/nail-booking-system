# uv 環境設置指南

本專案已遷移到使用 uv 作為 Python 套件與環境管理工具。

## 🚀 快速開始

### 1. 安裝 uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 設置專案環境
```bash
# 同步依賴
uv sync

# 啟動後端
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 環境變數設置
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入實際配置值
nano .env
```

## 📦 依賴管理

### 新增依賴
```bash
# 新增生產依賴
uv add fastapi

# 新增開發依賴
uv add --group dev pytest
```

### 移除依賴
```bash
uv remove package-name
```

### 查看依賴樹
```bash
uv tree
```

## 🐍 Python 版本管理

本專案使用 Python 3.10.0：

```bash
# 查看已安裝的 Python 版本
uv python list

# 安裝特定版本
uv python install 3.10.0

# 使用指定版本建立環境
uv venv --python 3.10.0
```

## 🔧 常用指令

```bash
# 同步依賴
uv sync

# 鎖定依賴版本
uv lock

# 在虛擬環境中執行指令
uv run python script.py
uv run pytest
uv run ruff check

# 查看虛擬環境資訊
uv run python --version
```

## 🛠️ 開發工具

### 代碼格式化與檢查
```bash
# 安裝開發工具
uv add --group dev ruff mypy

# 格式化代碼
uv run ruff format

# 檢查代碼
uv run ruff check

# 型別檢查
uv run mypy app/
```

### 測試
```bash
# 執行測試
uv run pytest

# 執行測試並生成覆蓋率報告
uv run pytest --cov=app
```

## 📁 專案結構

```
美甲預約系統/
├── pyproject.toml          # uv 專案配置
├── uv.lock                 # 依賴鎖定檔
├── .python-version         # Python 版本指定
├── .env.example            # 環境變數範本
├── .venv/                  # 虛擬環境 (不提交)
├── app/                    # 後端代碼
├── frontend/               # 前端代碼
├── platform-admin/         # 平台管理員
└── scripts/                # 啟動腳本
```

## 🚀 啟動服務

### 一鍵啟動所有服務
```bash
./scripts/start_all.sh
```

### 僅啟動後端
```bash
./scripts/start_backend.sh
```

## ⚠️ 注意事項

1. **虛擬環境**：`.venv/` 資料夾不會提交到版本控制
2. **環境變數**：`.env` 檔案不會提交到版本控制，請使用 `.env.example` 作為範本
3. **依賴鎖定**：`uv.lock` 檔案會提交到版本控制，確保環境一致性
4. **Python 版本**：使用 `.python-version` 檔案指定 Python 版本

## 🔄 從舊環境遷移

如果您之前使用 pip 和 requirements.txt：

1. 刪除舊的虛擬環境：`rm -rf venv/`
2. 執行 `uv sync` 同步新依賴
3. 使用 `uv run` 替代 `python -m` 執行指令

## 📚 更多資訊

- [uv 官方文檔](https://docs.astral.sh/uv/)
- [uv GitHub 倉庫](https://github.com/astral-sh/uv)
