# Feature: 查詢可訂時段
# 目的: 客戶可查看特定日期的可預約時段
# 對應 PRD: US-003

Feature: Query Bookable Slots

  @happy-path
  Scenario: 客戶查看特定日期的可預約時段
    Given merchant "nail-abc" is active
    And staff "Amy" is active with working hours on "2025-10-15" from "10:00" to "18:00"
    And a booking exists from "2025-10-15T13:00+08:00" to "14:30+08:00" for "Amy"
    When I query slots for "2025-10-15" and staff "Amy"
    Then I should not see any slot overlapping "13:00-14:30"
    And I should see at least one slot "10:00-11:00"
    And I should see at least one slot "15:00-16:00"

  @edge-case
  Scenario: 全天滿檔應返回空列表
    Given staff "Amy" working hours on "2025-10-16" are "10:00-18:00"
    And staff "Amy" has bookings covering all time from "10:00" to "18:00"
    When I query slots for "2025-10-16" and staff "Amy"
    Then all returned slots have available=false
    Or the slots list is empty

  @edge-case
  Scenario: 員工休假日應無可訂時段
    Given staff "Amy" has a time_off from "2025-10-17T00:00" to "2025-10-17T23:59"
    When I query slots for "2025-10-17" and staff "Amy"
    Then all slots have available=false
    Or the slots list is empty

