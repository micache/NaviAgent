"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import "@/styles/itinerary-detail.css";
import ReactMarkdown from "react-markdown";

interface TravelPlan {
  id: string;
  travel_data: {
    destination: string;
    departure_point: string;
    departure_date: string;
    trip_duration: number;
    num_travelers: number;
    budget: number;
    travel_style: string;
    customer_notes?: string;
  };
  plan: {
    itinerary?: any;
    accommodation?: any;
    flights?: any;
    budget_breakdown?: any;
    souvenirs?: any;
    travel_advisory?: any;
  };
  created_at: string;
}

export default function ItineraryDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [plan, setPlan] = useState<TravelPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("itinerary");

  useEffect(() => {
    if (id) {
      loadPlanDetail(id);
    }
  }, [id]);

  const loadPlanDetail = (planId: string) => {
    try {
      const savedPlan = localStorage.getItem(`travel_plan_${planId}`);
      if (savedPlan) {
        setPlan(JSON.parse(savedPlan));
      } else {
        alert("Không tìm thấy lịch trình!");
        router.push('/itinerary');
      }
    } catch (error) {
      console.error("Error loading plan:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('vi-VN', { 
      style: 'currency', 
      currency: 'VND' 
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const tabs = [
    { id: 'itinerary', label: '📅 Lịch trình', icon: '📅' },
    { id: 'accommodation', label: '🏨 Khách sạn', icon: '🏨' },
    { id: 'flights', label: '✈️ Chuyến bay', icon: '✈️' },
    { id: 'budget', label: '💰 Chi phí', icon: '💰' },
    { id: 'souvenirs', label: '🎁 Quà lưu niệm', icon: '🎁' },
    { id: 'advisory', label: '⚠️ Lưu ý', icon: '⚠️' },
  ];

  const renderContent = () => {
    if (!plan?.plan) return <p>Không có dữ liệu</p>;

    switch(activeTab) {
      case 'itinerary':
        return <ReactMarkdown>{plan.plan.itinerary || 'Chưa có lịch trình'}</ReactMarkdown>;
      case 'accommodation':
        return <ReactMarkdown>{plan.plan.accommodation || 'Chưa có thông tin khách sạn'}</ReactMarkdown>;
      case 'flights':
        return <ReactMarkdown>{plan.plan.flights || 'Chưa có thông tin chuyến bay'}</ReactMarkdown>;
      case 'budget':
        return <ReactMarkdown>{plan.plan.budget_breakdown || 'Chưa có phân tích chi phí'}</ReactMarkdown>;
      case 'souvenirs':
        return <ReactMarkdown>{plan.plan.souvenirs || 'Chưa có gợi ý quà'}</ReactMarkdown>;
      case 'advisory':
        return <ReactMarkdown>{plan.plan.travel_advisory || 'Chưa có lưu ý đặc biệt'}</ReactMarkdown>;
      default:
        return <p>Tab không hợp lệ</p>;
    }
  };

  if (isLoading) {
    return (
      <div className="itinerary-detail-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Đang tải...</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="itinerary-detail-container">
        <div className="error-state">
          <h2>❌ Không tìm thấy lịch trình</h2>
          <button onClick={() => router.push('/itinerary')}>
            ← Quay lại danh sách
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="itinerary-detail-container">
      {/* Header with travel info */}
      <div className="detail-header">
        <button className="back-button" onClick={() => router.push('/itinerary')}>
          ← Quay lại
        </button>
        
        <div className="header-content">
          <h1>🗺️ {plan.travel_data.destination}</h1>
          <div className="header-info">
            <span>📍 Từ: {plan.travel_data.departure_point}</span>
            <span>📅 Khởi hành: {formatDate(plan.travel_data.departure_date)}</span>
            <span>⏱️ {plan.travel_data.trip_duration} ngày</span>
            <span>👥 {plan.travel_data.num_travelers} người</span>
            <span>💰 {formatCurrency(plan.travel_data.budget)}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="content-container">
        <div className="markdown-content">
          {renderContent()}
        </div>
      </div>

      {/* Actions */}
      <div className="action-buttons">
        <button className="btn-secondary" onClick={() => router.push('/itinerary')}>
          📋 Danh sách lịch trình
        </button>
        <button className="btn-primary" onClick={() => window.print()}>
          🖨️ In lịch trình
        </button>
      </div>
    </div>
  );
}
