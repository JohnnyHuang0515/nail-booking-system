"""
Catalog Context - Domain Layer - Exceptions
"""
from shared.exceptions import DomainException


class ServiceNotFoundError(DomainException):
    """服務不存在異常"""
    
    def __init__(self, service_id: int):
        super().__init__(
            message=f"服務 {service_id} 不存在",
            error_code="service_not_found",
            details={"service_id": service_id}
        )


class StaffNotFoundError(DomainException):
    """員工不存在異常"""
    
    def __init__(self, staff_id: int):
        super().__init__(
            message=f"員工 {staff_id} 不存在",
            error_code="staff_not_found",
            details={"staff_id": staff_id}
        )


class StaffCannotPerformServiceError(DomainException):
    """員工無法執行服務異常"""
    
    def __init__(self, staff_id: int, service_id: int):
        super().__init__(
            message=f"員工 {staff_id} 無法執行服務 {service_id}（技能不符）",
            error_code="staff_cannot_perform_service",
            details={"staff_id": staff_id, "service_id": service_id}
        )


class ServiceOptionNotFoundError(DomainException):
    """服務選項不存在異常"""
    
    def __init__(self, option_id: int, service_id: int):
        super().__init__(
            message=f"服務 {service_id} 的選項 {option_id} 不存在",
            error_code="service_option_not_found",
            details={"option_id": option_id, "service_id": service_id}
        )

