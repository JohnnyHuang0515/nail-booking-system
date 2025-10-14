# Feature: 建立預約
# 目的: 客戶可透過 LIFF 預約美甲服務，系統確保無時段重疊
# 對應 PRD: US-001, US-002
# Bounded Context: Booking

Feature: Create Booking

  Background:
    Given merchant "nail-abc" is active with id "123e4567-e89b-12d3-a456-426614174000"
    And merchant "nail-abc" subscription is "active"
    And staff "Amy" with id 1 belongs to merchant "nail-abc"
    And staff "Amy" is active
    And service "Gel Basic" with id 1 belongs to merchant "nail-abc"
    And service "Gel Basic" has price 800 TWD and duration 60 minutes
    And service "Gel Basic" is active

  @critical @happy-path
  Scenario: 成功建立單一服務預約
    Given staff "Amy" has no bookings on "2025-10-16" at "14:00"
    And staff "Amy" working hours on Wednesday include "14:00-15:00"
    When I create a booking with:
      | field       | value                                  |
      | merchant_id | 123e4567-e89b-12d3-a456-426614174000   |
      | staff_id    | 1                                      |
      | customer    | {"line_user_id": "U123", "name": "王小明"} |
      | start_at    | 2025-10-16T14:00:00+08:00              |
      | service_ids | [1]                                    |
    Then booking is created with status "confirmed"
    And booking total_price is 800 TWD
    And booking total_duration is 60 minutes
    And booking end_at is "2025-10-16T15:00:00+08:00"
    And a booking_lock exists for staff 1 from "14:00" to "15:00"
    And BookingConfirmed event is published
    And LINE notification is queued for user "U123"

  @happy-path
  Scenario: 建立含多個加購選項的預約
    Given service option "French Tips" with id 1 for service 1 has price 200 and duration 15
    And service option "Nail Art" with id 2 for service 1 has price 300 and duration 20
    When I create a booking with service 1 and options [1, 2]
    Then booking total_price is 1300 TWD
    And booking total_duration is 95 minutes
    And booking end_at is "2025-10-16T15:35:00+08:00"

  @critical @sad-path
  Scenario: 時段重疊應拋出錯誤
    Given an existing booking for staff "Amy" from "2025-10-16T13:00+08:00" to "2025-10-16T14:30+08:00"
    When I create a booking with start_at "2025-10-16T14:00+08:00" for staff "Amy"
    Then API responds with status code 400
    And response contains error_code "booking_overlap"
    And no new booking_lock is created
    And no BookingConfirmed event is published

  @edge-case
  Scenario: 併發請求只有一個成功
    Given two users simultaneously request booking for:
      | user | line_id |
      | User A | U111  |
      | User B | U222  |
    And both requests are for staff "Amy" at "2025-10-16T14:00+08:00"
    When both requests are processed concurrently
    Then exactly one booking is created
    And exactly one booking_lock exists
    And the other request receives error "booking_overlap"

  @sad-path
  Scenario: 商家停用應拒絕預約
    Given merchant "nail-abc" is inactive
    When I create a booking for merchant "nail-abc"
    Then API responds with status code 403
    And response contains error_code "merchant_inactive"

  @sad-path
  Scenario: 訂閱逾期應拒絕預約
    Given merchant "nail-abc" subscription is "past_due"
    When I create a booking for merchant "nail-abc"
    Then API responds with status code 403
    And response contains error_code "subscription_past_due"

  @edge-case
  Scenario: 員工停用應無法被預約
    Given staff "Amy" is inactive
    When I create a booking with staff "Amy"
    Then API responds with status code 400
    And response contains error_code "staff_inactive"

  @edge-case
  Scenario: 超出工作時間應拒絕
    Given staff "Amy" working hours on Wednesday are "10:00-18:00"
    When I create a booking with start_at "2025-10-16T18:30+08:00"
    Then API responds with status code 400
    And response contains error_code "outside_working_hours"

