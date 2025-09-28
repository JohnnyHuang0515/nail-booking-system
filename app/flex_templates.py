"""
Flex Message 模板：多商家預約系統的訊息模板
"""
from typing import Dict, Any, Optional
from datetime import datetime, date, time
from uuid import UUID


class FlexTemplates:
    """Flex Message 模板集合"""
    
    @staticmethod
    def appointment_confirmation(
        merchant_name: str,
        merchant_id: UUID,
        appointment_id: UUID,
        user_name: str,
        service_name: str,
        appointment_date: date,
        appointment_time: time,
        price: float
    ) -> Dict[str, Any]:
        """
        預約確認 Flex Message
        
        Args:
            merchant_name: 商家名稱
            merchant_id: 商家ID
            appointment_id: 預約ID
            user_name: 使用者名稱
            service_name: 服務名稱
            appointment_date: 預約日期
            appointment_time: 預約時間
            price: 價格
            
        Returns:
            Dict: Flex Message 內容
        """
        date_str = appointment_date.strftime("%Y年%m月%d日")
        time_str = appointment_time.strftime("%H:%M")
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": merchant_name,
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": "預約已建立",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"{date_str} {time_str}",
                        "weight": "bold",
                        "size": "xl",
                        "margin": "md",
                        "color": "#1DB446"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "服務",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": service_name,
                                        "flex": 5,
                                        "wrap": True,
                                        "color": "#333333"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "姓名",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": user_name,
                                        "flex": 5,
                                        "wrap": True,
                                        "color": "#333333"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "價格",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"NT$ {price:,.0f}",
                                        "flex": 5,
                                        "color": "#1DB446",
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "取消預約",
                            "data": f"action=cancel&merchant_id={merchant_id}&apt={appointment_id}",
                            "displayText": "取消預約"
                        },
                        "color": "#FF6B6B"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "查看詳情",
                            "data": f"action=view&merchant_id={merchant_id}&apt={appointment_id}",
                            "displayText": "查看詳情"
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def service_selection(merchant_name: str, services: list) -> Dict[str, Any]:
        """
        服務選擇 Flex Message
        
        Args:
            merchant_name: 商家名稱
            services: 服務列表，每個服務包含 id, name, price, duration_minutes
            
        Returns:
            Dict: Flex Message 內容
        """
        service_buttons = []
        for service in services:
            service_buttons.append({
                "type": "button",
                "style": "primary",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": f"{service['name']} - NT$ {service['price']:,.0f}",
                    "data": f"action=select_service&service_id={service['id']}",
                    "displayText": f"選擇 {service['name']}"
                }
            })
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": merchant_name,
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": "請選擇您想要的服務",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": service_buttons
            }
        }
    
    @staticmethod
    def appointment_reminder(
        merchant_name: str,
        user_name: str,
        service_name: str,
        appointment_date: date,
        appointment_time: time,
        appointment_id: UUID
    ) -> Dict[str, Any]:
        """
        預約提醒 Flex Message
        
        Args:
            merchant_name: 商家名稱
            user_name: 使用者名稱
            service_name: 服務名稱
            appointment_date: 預約日期
            appointment_time: 預約時間
            appointment_id: 預約ID
            
        Returns:
            Dict: Flex Message 內容
        """
        date_str = appointment_date.strftime("%Y年%m月%d日")
        time_str = appointment_time.strftime("%H:%M")
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📅 預約提醒",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": f"親愛的 {user_name}，",
                        "size": "sm",
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"提醒您明天有預約！",
                        "size": "md",
                        "weight": "bold",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "商家",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": merchant_name,
                                        "flex": 5,
                                        "color": "#333333"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "時間",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{date_str} {time_str}",
                                        "flex": 5,
                                        "weight": "bold",
                                        "color": "#1DB446"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "服務",
                                        "flex": 2,
                                        "color": "#888888",
                                        "size": "sm"
                                    },
                                    {
                                        "type": "text",
                                        "text": service_name,
                                        "flex": 5,
                                        "color": "#333333"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "確認收到",
                            "data": f"action=reminder_ack&apt={appointment_id}",
                            "displayText": "確認收到"
                        },
                        "color": "#1DB446"
                    }
                ]
            }
        }
    
    @staticmethod
    def welcome_message(merchant_name: str) -> Dict[str, Any]:
        """
        歡迎訊息 Flex Message
        
        Args:
            merchant_name: 商家名稱
            
        Returns:
            Dict: Flex Message 內容
        """
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"歡迎來到 {merchant_name}！",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": "我們提供專業的美甲服務",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "請點擊下方按鈕開始預約",
                        "size": "md",
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "開始預約",
                            "data": "action=start_booking",
                            "displayText": "開始預約"
                        },
                        "color": "#1DB446"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "查看服務",
                            "data": "action=view_services",
                            "displayText": "查看服務"
                        }
                    }
                ]
            }
        }
