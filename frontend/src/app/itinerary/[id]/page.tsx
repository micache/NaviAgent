"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import "@/styles/itinerary-detail.css";

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
  plan: any; // Full travel plan JSON
  guidebook_id?: string; // Guidebook ID from plan creation
  guidebook_files?: { [key: string]: string }; // Guidebook file paths
  created_at: string;
}

const TRAVEL_PLANNER_API = process.env.NEXT_PUBLIC_TRAVEL_PLANNER_API_URL || "http://localhost:8003";

export default function ItineraryDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [plan, setPlan] = useState<TravelPlan | null>(null);
  const [guidebookHtml, setGuidebookHtml] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingGuidebook, setIsGeneratingGuidebook] = useState(false);

  useEffect(() => {
    if (id) {
      loadPlanDetail(id);
    }
  }, [id]);

  const loadPlanDetail = async (planId: string) => {
    try {
      const savedPlan = localStorage.getItem(`travel_plan_${planId}`);
      if (savedPlan) {
        const planData = JSON.parse(savedPlan);
        setPlan(planData);
        
        // Check if guidebook already exists
        if (planData.guidebook_id && planData.guidebook_files?.html) {
          console.log("📚 Guidebook already exists, loading...");
          console.log("  - Guidebook ID:", planData.guidebook_id);
          await loadExistingGuidebook(planData.guidebook_id);
        } else {
          console.log("📚 No guidebook found, generating new one...");
          await generateGuidebook(planData.plan, planId);
        }
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

  const loadExistingGuidebook = async (guidebookId: string) => {
    setIsGeneratingGuidebook(true);
    try {
      
      const downloadUrl = `${TRAVEL_PLANNER_API}/v1/guidebook/${guidebookId}/download?format=html`;
      console.log("📥 Loading existing guidebook HTML from:", downloadUrl);
      const htmlResponse = await fetch(downloadUrl);
      
      console.log("📡 Download response status:", htmlResponse.status);
        
      if (htmlResponse.ok) {
        const htmlContent = await htmlResponse.text();
        setGuidebookHtml(htmlContent);
        console.log("✅ Guidebook loaded successfully");
      } else {
        const errorText = await htmlResponse.text();
        console.error("❌ Failed to load guidebook:", htmlResponse.status, errorText);
        throw new Error(`Failed to load guidebook: ${htmlResponse.status}`);
      }
    } catch (error) {
      console.error("❌ Error loading guidebook:", error);
      setGuidebookHtml("<p style='color: red;'>Lỗi khi tải guidebook. Vui lòng tải lại trang.</p>");
    } finally {
      setIsGeneratingGuidebook(false);
    }
  };

  const generateGuidebook = async (travelPlanData: any, planId: string) => {
    setIsGeneratingGuidebook(true);
    try {  
      const generateUrl = `${TRAVEL_PLANNER_API}/v1/generate_guidebook`;
      console.log("📚 Generating new guidebook...");
      console.log("📡 API URL:", generateUrl);
      
      const response = await fetch(generateUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          travel_plan: travelPlanData,
          formats: ["html"],
          language: "vi"
        }),
      });

      console.log("📡 Generate response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Generate failed:", response.status, errorText);
        throw new Error(`Failed to generate guidebook: ${response.status}`);
      }

      const guidebookResponse = await response.json();
      console.log("✅ Guidebook generated:", guidebookResponse);

      // Update localStorage with guidebook info
      const savedPlan = localStorage.getItem(`travel_plan_${planId}`);
      if (savedPlan) {
        const planData = JSON.parse(savedPlan);
        planData.guidebook_id = guidebookResponse.guidebook_id;
        planData.guidebook_files = guidebookResponse.files || {};
        localStorage.setItem(`travel_plan_${planId}`, JSON.stringify(planData));
        console.log("💾 Updated plan with guidebook info");
      }

      // Fetch the HTML file content
      if (guidebookResponse.files?.html) {
        const downloadUrl = `${TRAVEL_PLANNER_API}/v1/guidebook/${guidebookResponse.guidebook_id}/download?format=html`;
        console.log("📥 Downloading HTML from:", downloadUrl);
        const htmlResponse = await fetch(downloadUrl);
        
        console.log("📡 HTML download status:", htmlResponse.status);
        
        if (htmlResponse.ok) {
          const htmlContent = await htmlResponse.text();
          setGuidebookHtml(htmlContent);
          console.log("✅ HTML content loaded");
        } else {
          const errorText = await htmlResponse.text();
          console.error("❌ HTML download failed:", htmlResponse.status, errorText);
        }
      }
    } catch (error) {
      console.error("❌ Error generating guidebook:", error);
      setGuidebookHtml("<p style='color: red;'>Lỗi khi tạo guidebook. Vui lòng thử lại.</p>");
    } finally {
      setIsGeneratingGuidebook(false);
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

      {/* Guidebook Content */}
      <div className="content-container">
        {isGeneratingGuidebook ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Đang tạo guidebook...</p>
          </div>
        ) : guidebookHtml ? (
          <div 
            className="guidebook-content"
            dangerouslySetInnerHTML={{ __html: guidebookHtml }}
          />
        ) : (
          <div className="empty-state">
            <p>Chưa có guidebook</p>
          </div>
        )}
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
