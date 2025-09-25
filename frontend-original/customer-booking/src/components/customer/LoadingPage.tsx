import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Scissors, Loader2 } from 'lucide-react';

interface LoadingPageProps {
  message?: string;
}

export default function LoadingPage({ message = '載入中...' }: LoadingPageProps) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md mx-auto w-full">
        <Card>
          <CardContent className="pt-12 pb-12">
            <div className="text-center space-y-6">
              {/* Logo with animation */}
              <div className="relative">
                <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                  <Scissors className="h-8 w-8 text-primary animate-pulse" />
                </div>
                <div className="absolute -top-1 -right-1">
                  <Loader2 className="h-6 w-6 text-primary animate-spin" />
                </div>
              </div>

              {/* App Title */}
              <div>
                <h1 className="text-2xl font-semibold text-foreground mb-2">美甲預約系統</h1>
                <p className="text-muted-foreground">為您打造完美的美甲體驗</p>
              </div>

              {/* Loading message */}
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">{message}</p>
                
                {/* Loading dots animation */}
                <div className="flex justify-center space-x-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>

              {/* Features preview */}
              <div className="text-xs text-muted-foreground space-y-1 pt-4 border-t">
                <div>✨ 多樣化美甲服務</div>
                <div>📅 靈活預約時段</div>
                <div>💅 專業美甲師團隊</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}