"""
簡化的 LINE Webhook 處理器：用於測試
"""
from fastapi import APIRouter, Request, HTTPException
import json

router = APIRouter()


@router.post("/line/webhook")
async def simple_line_webhook(request: Request):
    """
    簡化的 LINE Webhook 處理器
    用於測試 LINE 連接
    """
    try:
        # 讀取請求主體
        body = await request.body()
        
        # 記錄請求資訊
        print(f"收到 LINE Webhook 請求:")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {body.decode('utf-8') if body else 'Empty'}")
        
        # 嘗試解析 JSON
        if body:
            try:
                payload = json.loads(body.decode('utf-8'))
                print(f"解析的負載: {payload}")
            except json.JSONDecodeError as e:
                print(f"JSON 解析錯誤: {e}")
        
        # 返回成功響應
        return {"status": "success", "message": "Webhook 接收成功"}
        
    except Exception as e:
        print(f"Webhook 處理錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理 Webhook 時發生錯誤: {str(e)}")


@router.get("/line/webhook")
async def webhook_verification(request: Request):
    """
    LINE Webhook 驗證端點
    """
    return {"status": "ok", "message": "Webhook 端點正常"}
