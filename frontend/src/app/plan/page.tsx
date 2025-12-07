"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
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

interface SessionItem {
  session_id: string;
  user_id: string;
  created_at: string;
  update_at: string;
  title?: string;
}

export default function PlanPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [travelData, setTravelData] = useState<TravelData>({});
  const [isComplete, setIsComplete] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Sidebar states
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem("user");
    setIsAuthenticated(!!token);
    console.log("🔐 Authentication status:", !!token);
    
    // Load sessions when authenticated and auto-load latest session
    if (token) {
      loadUserSessions();
    }
  }, []);

  // Load user sessions
  const loadUserSessions = async () => {
    try {
      const token = localStorage.getItem("user");
      if (!token) return;

      const user = JSON.parse(token);
      const userId = user.user_id;

      setLoadingSessions(true);
      const response = await fetch(`${RECEPTION_API_URL}/sessions/${userId}`);
      
      if (response.ok) {
        const data = await response.json();
        // Map 'id' from database to 'session_id' for frontend
        const mappedSessions = (data.sessions || []).map((session: any) => ({
          session_id: session.id, // Map 'id' to 'session_id'
          user_id: session.user_id,
          created_at: session.created_at,
          update_at: session.update_at,
          title: session.title
        }));
        setSessions(mappedSessions);
        console.log("📋 Loaded sessions:", mappedSessions);
        
        // Auto-load the latest session if exists and no current session
        if (mappedSessions.length > 0 && !sessionId) {
          const latestSession = mappedSessions[0]; // Sessions are ordered by created_at DESC
          console.log("🔄 Auto-loading latest session:", latestSession.session_id);
          await loadSessionMessages(latestSession.session_id);
        }
      }
    } catch (error) {
      console.error("❌ Error loading sessions:", error);
    } finally {
      setLoadingSessions(false);
    }
  };

  // Load a specific session's messages
  const loadSessionMessages = async (selectedSessionId: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${RECEPTION_API_URL}/sessions/${selectedSessionId}/messages`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Map messages from API response
        const loadedMessages = (data.messages || []).map((msg: any) => ({
          role: msg.role === "user" ? "user" : "assistant",
          content: msg.content
        }));
        
        setMessages(loadedMessages);
        setSessionId(selectedSessionId);
        
        // Update travel_data from API response
        if (data.travel_data) {
          setTravelData(data.travel_data);
          setIsComplete(data.is_complete || false);
          
          console.log("📋 Travel data loaded:", data.travel_data);
          console.log("✅ Is complete:", data.is_complete);
        } else {
          setTravelData({});
          setIsComplete(false);
        }
        
        console.log("💬 Loaded messages for session:", selectedSessionId);
      }
    } catch (error) {
      console.error("❌ Error loading session messages:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Create new chat session
  const handleNewChat = async () => {
    try {
      const token = localStorage.getItem("user");
      if (!token) {
        alert("Please sign in first!");
        return;
      }

      const user = JSON.parse(token);
      const userId = user.user_id;

      setIsLoading(true);
      const response = await fetch(`${RECEPTION_API_URL}/start_chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setMessages([{ role: "assistant", content: data.message }]);
        setTravelData({});
        setIsComplete(false);
        
        // Reload sessions list
        await loadUserSessions();
        
        console.log("✅ New chat session created:", data.session_id);
      }
    } catch (error) {
      console.error("❌ Error creating new chat:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Removed auto-start chat session - now loads latest session instead

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

  // Mock data for testing
  const handleMockData = () => {
    const mockData: TravelData = {
      destination: "Ho Chi Minh City, Vietnam",
      departure_point: "Ha Noi, Vietnam",
      departure_date: "2025-12-07",
      trip_duration: "2",
      num_travelers: "2",
      budget: "100000000",
      travel_style: "self-guided",
      customer_notes: "Tìm hiểu ẩm thực địa phương và tham quan các điểm lịch sử."
    };
    setTravelData(mockData);
    setIsComplete(true);
    setMessages([{ role: "assistant", content: "✅ Mock data loaded! You can now create itinerary." }]);
  };

  // Handle create itinerary
  const handleCreateItinerary = async () => {
    console.log("🚀 Creating itinerary with travel data:");
    console.log(JSON.stringify(travelData, null, 2));
    
    setIsLoading(true);
    
    try {
      // Call travel planner API
      const PLANNER_API_URL = "http://localhost:8003";
      
      // Prepare data according to travel_planner schema
      const plannerRequest = {
        departure_point: travelData.departure_point,
        destination: travelData.destination,
        departure_date: travelData.departure_date,
        trip_duration: parseInt(travelData.trip_duration || "1"),
        num_travelers: parseInt(travelData.num_travelers || "1"),
        budget: parseFloat(travelData.budget || "0"),
        travel_style: travelData.travel_style === "self-guided" ? "self_guided" : travelData.travel_style,
        customer_notes: travelData.customer_notes || ""
      };
      
      console.log("📤 Sending to travel planner:", plannerRequest);
      
      const response = await fetch(`${PLANNER_API_URL}/v1/plan_trip`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(plannerRequest),
      });
      
      if (!response.ok) {
        const errorDetail = await response.json().catch(() => null);
        console.error("❌ API Error:", errorDetail);
        throw new Error(`Travel planner API error: ${response.status} - ${JSON.stringify(errorDetail)}`);
      }
      
      const planResult = await response.json();
      console.log("✅ Received plan from travel planner:", planResult);
      
      // 📚 STEP 2: Generate guidebook immediately after receiving travel plan
      console.log("📚 Step 2: Generating guidebook from travel plan...");
      let guidebookId = null;
      let guidebookFiles = {};
      
      try {
        const guidebookResponse = await fetch(`${PLANNER_API_URL}/api/v1/generate_guidebook`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            travel_plan: planResult,
            formats: ["html"],
            language: "vi"
          }),
        });

        if (guidebookResponse.ok) {
          const guidebookData = await guidebookResponse.json();
          guidebookId = guidebookData.guidebook_id;
          guidebookFiles = guidebookData.files || {};
          console.log("✅ Guidebook generated successfully!");
          console.log("  - Guidebook ID:", guidebookId);
          console.log("  - Files:", guidebookFiles);
        } else {
          console.warn("⚠️ Guidebook generation failed, will retry on detail page");
        }
      } catch (guidebookError) {
        console.warn("⚠️ Guidebook generation error:", guidebookError);
      }
      
      // Save to localStorage with guidebook info
      const planId = Date.now().toString();
      const completePlan = {
        id: planId,
        travel_data: travelData,
        plan: planResult,
        guidebook_id: guidebookId,
        guidebook_files: guidebookFiles,
        created_at: new Date().toISOString()
      };
      
      // Save detail
      localStorage.setItem(`travel_plan_${planId}`, JSON.stringify(completePlan));
      
      // Update list
      const existingPlans = JSON.parse(localStorage.getItem('travel_plans_list') || '[]');
      existingPlans.push({
        id: planId,
        destination: travelData.destination,
        departure_date: travelData.departure_date,
        trip_duration: parseInt(travelData.trip_duration || "1"),
        num_travelers: parseInt(travelData.num_travelers || "1"),
        budget: parseInt(travelData.budget || "0"),
        created_at: new Date().toISOString()
      });
      localStorage.setItem('travel_plans_list', JSON.stringify(existingPlans));
      
      console.log("💾 Plan saved to localStorage with ID:", planId);
      
      // Navigate to detail page
      router.push(`/itinerary/${planId}`);
      
    } catch (error) {
      console.error("❌ Error creating itinerary:", error);
      alert("Không thể tạo lịch trình. Vui lòng thử lại!");
    } finally {
      setIsLoading(false);
    }
    alert("Tính năng tạo lịch trình đang được phát triển!\n\nTravel Data:\n" + JSON.stringify(travelData, null, 2));
  };

  return (
    <section className="plan-layout">
      {/* ===== SIDEBAR: Chat Sessions ===== */}
      <div className={`chat-sidebar ${isSidebarOpen ? 'open' : 'collapsed'}`}>
        <div className="sidebar-header">
          <button 
            className="sidebar-toggle"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            title={isSidebarOpen ? "Collapse" : "Expand"}
          >
            {isSidebarOpen ? '◀' : '▶'}
          </button>
          {isSidebarOpen && (
            <button 
              className="new-chat-btn"
              onClick={handleNewChat}
              disabled={isLoading}
            >
              ➕ New Chat
            </button>
          )}
        </div>

        {isSidebarOpen && (
          <div className="sessions-list">
            {loadingSessions ? (
              <div className="loading-sessions">Loading...</div>
            ) : sessions.length === 0 ? (
              <div className="no-sessions">No chat history</div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`session-item ${session.session_id === sessionId ? 'active' : ''}`}
                  onClick={() => loadSessionMessages(session.session_id)}
                >
                  <div className="session-title">
                    💬 {session.title || `Chat ${new Date(session.update_at).toLocaleDateString()}`}
                  </div>
                  <div className="session-date">
                    {new Date(session.update_at).toLocaleString('vi-VN', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

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
                Tạo lịch trình
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
          {/* Test buttons */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
            <button 
              onClick={handleMockData}
              style={{
                padding: '8px 16px',
                background: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🧪 Load Mock Data
            </button>
          </div>
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
