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
const NAVIAGENT_API = process.env.NEXT_PUBLIC_NAVIAGENT_API_URL || "http://localhost:8001";

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
      console.log("🔍 Loading plan:", planId);
      
      // Check if this is a mock plan (starts with "mock_")
      const isMockPlan = planId.startsWith('mock_');
      
      // Try loading from database first (if user is authenticated and NOT a mock plan)
      const token = localStorage.getItem("user");
      let planData = null;
      
      if (token && !isMockPlan) {
        try {
          const user = JSON.parse(token);
          console.log("👤 User authenticated, loading from database...");
          
          const response = await fetch(`${NAVIAGENT_API}/plans/${planId}`, {
            headers: {
              "Authorization": `Bearer ${user.access_token}`
            }
          });
          
          if (response.ok) {
            const dbPlan = await response.json();
            console.log("✅ Loaded plan from database:", dbPlan);
            
            // Transform database plan to TravelPlan format
            planData = {
              id: dbPlan.id,
              travel_data: {
                destination: dbPlan.destination,
                departure_point: dbPlan.departure,
                departure_date: dbPlan.start_date,
                trip_duration: dbPlan.duration,
                num_travelers: dbPlan.number_of_travelers,
                budget: dbPlan.budget,
                travel_style: dbPlan.travel_style,
                customer_notes: dbPlan.notes
              },
              plan: null, // Not stored in DB
              guidebook_id: undefined,
              guidebook_files: undefined,
              created_at: new Date().toISOString()
            };
            
            setPlan(planData);
            
            // Load guidebook HTML from database (guidebook field contains URL or HTML)
            if (dbPlan.guidebook) {
              console.log("📚 Guidebook found in database");
              
              // Check if it's a URL or HTML content
              if (dbPlan.guidebook.startsWith('http')) {
                // It's a Storage URL - fetch the content
                console.log("📥 Fetching guidebook from Storage URL:", dbPlan.guidebook);
                const htmlResponse = await fetch(dbPlan.guidebook);
                if (htmlResponse.ok) {
                  const htmlContent = await htmlResponse.text();
                  setGuidebookHtml(htmlContent);
                  console.log("✅ Guidebook loaded from Storage");
                } else {
                  console.error("❌ Failed to fetch guidebook from Storage");
                  setGuidebookHtml("<p style='color: red;'>Lỗi khi tải guidebook từ Storage.</p>");
                }
              } else {
                // It's HTML content directly
                console.log("📄 Using guidebook HTML from database");
                setGuidebookHtml(dbPlan.guidebook);
              }
              
              setIsLoading(false);
              return; // Exit early, we have everything we need
            } else {
              console.log("⚠️ No guidebook in database");
            }
          } else {
            console.log("⚠️ Failed to load from database:", response.status);
          }
        } catch (dbError) {
          console.error("⚠️ Database load error:", dbError);
        }
      } else {
        if (isMockPlan) {
          console.log("🧪 Mock plan detected, skipping database lookup");
        } else {
          console.log("⚠️ User not authenticated, skipping database load");
        }
      }
      
      // Fallback to localStorage if database load failed or no guidebook
      if (!planData) {
        console.log("💾 Falling back to localStorage...");
        const savedPlan = localStorage.getItem(`travel_plan_${planId}`);
        if (savedPlan) {
          planData = JSON.parse(savedPlan);
          setPlan(planData);
          console.log("✅ Loaded plan from localStorage");
        } else {
          console.error("❌ Plan not found in localStorage");
          alert("Không tìm thấy lịch trình!");
          router.push('/itinerary');
          return;
        }
      }
      
      // Check if guidebook already exists in localStorage data
      if (planData && planData.guidebook_id && planData.guidebook_files?.html) {
        console.log("📚 Guidebook exists in localStorage, loading...");
        console.log("  - Guidebook ID:", planData.guidebook_id);
        await loadExistingGuidebook(planData.guidebook_id);
      } else if (planData && planData.plan) {
        console.log("📚 No guidebook found, generating new one...");
        await generateGuidebook(planData.plan, planId, planData.travel_data);
      } else {
        console.log("⚠️ No travel plan data available for guidebook generation");
        setGuidebookHtml("<p style='color: orange;'>Không có dữ liệu để tạo guidebook.</p>");
      }
    } catch (error) {
      console.error("❌ Error loading plan:", error);
      alert("Lỗi khi tải lịch trình!");
      router.push('/itinerary');
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

  const generateGuidebook = async (travelPlanData: any, planId: string, travelData?: TravelPlan["travel_data"]) => {
    setIsGeneratingGuidebook(true);
    try {  
      const generateUrl = `${TRAVEL_PLANNER_API}/v1/generate_guidebook`;
      console.log("📚 Generating new guidebook...");
      console.log("📡 API URL:", generateUrl);

      // Ensure trip_duration is present for guidebook generation
      const travelPlanForGuidebook = {
        ...travelPlanData,
        trip_duration: travelPlanData?.trip_duration || travelPlanData?.duration || travelData?.trip_duration,
        duration: travelPlanData?.duration || travelPlanData?.trip_duration || travelData?.trip_duration,
      };
      
      const response = await fetch(generateUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          travel_plan: travelPlanForGuidebook,
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
