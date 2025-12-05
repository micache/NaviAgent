"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import "@/styles/itinerary.css";
import { useLanguage } from "@/contexts/LanguageContext";

interface SavedItinerary {
  id: string;
  destination: string;
  departure_date: string;
  trip_duration: number;
  num_travelers: number;
  budget: number;
  created_at: string;
}

export default function ItineraryListPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [itineraries, setItineraries] = useState<SavedItinerary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadItineraries();
  }, []);

  const loadItineraries = () => {
    try {
      // Load từ localStorage
      const savedPlans = localStorage.getItem('travel_plans_list');
      if (savedPlans) {
        const plans = JSON.parse(savedPlans);
        setItineraries(plans);
      }
    } catch (error) {
      console.error("Error loading itineraries:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewItinerary = (id: string) => {
    router.push(`/itinerary/${id}`);
  };

  const handleDeleteItinerary = (id: string) => {
    if (confirm("Bạn có chắc muốn xóa lịch trình này?")) {
      const updatedPlans = itineraries.filter(plan => plan.id !== id);
      localStorage.setItem('travel_plans_list', JSON.stringify(updatedPlans));
      setItineraries(updatedPlans);
      
      // Xóa chi tiết plan
      localStorage.removeItem(`travel_plan_${id}`);
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

  if (isLoading) {
    return (
      <div className="itinerary-list-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="itinerary-list-container">
      <div className="itinerary-list-header">
        <h1>📋 Lịch trình đã tạo</h1>
        <p className="subtitle">Xem lại các chuyến đi bạn đã lên kế hoạch</p>
      </div>

      {itineraries.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🗺️</div>
          <h2>Chưa có lịch trình nào</h2>
          <p>Hãy bắt đầu tạo lịch trình cho chuyến đi của bạn!</p>
          <button 
            className="create-plan-btn"
            onClick={() => router.push('/plan')}
          >
            + Tạo lịch trình mới
          </button>
        </div>
      ) : (
        <div className="itinerary-grid">
          {itineraries.map((itinerary) => (
            <div key={itinerary.id} className="itinerary-card">
              <div className="card-header">
                <h3>{itinerary.destination}</h3>
                <span className="created-date">
                  {formatDate(itinerary.created_at)}
                </span>
              </div>
              
              <div className="card-body">
                <div className="info-row">
                  <span className="label">📅 Khởi hành:</span>
                  <span className="value">{formatDate(itinerary.departure_date)}</span>
                </div>
                <div className="info-row">
                  <span className="label">⏱️ Thời gian:</span>
                  <span className="value">{itinerary.trip_duration} ngày</span>
                </div>
                <div className="info-row">
                  <span className="label">👥 Số người:</span>
                  <span className="value">{itinerary.num_travelers} người</span>
                </div>
                <div className="info-row">
                  <span className="label">💰 Ngân sách:</span>
                  <span className="value">{formatCurrency(itinerary.budget)}</span>
                </div>
              </div>
              
              <div className="card-actions">
                <button 
                  className="view-btn"
                  onClick={() => handleViewItinerary(itinerary.id)}
                >
                  👁️ Xem chi tiết
                </button>
                <button 
                  className="delete-btn"
                  onClick={() => handleDeleteItinerary(itinerary.id)}
                >
                  🗑️ Xóa
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
