import React, { useState, useEffect } from 'react';
import { Plus, Search, MessageSquare, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface Ticket {
  id: string;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  merchant_id: string;
  merchant_name: string;
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  messages: TicketMessage[];
}

interface TicketMessage {
  id: string;
  content: string;
  sender: string;
  sender_type: 'user' | 'admin';
  created_at: string;
}

const TicketCenter: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      // Mock data for now
      const mockTickets: Ticket[] = [
        {
          id: '1',
          title: 'LINE Webhook 無法接收訊息',
          description: '商家回報LINE Webhook無法正常接收客戶訊息，請協助檢查。',
          status: 'open',
          priority: 'high',
          category: '技術問題',
          merchant_id: '123e4567-e89b-12d3-a456-426614174000',
          merchant_name: '美甲工作室A',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-15T10:30:00Z',
          messages: [
            {
              id: '1',
              content: '商家回報LINE Webhook無法正常接收客戶訊息，請協助檢查。',
              sender: '美甲工作室A',
              sender_type: 'user',
              created_at: '2024-01-15T10:30:00Z'
            }
          ]
        },
        {
          id: '2',
          title: '預約系統時間設定問題',
          description: '希望調整營業時間設定，但系統顯示錯誤。',
          status: 'in_progress',
          priority: 'medium',
          category: '功能需求',
          merchant_id: '123e4567-e89b-12d3-a456-426614174001',
          merchant_name: '美甲工作室B',
          created_at: '2024-01-14T15:20:00Z',
          updated_at: '2024-01-15T09:15:00Z',
          assigned_to: 'admin@platform.com',
          messages: [
            {
              id: '1',
              content: '希望調整營業時間設定，但系統顯示錯誤。',
              sender: '美甲工作室B',
              sender_type: 'user',
              created_at: '2024-01-14T15:20:00Z'
            },
            {
              id: '2',
              content: '已收到您的問題，正在檢查系統設定。',
              sender: 'admin@platform.com',
              sender_type: 'admin',
              created_at: '2024-01-15T09:15:00Z'
            }
          ]
        }
      ];
      setTickets(mockTickets);
    } catch (error) {
      console.error('取得工單失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'resolved':
      case 'closed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <MessageSquare className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const sendMessage = async (ticketId: string) => {
    if (!newMessage.trim()) return;

    try {
      // Mock API call
      const message: TicketMessage = {
        id: Date.now().toString(),
        content: newMessage,
        sender: 'admin@platform.com',
        sender_type: 'admin',
        created_at: new Date().toISOString()
      };

      setTickets(prev => prev.map(ticket => 
        ticket.id === ticketId 
          ? { ...ticket, messages: [...ticket.messages, message], updated_at: new Date().toISOString() }
          : ticket
      ));

      if (selectedTicket?.id === ticketId) {
        setSelectedTicket(prev => prev ? {
          ...prev,
          messages: [...prev.messages, message],
          updated_at: new Date().toISOString()
        } : null);
      }

      setNewMessage('');
    } catch (error) {
      console.error('發送訊息失敗:', error);
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ticket.merchant_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">工單中心</h1>
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4 mr-2" />
          新增工單
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 工單列表 */}
        <div className="lg:col-span-1 space-y-4">
          {/* 篩選器 */}
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="搜尋工單..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">所有狀態</option>
                <option value="open">待處理</option>
                <option value="in_progress">處理中</option>
                <option value="resolved">已解決</option>
                <option value="closed">已關閉</option>
              </select>
            </div>
          </div>

          {/* 工單列表 */}
          <div className="space-y-2">
            {loading ? (
              <div className="p-4 text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-500">載入中...</p>
              </div>
            ) : (
              filteredTickets.map((ticket) => (
                <div
                  key={ticket.id}
                  onClick={() => setSelectedTicket(ticket)}
                  className={`p-4 bg-white rounded-lg shadow-sm border cursor-pointer transition-colors ${
                    selectedTicket?.id === ticket.id ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {ticket.title}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {ticket.merchant_name}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2 ml-2">
                      {getStatusIcon(ticket.status)}
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(ticket.updated_at).toLocaleString('zh-TW')}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 工單詳情 */}
        <div className="lg:col-span-2">
          {selectedTicket ? (
            <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
              {/* 工單標題 */}
              <div className="p-6 border-b">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {selectedTicket.title}
                    </h2>
                    <p className="text-sm text-gray-500 mt-1">
                      {selectedTicket.merchant_name} • {selectedTicket.category}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(selectedTicket.status)}
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(selectedTicket.priority)}`}>
                      {selectedTicket.priority}
                    </span>
                  </div>
                </div>
              </div>

              {/* 訊息列表 */}
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="space-y-4">
                  {selectedTicket.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_type === 'admin' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.sender_type === 'admin'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.sender_type === 'admin' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.sender} • {new Date(message.created_at).toLocaleString('zh-TW')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 回覆輸入 */}
              <div className="p-6 border-t">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="輸入回覆訊息..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage(selectedTicket.id)}
                  />
                  <button
                    onClick={() => sendMessage(selectedTicket.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    發送
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">選擇一個工單查看詳情</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketCenter;