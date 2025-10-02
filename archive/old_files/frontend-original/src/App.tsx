import React from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent } from './components/ui/card';
import { Hand, Settings, Sparkles } from 'lucide-react';

export default function App() {
  const handleAdminClick = () => {
    // 在新視窗中開啟管理後台
    window.open('/admin-panel', '_blank');
  };

  const handleCustomerClick = () => {
    // 在新視窗中開啟客戶預約
    window.open('/customer-liff', '_blank');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-lg mx-auto w-full space-y-6">
        <div className="text-center space-y-4">
          <div className="mx-auto w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
            <Hand className="h-10 w-10 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-semibold text-foreground mb-2">美甲管理系統</h1>
            <p className="text-muted-foreground">請選擇您要使用的功能</p>
          </div>
        </div>

        <div className="grid gap-4">
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={handleAdminClick}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Settings className="h-6 w-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">管理後台</h3>
                  <p className="text-muted-foreground text-sm">
                    管理預約、服務項目、顧客資料等
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={handleCustomerClick}>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-pink-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">客戶預約</h3>
                  <p className="text-muted-foreground text-sm">
                    快速預約美甲服務
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          奶茶色系美甲管理系統 • 優雅簡約設計
        </div>
      </div>
    </div>
  );
}