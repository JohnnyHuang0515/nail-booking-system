"""
LINE Webhook 處理器：處理多商家的 LINE 事件
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
import json

from app.context import RequestContext
from app.line_client import LineClient
from app.flex_templates import FlexTemplates
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.repositories.sql_service_repository import SqlServiceRepository
from app.infrastructure.repositories.sql_appointment_repository import SqlAppointmentRepository
from app.infrastructure.database.session import get_db_session

router = APIRouter()


@router.post("/line/webhook")
async def line_webhook(request: Request):
    """
    處理 LINE Webhook 事件
    
    此端點會由中介軟體自動設定商家上下文
    """
    try:
        # 從中介軟體設定的狀態中取得解析後的負載
        payload = getattr(request.state, 'line_payload', None)
        if not payload:
            raise HTTPException(status_code=400, detail="無效的 Webhook 負載")
        
        # 取得當前商家上下文
        merchant_id = RequestContext.get_merchant_id()
        line_token = RequestContext.get_line_token()
        merchant_data = RequestContext.get_merchant_data()
        
        if not merchant_id or not line_token:
            raise HTTPException(status_code=400, detail="商家上下文未正確設定")
        
        # 處理事件
        events = payload.get("events", [])
        line_client = get_line_client()
        
        for event in events:
            await _handle_line_event(event, merchant_id, line_client, merchant_data)
        
        return {"status": "success", "message": "事件處理完成"}
        
    except Exception as e:
        print(f"LINE Webhook 處理錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理 Webhook 事件時發生錯誤: {str(e)}")


async def _handle_line_event(event: Dict[str, Any], merchant_id: str, line_client, merchant_data: Dict[str, Any]):
    """處理單個 LINE 事件"""
    event_type = event.get("type")
    
    if event_type == "message":
        await _handle_message_event(event, merchant_id, line_client, merchant_data)
    elif event_type == "postback":
        await _handle_postback_event(event, merchant_id, line_client, merchant_data)
    elif event_type == "follow":
        await _handle_follow_event(event, merchant_id, line_client, merchant_data)
    elif event_type == "unfollow":
        await _handle_unfollow_event(event, merchant_id, line_client, merchant_data)
    else:
        print(f"未處理的事件類型: {event_type}")


async def _handle_message_event(event: Dict[str, Any], merchant_id: str, line_client, merchant_data: Dict[str, Any]):
    """處理訊息事件"""
    message = event.get("message", {})
    message_type = message.get("type")
    reply_token = event.get("replyToken")
    user_id = event.get("source", {}).get("userId")
    
    if not reply_token or not user_id:
        return
    
    # 取得或創建使用者
    with get_db_session() as db_session:
        user_repo = SQLUserRepository(db_session)
        user = user_repo.get_or_create_by_line_user_id(merchant_id, user_id)
        
        if message_type == "text":
            text = message.get("text", "")
            await _handle_text_message(text, user, reply_token, line_client, merchant_data)


async def _handle_text_message(text: str, user, reply_token: str, line_client, merchant_data: Dict[str, Any]):
    """處理文字訊息"""
    merchant_name = merchant_data.get("name", "美甲店")
    
    # 簡單的關鍵字處理
    if "預約" in text or "預訂" in text:
        # 顯示服務選擇
        await _show_service_selection(reply_token, line_client, merchant_name, user.merchant_id)
    elif "服務" in text:
        await _show_service_selection(reply_token, line_client, merchant_name, user.merchant_id)
    elif "取消" in text:
        await _show_cancel_options(reply_token, line_client, user)
    else:
        # 預設歡迎訊息
        welcome_flex = FlexTemplates.welcome_message(merchant_name)
        await line_client.reply_flex(reply_token, welcome_flex, "歡迎訊息")


async def _handle_postback_event(event: Dict[str, Any], merchant_id: str, line_client, merchant_data: Dict[str, Any]):
    """處理 Postback 事件"""
    postback = event.get("postback", {})
    data = postback.get("data", "")
    reply_token = event.get("replyToken")
    user_id = event.get("source", {}).get("userId")
    
    if not reply_token or not user_id:
        return
    
    # 解析 postback data
    params = _parse_postback_data(data)
    action = params.get("action")
    
    # 取得使用者
    with get_db_session() as db_session:
        user_repo = SQLUserRepository(db_session)
        user = user_repo.get_or_create_by_line_user_id(merchant_id, user_id)
        
        if action == "start_booking":
            await _show_service_selection(reply_token, line_client, merchant_data.get("name"), merchant_id)
        elif action == "view_services":
            await _show_service_selection(reply_token, line_client, merchant_data.get("name"), merchant_id)
        elif action == "select_service":
            service_id = params.get("service_id")
            await _handle_service_selection(service_id, user, reply_token, line_client, merchant_data)
        elif action == "cancel":
            appointment_id = params.get("apt")
            await _handle_appointment_cancellation(appointment_id, user, reply_token, line_client, merchant_data)
        else:
            print(f"未處理的 postback action: {action}")


async def _handle_follow_event(event: Dict[str, Any], merchant_id: str, line_client, merchant_data: Dict[str, Any]):
    """處理關注事件"""
    user_id = event.get("source", {}).get("userId")
    reply_token = event.get("replyToken")
    
    if not reply_token or not user_id:
        return
    
    # 取得或創建使用者
    with get_db_session() as db_session:
        user_repo = SQLUserRepository(db_session)
        user = user_repo.get_or_create_by_line_user_id(merchant_id, user_id)
        
        # 發送歡迎訊息
        welcome_flex = FlexTemplates.welcome_message(merchant_data.get("name", "美甲店"))
        await line_client.reply_flex(reply_token, welcome_flex, "歡迎加入！")


async def _handle_unfollow_event(event: Dict[str, Any], merchant_id: str, line_client, merchant_data: Dict[str, Any]):
    """處理取消關注事件"""
    user_id = event.get("source", {}).get("userId")
    print(f"使用者 {user_id} 取消關注商家 {merchant_id}")


async def _show_service_selection(reply_token: str, line_client, merchant_name: str, merchant_id: str):
    """顯示服務選擇"""
    with get_db_session() as db_session:
        service_repo = SQLServiceRepository(db_session)
        services = service_repo.list_by_merchant(merchant_id)
        
        if not services:
            await line_client.reply_text(reply_token, "目前沒有可用的服務，請稍後再試。")
            return
        
        # 轉換為 Flex Message 需要的格式
        service_list = []
        for service in services:
            service_list.append({
                "id": str(service.id),
                "name": service.name,
                "price": float(service.price),
                "duration_minutes": service.duration_minutes
            })
        
        flex_content = FlexTemplates.service_selection(merchant_name, service_list)
        await line_client.reply_flex(reply_token, flex_content, "服務選擇")


async def _handle_service_selection(service_id: str, user, reply_token: str, line_client, merchant_data: Dict[str, Any]):
    """處理服務選擇"""
    if not service_id:
        await line_client.reply_text(reply_token, "服務選擇無效，請重新選擇。")
        return
    
    with get_db_session() as db_session:
        service_repo = SQLServiceRepository(db_session)
        service = service_repo.find_by_id(service_id)
        
        if not service:
            await line_client.reply_text(reply_token, "找不到指定的服務，請重新選擇。")
            return
        
        # 這裡可以進一步處理預約流程
        # 例如顯示日期時間選擇器等
        await line_client.reply_text(
            reply_token, 
            f"您選擇了 {service.name}，價格 NT$ {service.price:,.0f}。\n"
            f"請稍後，我們將為您安排預約時間。"
        )


async def _handle_appointment_cancellation(appointment_id: str, user, reply_token: str, line_client, merchant_data: Dict[str, Any]):
    """處理預約取消"""
    if not appointment_id:
        await line_client.reply_text(reply_token, "預約ID無效。")
        return
    
    with get_db_session() as db_session:
        appointment_repo = SQLAppointmentRepository(db_session)
        appointment = appointment_repo.find_by_id(appointment_id)
        
        if not appointment or appointment.user_id != user.id:
            await line_client.reply_text(reply_token, "找不到指定的預約記錄。")
            return
        
        # 取消預約
        success = appointment_repo.cancel_appointment(appointment_id)
        
        if success:
            await line_client.reply_text(reply_token, "預約已成功取消。")
        else:
            await line_client.reply_text(reply_token, "取消預約失敗，請聯繫客服。")


async def _show_cancel_options(reply_token: str, line_client, user):
    """顯示取消選項"""
    with get_db_session() as db_session:
        appointment_repo = SQLAppointmentRepository(db_session)
        appointments = appointment_repo.list_by_user_id(user.id)
        
        if not appointments:
            await line_client.reply_text(reply_token, "您目前沒有預約記錄。")
            return
        
        # 這裡可以顯示預約列表供選擇取消
        await line_client.reply_text(reply_token, "請選擇要取消的預約，或提供預約編號。")


def _parse_postback_data(data: str) -> Dict[str, str]:
    """解析 postback data"""
    params = {}
    for pair in data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    return params
