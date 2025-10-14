.PHONY: help install dev test migrate format lint clean

help:
	@echo "LINE 美甲預約系統 - 後端開發指令"
	@echo ""
	@echo "可用指令："
	@echo "  make install    - 安裝依賴"
	@echo "  make dev        - 啟動開發服務器"
	@echo "  make test       - 執行所有測試"
	@echo "  make test-unit  - 執行單元測試"
	@echo "  make test-bdd   - 執行 BDD 測試"
	@echo "  make migrate    - 執行資料庫遷移"
	@echo "  make format     - 格式化代碼"
	@echo "  make lint       - 檢查代碼品質"
	@echo "  make clean      - 清理暫存檔案"

install:
	pip install -r requirements.txt

dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src --cov-report=html
	behave tests/features/

test-unit:
	pytest tests/unit/ -v --cov=src

test-bdd:
	behave tests/features/ --no-capture

test-integration:
	pytest tests/integration/ -v

migrate:
	alembic upgrade head

migrate-rollback:
	alembic downgrade -1

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

format:
	black src/ tests/
	ruff check src/ --fix

lint:
	ruff check src/
	mypy src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage

