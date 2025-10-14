import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { AlertTriangle, RefreshCw, Home, Phone } from 'lucide-react';

interface ErrorPageProps {
  error?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
}

export default function ErrorPage({ 
  error = '系統發生錯誤，請稍後再試', 
  onRetry,
  onGoHome 
}: ErrorPageProps) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md mx-auto w-full">
        <Card>
          <CardContent className="pt-12 pb-12">
            <div className="text-center space-y-6">
              {/* Error Icon */}
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>

              {/* Error Title */}
              <div>
                <h1 className="text-2xl font-semibold text-foreground mb-2">出現問題了</h1>
                <p className="text-muted-foreground">{error}</p>
              </div>

              {/* Error Details */}
              <div className="text-sm text-muted-foreground bg-muted p-4 rounded-lg text-left">
                <div className="font-medium mb-2">可能的原因：</div>
                <ul className="space-y-1 list-disc list-inside">
                  <li>網路連線不穩定</li>
                  <li>伺服器暫時無法回應</li>
                  <li>系統正在維護中</li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                {onRetry && (
                  <Button onClick={onRetry} className="w-full">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    重新載入
                  </Button>
                )}
                
                <div className="flex space-x-3">
                  {onGoHome && (
                    <Button variant="outline" onClick={onGoHome} className="flex-1">
                      <Home className="h-4 w-4 mr-2" />
                      回到首頁
                    </Button>
                  )}
                  <Button variant="outline" className="flex-1">
                    <Phone className="h-4 w-4 mr-2" />
                    聯繫客服
                  </Button>
                </div>
              </div>

              {/* Support Info */}
              <div className="text-xs text-muted-foreground pt-4 border-t space-y-1">
                <div>如問題持續發生，請聯繫我們：</div>
                <div className="font-mono">02-1234-5678</div>
                <div>或透過 LINE 官方帳號聯繫</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}