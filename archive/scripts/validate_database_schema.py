#!/usr/bin/env python3
"""
資料庫架構驗證腳本
驗證多商家美甲預約系統的資料庫設計是否符合 ERD 規範
"""
import sys
from pathlib import Path
from sqlalchemy import text, inspect
from sqlalchemy.orm import sessionmaker

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.infrastructure.database.session import engine
from app.infrastructure.database.models import Base


class DatabaseSchemaValidator:
    """資料庫架構驗證器"""
    
    def __init__(self):
        self.engine = engine
        self.inspector = inspect(engine)
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """驗證所有架構"""
        print("=" * 60)
        print("多商家美甲預約系統 - 資料庫架構驗證")
        print("=" * 60)
        
        # 1. 驗證表結構
        self._validate_tables()
        
        # 2. 驗證欄位
        self._validate_columns()
        
        # 3. 驗證約束
        self._validate_constraints()
        
        # 4. 驗證索引
        self._validate_indexes()
        
        # 5. 驗證外鍵
        self._validate_foreign_keys()
        
        # 6. 驗證 RLS
        self._validate_rls()
        
        # 7. 驗證資料隔離
        self._validate_data_isolation()
        
        # 輸出結果
        self._print_results()
        
        return len(self.errors) == 0
    
    def _validate_tables(self):
        """驗證表結構"""
        print("\n1. 驗證表結構...")
        
        expected_tables = {
            'merchants', 'users', 'services', 'appointments', 
            'transactions', 'business_hours', 'time_off'
        }
        
        actual_tables = set(self.inspector.get_table_names())
        
        # 檢查必需的表
        for table in expected_tables:
            if table not in actual_tables:
                self.errors.append(f"缺少必需的表: {table}")
            else:
                print(f"  ✓ 表 {table} 存在")
        
        # 檢查是否有額外的表
        extra_tables = actual_tables - expected_tables
        if extra_tables:
            self.warnings.append(f"發現額外的表: {extra_tables}")
    
    def _validate_columns(self):
        """驗證欄位結構"""
        print("\n2. 驗證欄位結構...")
        
        expected_columns = {
            'merchants': {
                'id', 'name', 'line_channel_id', 'line_channel_secret',
                'line_channel_access_token', 'timezone', 'is_active', 'created_at'
            },
            'users': {
                'id', 'merchant_id', 'line_user_id', 'name', 'phone', 'created_at'
            },
            'services': {
                'id', 'merchant_id', 'branch_id', 'name', 'price', 
                'duration_minutes', 'is_active'
            },
            'appointments': {
                'id', 'merchant_id', 'branch_id', 'user_id', 'service_id',
                'appointment_date', 'appointment_time', 'staff_id', 'status', 'created_at'
            },
            'transactions': {
                'id', 'merchant_id', 'user_id', 'appointment_id', 
                'amount', 'notes', 'created_at'
            },
            'business_hours': {
                'id', 'merchant_id', 'branch_id', 'day_of_week', 
                'start_time', 'end_time'
            },
            'time_off': {
                'id', 'merchant_id', 'branch_id', 'staff_id',
                'start_datetime', 'end_datetime', 'reason'
            }
        }
        
        for table_name, expected_cols in expected_columns.items():
            if table_name not in self.inspector.get_table_names():
                continue
                
            actual_cols = set(col['name'] for col in self.inspector.get_columns(table_name))
            
            # 檢查必需的欄位
            missing_cols = expected_cols - actual_cols
            if missing_cols:
                self.errors.append(f"表 {table_name} 缺少欄位: {missing_cols}")
            else:
                print(f"  ✓ 表 {table_name} 欄位完整")
            
            # 檢查是否有額外的欄位
            extra_cols = actual_cols - expected_cols
            if extra_cols:
                self.warnings.append(f"表 {table_name} 有額外欄位: {extra_cols}")
    
    def _validate_constraints(self):
        """驗證約束"""
        print("\n3. 驗證約束...")
        
        with self.engine.connect() as conn:
            # 檢查唯一約束
            unique_constraints = {
                'merchants': ['line_channel_id'],
                'users': ['merchant_id', 'line_user_id'],
                'services': ['merchant_id', 'name'],
                'appointments': ['merchant_id', 'branch_id', 'appointment_date', 'appointment_time', 'staff_id']
            }
            
            for table_name, constraint_cols in unique_constraints.items():
                if table_name not in self.inspector.get_table_names():
                    continue
                
                # 檢查唯一約束是否存在
                constraints = self.inspector.get_unique_constraints(table_name)
                constraint_exists = any(
                    set(c['column_names']) == set(constraint_cols) 
                    for c in constraints
                )
                
                if constraint_exists:
                    print(f"  ✓ 表 {table_name} 唯一約束正確")
                else:
                    self.errors.append(f"表 {table_name} 缺少唯一約束: {constraint_cols}")
    
    def _validate_indexes(self):
        """驗證索引"""
        print("\n4. 驗證索引...")
        
        expected_indexes = {
            'merchants': ['line_channel_id', 'is_active'],
            'users': ['merchant_id', 'merchant_id, line_user_id'],
            'services': ['merchant_id', 'merchant_id, is_active'],
            'appointments': ['merchant_id, appointment_date', 'merchant_id, user_id', 'appointment_date, appointment_time'],
            'transactions': ['merchant_id, created_at', 'merchant_id, user_id'],
            'business_hours': ['merchant_id', 'day_of_week'],
            'time_off': ['merchant_id', 'start_datetime, end_datetime']
        }
        
        for table_name, expected_idx in expected_indexes.items():
            if table_name not in self.inspector.get_table_names():
                continue
            
            indexes = self.inspector.get_indexes(table_name)
            existing_indexes = [idx['column_names'] for idx in indexes]
            
            for idx_cols in expected_idx:
                idx_cols_list = idx_cols.split(', ')
                if idx_cols_list not in existing_indexes:
                    self.warnings.append(f"表 {table_name} 建議添加索引: {idx_cols}")
                else:
                    print(f"  ✓ 表 {table_name} 索引 {idx_cols} 存在")
    
    def _validate_foreign_keys(self):
        """驗證外鍵"""
        print("\n5. 驗證外鍵...")
        
        expected_fks = {
            'users': ['merchant_id -> merchants.id'],
            'services': ['merchant_id -> merchants.id'],
            'appointments': ['merchant_id -> merchants.id', 'user_id -> users.id', 'service_id -> services.id'],
            'transactions': ['merchant_id -> merchants.id', 'user_id -> users.id', 'appointment_id -> appointments.id'],
            'business_hours': ['merchant_id -> merchants.id'],
            'time_off': ['merchant_id -> merchants.id']
        }
        
        for table_name, expected_fk in expected_fks.items():
            if table_name not in self.inspector.get_table_names():
                continue
            
            fks = self.inspector.get_foreign_keys(table_name)
            existing_fks = [f"{fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}" 
                           for fk in fks]
            
            for fk in expected_fk:
                if fk in existing_fks:
                    print(f"  ✓ 表 {table_name} 外鍵 {fk} 存在")
                else:
                    self.errors.append(f"表 {table_name} 缺少外鍵: {fk}")
    
    def _validate_rls(self):
        """驗證 Row Level Security"""
        print("\n6. 驗證 Row Level Security...")
        
        rls_tables = ['users', 'services', 'appointments', 'transactions', 'business_hours', 'time_off']
        
        with self.engine.connect() as conn:
            for table_name in rls_tables:
                if table_name not in self.inspector.get_table_names():
                    continue
                
                # 檢查 RLS 是否啟用
                result = conn.execute(text(f"""
                    SELECT relrowsecurity 
                    FROM pg_class 
                    WHERE relname = '{table_name}'
                """)).fetchone()
                
                if result and result[0]:
                    print(f"  ✓ 表 {table_name} RLS 已啟用")
                else:
                    self.warnings.append(f"表 {table_name} RLS 未啟用")
                
                # 檢查 RLS 策略
                policies = conn.execute(text(f"""
                    SELECT policyname 
                    FROM pg_policies 
                    WHERE tablename = '{table_name}'
                """)).fetchall()
                
                if policies:
                    print(f"  ✓ 表 {table_name} 有 {len(policies)} 個 RLS 策略")
                else:
                    self.warnings.append(f"表 {table_name} 缺少 RLS 策略")
    
    def _validate_data_isolation(self):
        """驗證資料隔離"""
        print("\n7. 驗證資料隔離...")
        
        with self.engine.connect() as conn:
            # 檢查是否有跨商家的資料
            isolation_queries = {
                'users': "SELECT COUNT(DISTINCT merchant_id) as merchant_count FROM users",
                'services': "SELECT COUNT(DISTINCT merchant_id) as merchant_count FROM services",
                'appointments': "SELECT COUNT(DISTINCT merchant_id) as merchant_count FROM appointments",
                'transactions': "SELECT COUNT(DISTINCT merchant_id) as merchant_count FROM transactions"
            }
            
            for table_name, query in isolation_queries.items():
                if table_name not in self.inspector.get_table_names():
                    continue
                
                try:
                    result = conn.execute(text(query)).fetchone()
                    if result and result[0] > 0:
                        print(f"  ✓ 表 {table_name} 包含 {result[0]} 個商家的資料")
                    else:
                        print(f"  ℹ 表 {table_name} 目前沒有資料")
                except Exception as e:
                    self.warnings.append(f"無法驗證表 {table_name} 的資料隔離: {str(e)}")
    
    def _print_results(self):
        """輸出驗證結果"""
        print("\n" + "=" * 60)
        print("驗證結果")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ 發現 {len(self.errors)} 個錯誤:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️ 發現 {len(self.warnings)} 個警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 所有驗證通過！資料庫架構符合 ERD 設計規範。")
        elif not self.errors:
            print("\n✅ 核心驗證通過，但有警告需要關注。")
        else:
            print(f"\n❌ 驗證失敗，需要修復 {len(self.errors)} 個錯誤。")
        
        print("\n建議:")
        if self.errors:
            print("- 修復所有錯誤後重新驗證")
        if self.warnings:
            print("- 考慮處理警告以提高系統性能")
        print("- 定期運行此驗證腳本確保架構一致性")
        print("- 在部署前運行完整的資料庫優化腳本")


def main():
    """主函數"""
    try:
        validator = DatabaseSchemaValidator()
        success = validator.validate_all()
        
        if not success:
            print("\n驗證失敗，請修復錯誤後重新運行。")
            sys.exit(1)
        else:
            print("\n資料庫架構驗證完成！")
            
    except Exception as e:
        print(f"驗證過程中發生錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
