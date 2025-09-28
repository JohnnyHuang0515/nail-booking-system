"""
Rich Menu 管理器
負責 Rich Menu 的創建、更新、發布和回滾
"""
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RichMenuManager:
    """Rich Menu 管理器"""
    
    def __init__(self):
        self.base_url = "https://api.line.me/v2"
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def create_default_rich_menu(self, access_token: str) -> str:
        """
        創建預設 Rich Menu
        
        Args:
            access_token: LINE Access Token
            
        Returns:
            str: Rich Menu ID
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 預設 Rich Menu 配置
            rich_menu_data = {
                "size": {
                    "width": 2500,
                    "height": 1686
                },
                "selected": False,
                "name": "美甲預約系統主選單",
                "chatBarText": "預約美甲",
                "areas": [
                    {
                        "bounds": {
                            "x": 0,
                            "y": 0,
                            "width": 1250,
                            "height": 843
                        },
                        "action": {
                            "type": "uri",
                            "uri": "https://liff.line.me/your-liff-id/booking"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1250,
                            "y": 0,
                            "width": 1250,
                            "height": 843
                        },
                        "action": {
                            "type": "uri",
                            "uri": "https://liff.line.me/your-liff-id/services"
                        }
                    },
                    {
                        "bounds": {
                            "x": 0,
                            "y": 843,
                            "width": 1250,
                            "height": 843
                        },
                        "action": {
                            "type": "uri",
                            "uri": "https://liff.line.me/your-liff-id/appointments"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1250,
                            "y": 843,
                            "width": 1250,
                            "height": 843
                        },
                        "action": {
                            "type": "uri",
                            "uri": "https://liff.line.me/your-liff-id/contact"
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/bot/richmenu",
                    headers=headers,
                    json=rich_menu_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        rich_menu_id = result.get("richMenuId")
                        logger.info(f"Rich Menu 創建成功: {rich_menu_id}")
                        return rich_menu_id
                    else:
                        error_text = await response.text()
                        raise Exception(f"Rich Menu 創建失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"創建 Rich Menu 失敗: {str(e)}")
            raise
    
    async def upload_rich_menu_image(self, access_token: str, rich_menu_id: str, image_data: bytes) -> bool:
        """
        上傳 Rich Menu 圖片
        
        Args:
            access_token: LINE Access Token
            rich_menu_id: Rich Menu ID
            image_data: 圖片資料
            
        Returns:
            bool: 上傳是否成功
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "image/jpeg"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/bot/richmenu/{rich_menu_id}/content",
                    headers=headers,
                    data=image_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Rich Menu 圖片上傳成功: {rich_menu_id}")
                        return True
                    else:
                        error_text = await response.text()
                        raise Exception(f"Rich Menu 圖片上傳失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"上傳 Rich Menu 圖片失敗: {str(e)}")
            raise
    
    async def set_default_rich_menu(self, access_token: str, rich_menu_id: str) -> bool:
        """
        設定預設 Rich Menu
        
        Args:
            access_token: LINE Access Token
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 設定是否成功
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/bot/user/all/richmenu/{rich_menu_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"預設 Rich Menu 設定成功: {rich_menu_id}")
                        return True
                    else:
                        error_text = await response.text()
                        raise Exception(f"設定預設 Rich Menu 失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"設定預設 Rich Menu 失敗: {str(e)}")
            raise
    
    async def get_rich_menu_list(self, access_token: str) -> List[Dict[str, Any]]:
        """
        取得 Rich Menu 列表
        
        Args:
            access_token: LINE Access Token
            
        Returns:
            List[Dict]: Rich Menu 列表
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.base_url}/bot/richmenu/list",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("richmenus", [])
                    else:
                        error_text = await response.text()
                        raise Exception(f"取得 Rich Menu 列表失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"取得 Rich Menu 列表失敗: {str(e)}")
            raise
    
    async def delete_rich_menu(self, access_token: str, rich_menu_id: str) -> bool:
        """
        刪除 Rich Menu
        
        Args:
            access_token: LINE Access Token
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 刪除是否成功
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.delete(
                    f"{self.base_url}/bot/richmenu/{rich_menu_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"Rich Menu 刪除成功: {rich_menu_id}")
                        return True
                    else:
                        error_text = await response.text()
                        raise Exception(f"刪除 Rich Menu 失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"刪除 Rich Menu 失敗: {str(e)}")
            raise
    
    async def publish_rich_menu(self, access_token: str, rich_menu_id: str) -> Dict[str, Any]:
        """
        發布 Rich Menu
        
        Args:
            access_token: LINE Access Token
            rich_menu_id: Rich Menu ID
            
        Returns:
            Dict: 發布結果
        """
        try:
            # 1. 設定為預設 Rich Menu
            success = await self.set_default_rich_menu(access_token, rich_menu_id)
            
            if success:
                return {
                    "status": "success",
                    "message": "Rich Menu 發布成功",
                    "rich_menu_id": rich_menu_id,
                    "published_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Rich Menu 發布失敗",
                    "rich_menu_id": rich_menu_id,
                    "published_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Rich Menu 發布失敗: {str(e)}",
                "rich_menu_id": rich_menu_id,
                "published_at": datetime.now().isoformat()
            }
    
    async def rollback_rich_menu(self, access_token: str, previous_rich_menu_id: str) -> Dict[str, Any]:
        """
        回滾 Rich Menu
        
        Args:
            access_token: LINE Access Token
            previous_rich_menu_id: 之前的 Rich Menu ID
            
        Returns:
            Dict: 回滾結果
        """
        try:
            # 設定之前的 Rich Menu 為預設
            success = await self.set_default_rich_menu(access_token, previous_rich_menu_id)
            
            if success:
                return {
                    "status": "success",
                    "message": "Rich Menu 回滾成功",
                    "rich_menu_id": previous_rich_menu_id,
                    "rolled_back_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Rich Menu 回滾失敗",
                    "rich_menu_id": previous_rich_menu_id,
                    "rolled_back_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Rich Menu 回滾失敗: {str(e)}",
                "rich_menu_id": previous_rich_menu_id,
                "rolled_back_at": datetime.now().isoformat()
            }
