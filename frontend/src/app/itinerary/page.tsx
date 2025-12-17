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

const NAVIAGENT_API = process.env.NEXT_PUBLIC_NAVIAGENT_API_URL || "http://localhost:8001";

export default function ItineraryListPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [itineraries, setItineraries] = useState<SavedItinerary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadItineraries();
  }, []);

  const loadItineraries = async () => {
    try {
      console.log("🔍 Loading itineraries...");
      
      // Try loading from database first (if user is authenticated)
      const token = sessionStorage.getItem("user");
      let plans: SavedItinerary[] = [];
      
      if (token) {
        try {
          const user = JSON.parse(token);
          console.log("👤 User authenticated, loading from database...");
          
          const response = await fetch(`${NAVIAGENT_API}/plans`, {
            headers: {
              "Authorization": `Bearer ${user.access_token}`
            }
          });
          
          if (response.ok) {
            const dbPlans = await response.json();
            console.log("✅ Loaded plans from database:", dbPlans.length);
            
            // Transform database plans to SavedItinerary format
            plans = dbPlans.map((dbPlan: any) => ({
              id: dbPlan.id,
              destination: dbPlan.destination,
              departure_date: dbPlan.start_date,
              trip_duration: dbPlan.duration,
              num_travelers: dbPlan.number_of_travelers,
              budget: dbPlan.budget || 0,
              created_at: dbPlan.start_date // Use start_date as created_at fallback
            }));
            
            setItineraries(plans);
            setIsLoading(false);
            return; // Exit early if database load successful
          } else {
            console.log("⚠️ Failed to load from database:", response.status);
          }
        } catch (dbError) {
          console.error("⚠️ Database load error:", dbError);
        }
      } else {
        console.log("⚠️ User not authenticated, skipping database load");
      }
      
      // Fallback to localStorage if database load failed
      console.log("💾 Falling back to localStorage...");
      const savedPlans = localStorage.getItem('travel_plans_list');
      if (savedPlans) {
        plans = JSON.parse(savedPlans);
        console.log("✅ Loaded plans from localStorage:", plans.length);
        setItineraries(plans);
      } else {
        console.log("ℹ️ No plans found in localStorage");
        setItineraries([]);
      }
    } catch (error) {
      console.error("❌ Error loading itineraries:", error);
      setItineraries([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewItinerary = (id: string) => {
    router.push(`/itinerary/${id}`);
  };

  const handleDeleteItinerary = async (id: string) => {
    if (!confirm(t("confirmDelete"))) {
      return;
    }
    
    try {
      console.log("🗑️ Deleting itinerary:", id);
      
      // Check if this is a mock plan
      const isMockPlan = id.startsWith('mock_');
      
      // Try deleting from database first (if authenticated and NOT a mock plan)
      const token = sessionStorage.getItem("user");
      let deletedFromDB = false;
      
      if (token && !isMockPlan) {
        try {
          const user = JSON.parse(token);
          console.log("👤 Deleting from database...");
          
          const response = await fetch(`${NAVIAGENT_API}/plans/${id}`, {
            method: "DELETE",
            headers: {
              "Authorization": `Bearer ${user.access_token}`
            }
          });
          
          if (response.ok || response.status === 204) {
            console.log("✅ Deleted from database");
            deletedFromDB = true;
          } else if (response.status === 404) {
            console.log("ℹ️ Plan not found in database (may be localStorage only)");
          } else {
            console.log("⚠️ Failed to delete from database:", response.status);
          }
        } catch (dbError) {
          console.error("⚠️ Database delete error:", dbError);
        }
      } else if (isMockPlan) {
        console.log("🧪 Mock plan detected, skipping database deletion");
      }
      
      // Also delete from localStorage (regardless of database result)
      console.log("💾 Deleting from localStorage...");
      const updatedPlans = itineraries.filter(plan => plan.id !== id);
      localStorage.setItem('travel_plans_list', JSON.stringify(updatedPlans));
      localStorage.removeItem(`travel_plan_${id}`);
      
      setItineraries(updatedPlans);
      console.log("✅ Itinerary deleted successfully");
      
      if (deletedFromDB) {
        alert(t("deleteSuccessDB"));
      } else if (isMockPlan) {
        alert(t("deleteSuccessMock"));
      } else {
        alert(t("deleteSuccessLocal"));
      }
    } catch (error) {
      console.error("❌ Error deleting itinerary:", error);
      alert(t("deleteError"));
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
          <p>{t("loading")}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="itinerary-list-container">
      <div className="itinerary-list-header">
        <h1>{t("createdItineraries")}</h1>
        <p className="subtitle">{t("reviewItineraries")}</p>
      </div>

      {itineraries.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🗺️</div>
          <h2>{t("noItineraries")}</h2>
          <p>{t("startCreating")}</p>
          <button 
            className="create-plan-btn"
            onClick={() => router.push('/plan')}
          >
            {t("createNewItinerary")}
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
                  <span className="label">{t("departureLabel")}</span>
                  <span className="value">{formatDate(itinerary.departure_date)}</span>
                </div>
                <div className="info-row">
                  <span className="label">{t("durationLabel")}</span>
                  <span className="value">{itinerary.trip_duration} {t("days")}</span>
                </div>
                <div className="info-row">
                  <span className="label">{t("travelersLabel")}</span>
                  <span className="value">{itinerary.num_travelers} {t("people")}</span>
                </div>
                <div className="info-row">
                  <span className="label">{t("budgetLabel")}</span>
                  <span className="value">{formatCurrency(itinerary.budget)}</span>
                </div>
              </div>
              
              <div className="card-actions">
                <button 
                  className="view-btn"
                  onClick={() => handleViewItinerary(itinerary.id)}
                >
                  {t("viewDetails")}
                </button>
                <button 
                  className="delete-btn"
                  onClick={() => handleDeleteItinerary(itinerary.id)}
                >
                  {t("delete")}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
