import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { CreditCard, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import adminApiService from '../../services/api';

interface Plan {
  id: number;
  tier: string;
  name: string;
  price_amount: number;
  price_currency: string;
  billing_interval: string;
  features: {
    max_bookings_per_month: number;
    max_staff: number;
    max_services: number;
    enable_line_notification: boolean;
    enable_custom_branding: boolean;
    enable_analytics: boolean;
    support_level: string;
  };
  is_active: boolean;
  description?: string;
}

interface Subscription {
  id: string;
  merchant_id: string;
  plan_id: number;
  status: string;
  current_period_start: string;
  current_period_end: string;
  trial_end?: string;
  cancelled_at?: string;
  created_at: string;
  updated_at?: string;
}

interface SubscriptionStatus {
  can_create_booking: boolean;
  status: string;
  plan_name: string;
  features: any;
  quota_info?: any;
}

export default function Billing() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);
      setError('');

      const [plansData, statusData] = await Promise.all([
        adminApiService.getPlans(),
        adminApiService.getSubscriptionStatus().catch(() => null)
      ]);

      setPlans(plansData);
      setSubscriptionStatus(statusData);

      // 如果有訂閱，載入訂閱詳情
      if (statusData) {
        try {
          const subscriptionData = await adminApiService.getSubscription();
          setSubscription(subscriptionData);
        } catch (err) {
          console.log('No active subscription found');
        }
      }
    } catch (err: any) {
      console.error('載入計費資料失敗:', err);
      setError('載入計費資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubscription = async (planId: number) => {
    try {
      const newSubscription = await adminApiService.createSubscription(planId, 14);
      setSubscription(newSubscription);
      await loadBillingData(); // 重新載入資料
    } catch (err: any) {
      console.error('建立訂閱失敗:', err);
      setError('建立訂閱失敗，請稍後再試');
    }
  };

  const handleCancelSubscription = async () => {
    if (!subscription) return;
    
    try {
      await adminApiService.cancelSubscription(subscription.id);
      await loadBillingData(); // 重新載入資料
    } catch (err: any) {
      console.error('取消訂閱失敗:', err);
      setError('取消訂閱失敗，請稍後再試');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />啟用中</Badge>;
      case 'trialing':
        return <Badge className="bg-blue-100 text-blue-800"><Clock className="w-3 h-3 mr-1" />試用中</Badge>;
      case 'past_due':
        return <Badge className="bg-yellow-100 text-yellow-800"><AlertTriangle className="w-3 h-3 mr-1" />逾期</Badge>;
      case 'cancelled':
        return <Badge className="bg-red-100 text-red-800"><XCircle className="w-3 h-3 mr-1" />已取消</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">計費管理</h1>
        <CreditCard className="h-8 w-8 text-gray-600" />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 當前訂閱狀態 */}
      {subscriptionStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              當前訂閱狀態
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{subscriptionStatus.plan_name}</h3>
                <p className="text-sm text-gray-600">訂閱狀態: {getStatusBadge(subscriptionStatus.status)}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">
                  可建立預約: {subscriptionStatus.can_create_booking ? '是' : '否'}
                </p>
              </div>
            </div>

            {subscriptionStatus.features && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="font-medium">每月預約上限</p>
                  <p className="text-gray-600">{subscriptionStatus.features.max_bookings_per_month}</p>
                </div>
                <div>
                  <p className="font-medium">員工上限</p>
                  <p className="text-gray-600">{subscriptionStatus.features.max_staff}</p>
                </div>
                <div>
                  <p className="font-medium">服務上限</p>
                  <p className="text-gray-600">{subscriptionStatus.features.max_services}</p>
                </div>
                <div>
                  <p className="font-medium">支援等級</p>
                  <p className="text-gray-600">{subscriptionStatus.features.support_level}</p>
                </div>
              </div>
            )}

            {subscription && subscription.status === 'active' && (
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={handleCancelSubscription}
                  className="text-red-600 hover:text-red-700"
                >
                  取消訂閱
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 可用方案 */}
      <Card>
        <CardHeader>
          <CardTitle>可用方案</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <Card key={plan.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{plan.name}</CardTitle>
                    {plan.tier === 'free' && (
                      <Badge variant="secondary">免費</Badge>
                    )}
                  </div>
                  <div className="text-2xl font-bold">
                    {plan.price_amount === 0 ? '免費' : `$${plan.price_amount}`}
                    {plan.price_amount > 0 && (
                      <span className="text-sm font-normal text-gray-600">
                        /{plan.billing_interval === 'month' ? '月' : '年'}
                      </span>
                    )}
                  </div>
                  {plan.description && (
                    <p className="text-sm text-gray-600">{plan.description}</p>
                  )}
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>每月預約上限</span>
                      <span className="font-medium">{plan.features.max_bookings_per_month}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>員工上限</span>
                      <span className="font-medium">{plan.features.max_staff}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>服務上限</span>
                      <span className="font-medium">{plan.features.max_services}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>LINE 推播</span>
                      <span className="font-medium">
                        {plan.features.enable_line_notification ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>客製化品牌</span>
                      <span className="font-medium">
                        {plan.features.enable_custom_branding ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>數據分析</span>
                      <span className="font-medium">
                        {plan.features.enable_analytics ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>支援等級</span>
                      <span className="font-medium">{plan.features.support_level}</span>
                    </div>
                  </div>

                  {(!subscriptionStatus || subscriptionStatus.status === 'cancelled') && (
                    <Button 
                      className="w-full" 
                      onClick={() => handleCreateSubscription(plan.id)}
                    >
                      {plan.tier === 'free' ? '選擇方案' : '開始試用'}
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
