"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import sendIcon from "@/images/send.svg";
import "@/styles/plan.css";
import { useLanguage } from "@/contexts/LanguageContext";
import ReactMarkdown from "react-markdown";

const RECEPTION_API_URL = process.env.NEXT_PUBLIC_RECEPTION_API_URL || "http://localhost:8002";

interface Message {
  role: string;
  content: string;
}

interface TravelData {
  destination?: string;
  departure_point?: string;
  departure_date?: string;
  trip_duration?: string;
  num_travelers?: string;
  budget?: string;
  travel_style?: string;
  customer_notes?: string;
}

export default function PlanPage() {
  const { t } = useLanguage();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [travelData, setTravelData] = useState<TravelData>({});
  const [isComplete, setIsComplete] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem("user");
    setIsAuthenticated(!!token);
    console.log("🔐 Authentication status:", !!token);
  }, []);

  const handleSendChat = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    console.log("📤 Send chat triggered");
    console.log("💬 Chat input:", chatInput);
    console.log("🆔 Session ID:", sessionId);
    
    if (!chatInput.trim()) {
      console.warn("⚠️ Empty message");
      return;
    }
    
    if (isLoading) {
      console.warn("⚠️ Already loading");
      return;
    }
    
    // Check authentication
    const token = localStorage.getItem("user");
    if (!token) {
      console.error("❌ Not authenticated");
      setMessages([{ role: "assistant", content: "Please sign in to start planning your trip." }]);
      return;
    }

    const user = JSON.parse(token);
    const userMessage = chatInput.trim();
    console.log("✅ Sending message:", userMessage);
    
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setChatInput("");
    setIsLoading(true);

    try {
      // If no session, create one first
      if (!sessionId) {
        console.log("🆕 Creating new session...");
        console.log("👤 User object:", user);
        
        const userId = user.user_id;
        console.log("🆔 Using user_id:", userId);
        
        const startResponse = await fetch(`${RECEPTION_API_URL}/start_chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ user_id: userId }),
        });

        console.log("📡 Start chat response status:", startResponse.status);

        if (!startResponse.ok) {
          const errorText = await startResponse.text();
          console.error("❌ Start chat failed:", errorText);
          throw new Error(`Failed to start chat session: ${errorText}`);
        }

        const startData = await startResponse.json();
        console.log("✅ Start chat response:", startData);
        const newSessionId = startData.session_id;
        setSessionId(newSessionId);
        console.log("✅ Session created:", newSessionId);
        console.log("💬 Greeting:", startData.message);
        
        // Add greeting to messages
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: startData.message }
        ]);

        // Now send the user's message with the new session
        console.log("🔗 Sending user message with new session...");
        const chatResponse = await fetch(`${RECEPTION_API_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            session_id: newSessionId,
            message: userMessage 
          }),
        });

        if (!chatResponse.ok) {
          throw new Error("Failed to send message");
        }

        const chatData = await chatResponse.json();
        console.log("📋 Travel Data Updated:", chatData.travel_data);
        console.log("✅ Is Complete:", chatData.is_complete);
        
        setMessages((prev) => [...prev, { role: "assistant", content: chatData.message }]);
        setTravelData(chatData.travel_data || {});
        setIsComplete(chatData.is_complete || false);
        
        if (chatData.is_complete) {
          console.log("🎉 Travel data collection complete!");
          console.log("📦 Final travel data:", chatData.travel_data);
        }
      } else {
        // Session exists, just send message
        console.log("🔗 Calling API with existing session:", `${RECEPTION_API_URL}/chat`);
        const response = await fetch(`${RECEPTION_API_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            session_id: sessionId,
            message: userMessage 
          }),
        });

        console.log("📡 API Response status:", response.status);

        if (!response.ok) {
          throw new Error("Failed to send message");
        }

        const data = await response.json();
        
        // Log travel data for debugging
        console.log("📋 Travel Data Updated:", data.travel_data);
        console.log("✅ Is Complete:", data.is_complete);
        
        setMessages((prev) => [...prev, { role: "assistant", content: data.message }]);
        setTravelData(data.travel_data || {});
        setIsComplete(data.is_complete || false);
        
        // Log completion
        if (data.is_complete) {
          console.log("🎉 Travel data collection complete!");
          console.log("📦 Final travel data:", data.travel_data);
        }
      }
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, there was an error. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
      console.log("✅ Chat request completed");
    }
  };

  // Format budget with VND
  const formatBudget = (budget?: string) => {
    if (!budget) return "—";
    const num = parseInt(budget);
    if (isNaN(num)) return budget;
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num);
  };

  // Format travel style
  const formatTravelStyle = (style?: string) => {
    if (!style) return "—";
    if (style === "self-guided") return "Tự túc";
    if (style === "tour") return "Tour";
    return style;
  };

  // Handle create itinerary
  const handleCreateItinerary = () => {
    console.log("🚀 Creating itinerary with travel data:");
    console.log(JSON.stringify(travelData, null, 2));
    
    // TODO: Call travel planner API with travelData
    alert("Tính năng tạo lịch trình đang được phát triển!\n\nTravel Data:\n" + JSON.stringify(travelData, null, 2));
  };

  return (
    <section className="plan-layout">
      {/* ===== LEFT: Travel Data Summary ===== */}
      <div className="plan-left">
        <h1 className="plan-title">{t("travelPlans")}</h1>
        <p className="plan-subtext">
          {t("managePlans")}
        </p>

        {isComplete && (
          <div className="plan-complete-banner">
            <div className="banner-content">
              <span className="banner-text">{t("planComplete")}</span>
              <button className="create-itinerary-btn" onClick={handleCreateItinerary}>
                🗓️ Tạo lịch trình
              </button>
            </div>
          </div>
        )}

        <div className="travel-data-summary">
          <h3>{t("travelInfo")}</h3>
          <div className="travel-data-grid">
            <div className="travel-data-item">
              <strong>{t("destination")}:</strong>
              <span>{travelData.destination || "—"}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("departurePoint")}:</strong>
              <span>{travelData.departure_point || "—"}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("departureDate")}:</strong>
              <span>{travelData.departure_date || "—"}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("duration")}:</strong>
              <span>{travelData.trip_duration || "—"}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("travelers")}:</strong>
              <span>{travelData.num_travelers || "—"}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("budget")}:</strong>
              <span>{formatBudget(travelData.budget)}</span>
            </div>
            <div className="travel-data-item">
              <strong>{t("travelStyle")}:</strong>
              <span>{formatTravelStyle(travelData.travel_style)}</span>
            </div>
            {travelData.customer_notes && (
              <div className="travel-data-item travel-data-notes">
                <strong>{t("notes") || "Ghi chú"}:</strong>
                <span>{travelData.customer_notes}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ===== RIGHT: Chatbot Assistant ===== */}
      <div className="plan-right">
        <div className="chat-header">
          <h2>{t("tripPlanner")}</h2>
          <p>{t("tripPlannerDesc")}</p>
          {sessionId && (
            <div className="session-indicator">
              <span className="status-dot"></span>
              <span className="status-text">Connected</span>
            </div>
          )}
        </div>

        {/* Chat messages area */}
        <div className="chat-messages">
          {!isAuthenticated && messages.length === 0 && (
            <div className="auth-prompt">
              <h3>🔐 {t("signIn")} / {t("signUp")}</h3>
              <p>Please sign in to start planning your trip with our AI assistant.</p>
              <p>Vui lòng đăng nhập để bắt đầu lên kế hoạch chuyến đi với trợ lý AI của chúng tôi.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <ReactMarkdown
                components={{
                  p: ({children}) => <span>{children}</span>,
                  strong: ({children}) => <strong>{children}</strong>,
                  br: () => <br />,
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant">
              <span className="loading-dots">...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat input */}
        <div className="chat-input-container">
          <form className="chat-input-row" onSubmit={handleSendChat}>
            <input
              type="text"
              className="chat-input"
              placeholder={isAuthenticated ? t("typeQuestion") : "Please sign in to chat / Vui lòng đăng nhập để chat"}
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="chat-send-btn" 
              title={t("send")}
              disabled={isLoading}
            >
              <Image src={sendIcon} alt="Send" width={24} height={24} />
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
