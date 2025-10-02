from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import booking, services, schedule, appointments, dashboard, users, transactions, merchants, line_webhook, admin, merchant_auth, merchant_settings, monitoring, reporting, security, support, billing
from app.middleware import LineWebhookMiddleware, MultiTenantMiddleware

app = FastAPI(
    title="Multi-Merchant Nail Booking System",
    description="多商家美甲預約系統 API，支援多個 LINE 官方帳號",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # React development servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add LINE Webhook middleware (處理多商家 LINE 事件)
app.add_middleware(LineWebhookMiddleware)

# Add Multi-tenant middleware (處理一般 API 請求的商家上下文)
app.add_middleware(MultiTenantMiddleware)

# Include the v1 API routers
# 平台管理員 API
app.include_router(admin.router, prefix="/api/v1", tags=["Platform Admin"])

# 商家後台認證 API
app.include_router(merchant_auth.router, prefix="/api/v1", tags=["Merchant Auth"])

# 商家管理 API
app.include_router(merchants.router, prefix="/api/v1", tags=["Merchants"])

# 商家設定管理 API
app.include_router(merchant_settings.router, prefix="/api/v1", tags=["Merchant Settings"])

# 監控與健診 API
app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"])

# 資料與報表 API
app.include_router(reporting.router, prefix="/api/v1", tags=["Reporting"])

# 安全與治理 API
app.include_router(security.router, prefix="/api/v1", tags=["Security & Governance"])

# 支援與運維 API
app.include_router(support.router, prefix="/api/v1", tags=["Support & Operations"])

# 帳務管理 API
app.include_router(billing.router, prefix="/api/v1", tags=["Billing"])

# LINE Webhook API
app.include_router(line_webhook.router, prefix="/api/v1", tags=["LINE Webhook"])

# 業務 API (需要多租戶支援)
app.include_router(booking.router, prefix="/api/v1", tags=["Booking"])
app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(schedule.router, prefix="/api/v1", tags=["Schedule"])
app.include_router(appointments.router, prefix="/api/v1", tags=["Appointments"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])


@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Nail Booking System API!"}
