"""
LINE Webhook 測試端點
"""
from fastapi import APIRouter, Request
import json

router = APIRouter()


@router.get("/webhook-test")
async def webhook_test_get():
    """測試 GET 請求"""
    return {"status": "ok", "message": "Webhook 測試端點正常"}


@router.post("/webhook-test")
async def webhook_test_post(request: Request):
    """測試 POST 請求"""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        result = {
            "status": "success",
            "message": "Webhook 測試成功",
            "headers": headers,
            "body": body.decode('utf-8') if body else "Empty"
        }
        
        print(f"收到測試請求: {result}")
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
