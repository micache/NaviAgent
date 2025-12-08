"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import sendIcon from "@/images/send.svg";
import "@/styles/plan.css";
import { useLanguage } from "@/contexts/LanguageContext";
import ReactMarkdown from "react-markdown";

const RECEPTION_API_URL = process.env.NEXT_PUBLIC_RECEPTION_API_URL || "http://localhost:8002";
const TRAVEL_PLANNER_API_URL = process.env.NEXT_PUBLIC_TRAVEL_PLANNER_API_URL || "http://localhost:8003";
const NAVIAGENT_API_URL = process.env.NEXT_PUBLIC_NAVIAGENT_API_URL || "http://localhost:8001";

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

  // Handle create itinerary
  const handleCreateItinerary = async () => {
    console.log("🚀 Creating itinerary with travel data:");
    console.log(JSON.stringify(travelData, null, 2));
    
    setIsLoading(true);
    
    try {      
      // Convert date from DD/MM/YYYY to YYYY-MM-DD format
      let formattedDate = travelData.departure_date;
      if (formattedDate && formattedDate.includes('/')) {
        const [day, month, year] = formattedDate.split('/');
        formattedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        console.log("📅 Converted date format:", travelData.departure_date, "→", formattedDate);
      }
      
      // Prepare data according to travel_planner schema
      const plannerRequest = {
        departure_point: travelData.departure_point,
        destination: travelData.destination,
        departure_date: formattedDate,
        trip_duration: parseInt(travelData.trip_duration || "1"),
        num_travelers: parseInt(travelData.num_travelers || "1"),
        budget: parseFloat(travelData.budget || "0"),
        travel_style: travelData.travel_style === "self-guided" ? "self_guided" : travelData.travel_style,
        customer_notes: travelData.customer_notes || ""
      };
      
      console.log("📤 Sending to travel planner:", plannerRequest);
      
      const response = await fetch(`${TRAVEL_PLANNER_API_URL}/v1/plan_trip`, {
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
      let guidebookHtmlContent = "";
      
      try {
        const guidebookUrl = `${TRAVEL_PLANNER_API_URL}/v1/generate_guidebook`;
        console.log("📡 Calling guidebook API:", guidebookUrl);
        
        const guidebookResponse = await fetch(guidebookUrl, {
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

        console.log("📡 Guidebook response status:", guidebookResponse.status);
        
        if (guidebookResponse.ok) {
          const guidebookData = await guidebookResponse.json();
          guidebookId = guidebookData.guidebook_id;
          guidebookFiles = guidebookData.files || {};
          console.log("✅ Guidebook generated successfully!");
          console.log("  - Guidebook ID:", guidebookId);
          console.log("  - Files:", guidebookFiles);
          
          // Download HTML content for database storage
          if (guidebookId) {
            const downloadUrl = `${TRAVEL_PLANNER_API_URL}/v1/guidebook/${guidebookId}/download?format=html`;
            console.log("📥 Downloading HTML content from:", downloadUrl);
            const htmlResponse = await fetch(downloadUrl);
            
            if (htmlResponse.ok) {
              guidebookHtmlContent = await htmlResponse.text();
              console.log("✅ HTML content downloaded, length:", guidebookHtmlContent.length);
            }
          }
        } else {
          const errorText = await guidebookResponse.text();
          console.error("❌ Guidebook generation failed:", guidebookResponse.status, errorText);
        }
      } catch (guidebookError) {
        console.error("❌ Guidebook generation error:", guidebookError);
      }
      
      // 💾 STEP 3: Save to database (NaviAgent API)
      console.log("💾 Step 3: Saving plan to database...");
      let databasePlanId = null;
      
      try {
        const token = localStorage.getItem("user");
        console.log("🔑 Token exists:", !!token);
        
        if (token) {
          const user = JSON.parse(token);
          console.log("👤 User data:", {
            user_id: user.user_id,
            has_access_token: !!user.access_token
          });
          
          // Validate access token exists
          if (!user.access_token) {
            console.error("❌ No access token found in user data");
            alert("⚠️ Session expired. Please login again.");
            return;
          }
          
          const savePlanRequest = {
            destination: travelData.destination,
            departure: travelData.departure_point || "",
            start_date: formattedDate,
            duration: parseInt(travelData.trip_duration || "1"),
            number_of_travelers: parseInt(travelData.num_travelers || "1"),
            budget: parseInt(travelData.budget || "0"),
            travel_style: travelData.travel_style,
            notes: travelData.customer_notes || "",
            guidebook: guidebookHtmlContent // Save HTML content
          };
          
          console.log("📤 Saving plan to database:");
          console.log("  - API URL:", `${NAVIAGENT_API_URL}/plans`);
          console.log("  - Authorization header:", `Bearer ${user.access_token.substring(0, 20)}...`);
          console.log("  - Request data:", {
            ...savePlanRequest,
            guidebook: guidebookHtmlContent ? `[HTML content, ${guidebookHtmlContent.length} chars]` : null
          });
          
          const saveResponse = await fetch(`${NAVIAGENT_API_URL}/plans`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${user.access_token}`
            },
            body: JSON.stringify(savePlanRequest),
          });
          
          console.log("📡 Save response status:", saveResponse.status);
          
          if (saveResponse.ok) {
            const savedPlan = await saveResponse.json();
            databasePlanId = savedPlan.id;
            console.log("✅ Plan saved to database with ID:", databasePlanId);
            console.log("📋 Guidebook URL in Storage:", savedPlan.guidebook);
            alert("✅ Lịch trình đã được lưu vào database và Storage!");
          } else {
            const errorText = await saveResponse.text();
            console.error("❌ Failed to save to database:", saveResponse.status, errorText);
            alert(`⚠️ Không thể lưu vào database: ${saveResponse.status}\n${errorText}`);
            // Continue even if database save fails
          }
        } else {
          console.log("⚠️ User not authenticated, skipping database save");
          alert("⚠️ Bạn chưa đăng nhập, lịch trình chỉ lưu ở localStorage!");
        }
      } catch (dbError) {
        console.error("❌ Database save error:", dbError);
        alert(`❌ Lỗi khi lưu database: ${dbError}`);
        // Continue even if database save fails
      }
      
      // Save to localStorage with guidebook info (as backup)
      const planId = databasePlanId || Date.now().toString();
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
  };

  // 🧪 TEST GUIDEBOOK with mock data
  const handleTestGuidebook = async () => {
    console.log("🧪 Testing guidebook with mock data...");
    setIsLoading(true);
    
    try {
      // Load mock travel plan from JSON file in parent directory
      // Since file is at NaviAgent/travel_plan_output_1.json
      // We need to fetch from backend or use relative path
      
      // Option 1: Load from backend endpoint (if served)
      // Option 2: Import directly if copied to public
      
      console.log("📂 Loading mock data from parent directory...");
      
      // For now, use a mock data object directly
      const mockPlanResponse = await fetch('/travel_plan_output_1.json');
      
      if (!mockPlanResponse.ok) {
        console.error("❌ Failed to load from /travel_plan_output_1.json");
        console.log("💡 Please copy travel_plan_output_1.json to frontend/public/ folder");
        throw new Error("Failed to load mock data. Please copy travel_plan_output_1.json to frontend/public/ folder");
      }
      
      const mockPlan = await mockPlanResponse.json();
      console.log("✅ Loaded mock travel plan:", mockPlan);
      console.log("📋 Mock plan keys:", Object.keys(mockPlan));
      console.log("📋 Mock plan version:", mockPlan.version);
      
      const guidebookUrl = `${TRAVEL_PLANNER_API_URL}/v1/generate_guidebook`;
      
      console.log("📚 Calling guidebook API with mock data...");
      console.log("🔗 URL:", guidebookUrl);
      
      const requestBody = {
        travel_plan: mockPlan,
        formats: ["html"],
        language: "vi"
      };
      
      console.log("📤 Request body structure:", {
        has_travel_plan: !!requestBody.travel_plan,
        travel_plan_version: requestBody.travel_plan?.version,
        formats: requestBody.formats,
        language: requestBody.language
      });
      
      const guidebookResponse = await fetch(guidebookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      console.log("📡 Response status:", guidebookResponse.status);
      
      if (!guidebookResponse.ok) {
        const errorText = await guidebookResponse.text();
        console.error("❌ Guidebook generation failed:", errorText);
        throw new Error(`Failed: ${guidebookResponse.status}`);
      }

      const guidebookData = await guidebookResponse.json();
      console.log("✅ Guidebook generated successfully!");
      console.log("📋 Guidebook data:", guidebookData);
      
      // Download HTML content for database storage
      let guidebookHtmlContent = "";
      if (guidebookData.guidebook_id) {
        const downloadUrl = `${TRAVEL_PLANNER_API_URL}/v1/guidebook/${guidebookData.guidebook_id}/download?format=html`;
        console.log("📥 Downloading HTML content from:", downloadUrl);
        const htmlResponse = await fetch(downloadUrl);
        
        if (htmlResponse.ok) {
          guidebookHtmlContent = await htmlResponse.text();
          console.log("✅ HTML content downloaded, length:", guidebookHtmlContent.length);
        }
      }
      
      // 💾 Save mock plan to database (if authenticated)
      console.log("💾 Saving mock plan to database...");
      let databasePlanId = null;
      
      try {
        const token = localStorage.getItem("user");
        if (token) {
          const user = JSON.parse(token);
          
          // Validate access token exists
          if (!user.access_token) {
            console.error("❌ No access token found in user data");
            alert("⚠️ Session expired. Please login again.");
            return;
          }
          
          // Convert date to YYYY-MM-DD format
          let formattedDate = mockPlan.request_summary.departure_date;
          if (formattedDate && formattedDate.includes('/')) {
            const [day, month, year] = formattedDate.split('/');
            formattedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
          }
          
          const savePlanRequest = {
            destination: mockPlan.request_summary.destination,
            departure: mockPlan.request_summary.departure_point,
            start_date: formattedDate,
            duration: mockPlan.request_summary.trip_duration,
            number_of_travelers: mockPlan.request_summary.num_travelers,
            budget: mockPlan.request_summary.budget,
            travel_style: mockPlan.request_summary.travel_style,
            notes: mockPlan.request_summary.customer_notes || "",
            guidebook: guidebookHtmlContent // Save HTML content
          };
          
          console.log("📤 Saving mock plan to database:");
          console.log("  - Authorization header:", `Bearer ${user.access_token.substring(0, 20)}...`);
          console.log("  - Request data:", {
            ...savePlanRequest,
            guidebook: guidebookHtmlContent ? `[HTML content, ${guidebookHtmlContent.length} chars]` : null
          });
          
          const saveResponse = await fetch(`${NAVIAGENT_API_URL}/plans`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${user.access_token}`
            },
            body: JSON.stringify(savePlanRequest),
          });
          
          if (saveResponse.ok) {
            const savedPlan = await saveResponse.json();
            databasePlanId = savedPlan.id;
            console.log("✅ Mock plan saved to database with ID:", databasePlanId);
            console.log("📋 Guidebook URL in Storage:", savedPlan.guidebook);
          } else {
            const errorText = await saveResponse.text();
            console.error("⚠️ Failed to save mock plan to database:", saveResponse.status, errorText);
          }
        } else {
          console.log("⚠️ User not authenticated, skipping database save");
        }
      } catch (dbError) {
        console.error("⚠️ Database save error:", dbError);
      }
      
      // Save mock plan to localStorage (as backup)
      const planId = databasePlanId || `mock_${Date.now()}`;
      const completePlan = {
        id: planId,
        travel_data: {
          destination: mockPlan.request_summary.destination,
          departure_point: mockPlan.request_summary.departure_point,
          departure_date: mockPlan.request_summary.departure_date,
          trip_duration: mockPlan.request_summary.trip_duration,
          num_travelers: mockPlan.request_summary.num_travelers,
          budget: mockPlan.request_summary.budget,
          travel_style: mockPlan.request_summary.travel_style,
          customer_notes: mockPlan.request_summary.customer_notes
        },
        plan: mockPlan,
        guidebook_id: guidebookData.guidebook_id,
        guidebook_files: guidebookData.files || {},
        created_at: new Date().toISOString()
      };
      
      localStorage.setItem(`travel_plan_${planId}`, JSON.stringify(completePlan));
      
      // Update list
      const existingPlans = JSON.parse(localStorage.getItem('travel_plans_list') || '[]');
      existingPlans.push({
        id: planId,
        destination: completePlan.travel_data.destination,
        departure_date: completePlan.travel_data.departure_date,
        trip_duration: completePlan.travel_data.trip_duration,
        num_travelers: completePlan.travel_data.num_travelers,
        budget: completePlan.travel_data.budget,
        created_at: new Date().toISOString()
      });
      localStorage.setItem('travel_plans_list', JSON.stringify(existingPlans));
      
      console.log("💾 Mock plan saved to localStorage with ID:", planId);
      
      if (databasePlanId) {
        alert("✅ Test guidebook thành công! Mock plan đã được lưu vào database và Storage. Chuyển đến trang xem guidebook...");
      } else {
        alert("✅ Test guidebook thành công! Mock plan đã được lưu vào localStorage. Chuyển đến trang xem guidebook...");
      }
      router.push(`/itinerary/${planId}`);
      
    } catch (error) {
      console.error("❌ Test guidebook error:", error);
      alert(`Lỗi test guidebook: ${error}`);
    } finally {
      setIsLoading(false);
    }
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
          
          {/* Test Guidebook Button - Always Visible */}
          <div style={{ 
            marginTop: "16px", 
            display: "flex", 
            justifyContent: "center",
            paddingBottom: "16px"
          }}>
            <button 
              className="test-guidebook-btn" 
              onClick={handleTestGuidebook}
              disabled={isLoading}
              title="Click to test guidebook generation with pre-made travel plan (travel_plan_output_1.json)"
              style={{
                background: isLoading ? "#ccc" : "#28a745",
                border: "none",
                color: "white",
                padding: "12px 24px",
                borderRadius: "8px",
                fontWeight: "600",
                cursor: isLoading ? "not-allowed" : "pointer",
                transition: "all 0.2s ease",
                fontSize: "14px",
                boxShadow: "0 2px 8px rgba(40, 167, 69, 0.3)"
              }}
              onMouseOver={(e) => !isLoading && (e.currentTarget.style.background = "#218838")}
              onMouseOut={(e) => !isLoading && (e.currentTarget.style.background = "#28a745")}
            >
              🧪 Test Guidebook with Mock Data
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
