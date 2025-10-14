# Feature: 取消預約
# 目的: 客戶可在 LINE 中取消預約，釋放時段
# 對應 PRD: US-011

Feature: Cancel Booking

  @happy-path
  Scenario: 客戶成功取消已確認預約
    Given a confirmed booking "B123" exists for user "U1"
    And booking "B123" is scheduled for "2025-10-16T14:00+08:00"
    When the user "U1" cancels booking "B123"
    Then booking "B123" status becomes "cancelled"
    And the time slot is released for staff
    And LINE sends a cancellation confirmation to user "U1"
    And the cancelled_at timestamp is recorded

  @sad-path
  Scenario: 無法取消已完成的預約
    Given a completed booking "B456" exists for user "U1"
    When the user "U1" attempts to cancel booking "B456"
    Then API responds with status code 400
    And response contains error_code "booking_already_completed"
    And booking "B456" status remains "completed"

  @edge-case
  Scenario: 僅預約擁有者可取消
    Given a confirmed booking "B789" exists for user "U1"
    When user "U2" attempts to cancel booking "B789"
    Then API responds with status code 403
    And response contains error_code "permission_denied"

  @edge-case
  Scenario: 取消已取消的預約應失敗
    Given a cancelled booking "B999" exists for user "U1"
    When the user "U1" attempts to cancel booking "B999"
    Then API responds with status code 400
    And response contains error_code "booking_already_cancelled"

