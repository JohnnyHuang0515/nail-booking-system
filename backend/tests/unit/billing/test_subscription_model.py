"""
Billing Context - Unit Tests - Subscription Aggregate
測試 Subscription 聚合的業務邏輯
"""
import pytest
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal

from billing.domain.models import (
    Subscription, Plan, SubscriptionStatus, PlanTier, PlanFeatures
)
from booking.domain.value_objects import Money


class TestSubscriptionAggregate:
    """Subscription 聚合根測試"""
    
    def test_create_subscription_with_trial(self):
        """✅ 測試案例：建立試用訂閱"""
        # Arrange & Act
        now = datetime.now(dt_timezone.utc)
        trial_end = now + timedelta(days=14)
        
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.TRIALING,
            trial_end=trial_end
        )
        
        # Assert
        assert subscription.id == "sub-001"
        assert subscription.status == SubscriptionStatus.TRIALING
        assert subscription.is_active() is True
        assert subscription.can_create_booking() is True
    
    def test_empty_merchant_id_raises_error(self):
        """✅ 測試案例：空商家 ID 應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="訂閱必須關聯到商家"):
            Subscription(
                id="sub-001",
                merchant_id="",  # 空字串
                plan_id=1
            )
    
    def test_invalid_period_raises_error(self):
        """✅ 測試案例：結束時間早於開始時間應拋出異常"""
        # Arrange
        now = datetime.now(dt_timezone.utc)
        past = now - timedelta(days=1)
        
        # Act & Assert
        with pytest.raises(ValueError, match="訂閱結束時間必須晚於開始時間"):
            Subscription(
                id="sub-001",
                merchant_id="merchant-001",
                plan_id=1,
                current_period_start=now,
                current_period_end=past  # 錯誤：早於開始時間
            )
    
    def test_is_active_for_active_status(self):
        """✅ 測試案例：active 狀態的 is_active() 返回 True"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Act & Assert
        assert subscription.is_active() is True
    
    def test_is_active_for_trialing_status(self):
        """✅ 測試案例：trialing 狀態的 is_active() 返回 True"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.TRIALING
        )
        
        # Act & Assert
        assert subscription.is_active() is True
    
    def test_is_active_false_for_cancelled_status(self):
        """✅ 測試案例：cancelled 狀態的 is_active() 返回 False"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.CANCELLED
        )
        
        # Act & Assert
        assert subscription.is_active() is False
    
    def test_can_create_booking_true_for_active(self):
        """✅ 測試案例：active 訂閱可建立預約"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Act & Assert
        assert subscription.can_create_booking() is True
    
    def test_can_create_booking_false_for_past_due(self):
        """✅ 測試案例：past_due 訂閱無法建立預約（核心！）"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.PAST_DUE
        )
        
        # Act & Assert
        assert subscription.can_create_booking() is False
    
    def test_can_create_booking_false_for_cancelled(self):
        """✅ 測試案例：cancelled 訂閱無法建立預約"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.CANCELLED
        )
        
        # Act & Assert
        assert subscription.can_create_booking() is False
    
    def test_activate_subscription(self):
        """✅ 測試案例：啟用訂閱（付款成功）"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.TRIALING
        )
        
        # Act
        subscription.activate()
        
        # Assert
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.updated_at is not None
    
    def test_mark_past_due(self):
        """✅ 測試案例：標記為逾期（付款失敗）"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Act
        subscription.mark_past_due()
        
        # Assert
        assert subscription.status == SubscriptionStatus.PAST_DUE
        assert subscription.can_create_booking() is False
    
    def test_cancel_subscription(self):
        """✅ 測試案例：取消訂閱"""
        # Arrange
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Act
        subscription.cancel()
        
        # Assert
        assert subscription.status == SubscriptionStatus.CANCELLED
        assert subscription.cancelled_at is not None
    
    def test_renew_subscription(self):
        """✅ 測試案例：續訂（更新週期）"""
        # Arrange
        now = datetime.now(dt_timezone.utc)
        current_end = now + timedelta(days=30)
        new_end = now + timedelta(days=60)
        
        subscription = Subscription(
            id="sub-001",
            merchant_id="merchant-001",
            plan_id=1,
            status=SubscriptionStatus.ACTIVE,
            current_period_end=current_end
        )
        
        # Act
        subscription.renew(new_period_end=new_end)
        
        # Assert
        assert subscription.current_period_end == new_end
        assert subscription.status == SubscriptionStatus.ACTIVE


class TestPlanAggregate:
    """Plan 聚合根測試"""
    
    def test_create_basic_plan(self):
        """✅ 測試案例：建立基礎方案"""
        # Act
        plan = Plan(
            id=1,
            tier=PlanTier.BASIC,
            name="基礎方案",
            price=Money(Decimal("999"), "TWD"),
            billing_interval="month"
        )
        
        # Assert
        assert plan.id == 1
        assert plan.tier == PlanTier.BASIC
        assert plan.price.amount == Decimal("999")
        assert plan.features is not None
    
    def test_negative_price_raises_error(self):
        """✅ 測試案例：負數價格應拋出異常（由 Money 值物件保護）"""
        # Act & Assert
        with pytest.raises(ValueError, match="金額不可為負數"):
            Plan(
                id=1,
                tier=PlanTier.BASIC,
                name="Test",
                price=Money(Decimal("-100"))
            )
    
    def test_invalid_billing_interval_raises_error(self):
        """✅ 測試案例：無效計費週期應拋出異常"""
        # Act & Assert
        with pytest.raises(ValueError, match="計費週期只能為"):
            Plan(
                id=1,
                tier=PlanTier.BASIC,
                name="Test",
                price=Money(Decimal("999")),
                billing_interval="week"  # 無效
            )
    
    def test_default_features_for_free_tier(self):
        """✅ 測試案例：免費方案的預設功能"""
        # Act
        plan = Plan(
            id=1,
            tier=PlanTier.FREE,
            name="免費方案",
            price=Money(Decimal("0"))
        )
        
        # Assert
        assert plan.features.max_bookings_per_month == 30
        assert plan.features.max_staff == 1
        assert plan.features.enable_line_notification is False
    
    def test_default_features_for_pro_tier(self):
        """✅ 測試案例：專業方案的預設功能"""
        # Act
        plan = Plan(
            id=1,
            tier=PlanTier.PRO,
            name="專業方案",
            price=Money(Decimal("2999"))
        )
        
        # Assert
        assert plan.features.max_bookings_per_month == 500
        assert plan.features.max_staff == 10
        assert plan.features.enable_line_notification is True
        assert plan.features.enable_custom_branding is True
        assert plan.features.enable_analytics is True


class TestPlanFeatures:
    """PlanFeatures 值物件測試"""
    
    def test_allows_booking_creation_within_quota(self):
        """✅ 測試案例：在額度內可建立預約"""
        # Arrange
        features = PlanFeatures(
            max_bookings_per_month=100,
            max_staff=3,
            max_services=20
        )
        
        # Act & Assert
        assert features.allows_booking_creation(50) is True
        assert features.allows_booking_creation(99) is True
    
    def test_allows_booking_creation_exceeds_quota(self):
        """✅ 測試案例：超過額度無法建立預約"""
        # Arrange
        features = PlanFeatures(
            max_bookings_per_month=100,
            max_staff=3,
            max_services=20
        )
        
        # Act & Assert
        assert features.allows_booking_creation(100) is False
        assert features.allows_booking_creation(150) is False


class TestSubscriptionStatus:
    """SubscriptionStatus 枚舉測試"""
    
    def test_status_values(self):
        """✅ 測試案例：狀態枚舉值正確"""
        assert SubscriptionStatus.ACTIVE.value == "active"
        assert SubscriptionStatus.PAST_DUE.value == "past_due"
        assert SubscriptionStatus.CANCELLED.value == "cancelled"
        assert SubscriptionStatus.TRIALING.value == "trialing"

