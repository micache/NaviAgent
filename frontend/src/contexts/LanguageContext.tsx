"use client";
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Language = "vi" | "en";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations = {
  vi: {
    // Header
    home: "Trang chủ",
    explore: "Khám phá",
    visited: "Nhật ký",
    plan: "Kế hoạch",
    signIn: "Đăng nhập",
    signOut: "Đăng xuất",
    signUp: "Đăng ký",
    email: "Email",
    password: "Mật khẩu",
    confirmPassword: "Xác nhận mật khẩu",
    alreadyHaveAccount: "Đã có tài khoản?",
    dontHaveAccount: "Chưa có tài khoản?",

    // Visited Page
    travelAssistant: "Trợ lý Hành trình",
    tellUsPlaces: "Hãy cho tôi biết địa điểm bạn đã đến!",
    greeting: "👋 Chào bạn! Bạn đã đến địa điểm nào rồi? Hãy cho tôi biết tên địa điểm nhé!",
    enterPlaceName: "Nhập tên địa điểm...",
    send: "Gửi",
    toggle2D: "Chế độ 2D",
    toggle3D: "Chế độ 3D",

    // Home Page
    heroTitle: "NaviAgent Travel",
    heroSubtitle: "Plan smarter, travel further — Trợ lý du lịch thông minh của bạn.",
    exploreNow: "Khám phá ngay",
    featuresTitle: "Tính năng nổi bật",
    travelMapTitle: "🌍 Nhật ký Hành trình",
    travelMapDesc: "Khám phá và nhìn lại hành trình của bạn trên bản đồ 3D tương tác. Ghim những nơi bạn từng đến và xem lại hành trình du lịch của mình một cách sinh động.",
    aiPlannerTitle: "🤖 Lập kế hoạch chuyến đi với AI",
    aiPlannerDesc: "Lên kế hoạch chuyến đi thông minh với sự trợ giúp của AI. Nhận gợi ý lịch trình, ước tính chi phí, và các điểm đến phù hợp với sở thích của bạn.",
    destinationGuideTitle: "📍 Gợi ý điểm đến",
    destinationGuideDesc: "Khám phá hàng ngàn điểm đến với hướng dẫn chi tiết về văn hóa, ẩm thực, thời tiết và những hoạt động tuyệt vời tại mỗi nơi.",
    planTitle: "🗂️ Xây dựng kế hoạch chuyên nghiệp",
    planDesc: "Tạo và chỉnh sửa kế hoạch du lịch chi tiết — bao gồm lịch trình, chi phí, lưu ý và gợi ý dịch vụ liên quan, giúp bạn sẵn sàng cho hành trình tiếp theo.",

    // Explore Page
    gallery: "📸 Bộ sưu tập",
    weather: "🌤️ Thời tiết",
    closePanel: "Đóng",
    chatPlaceholder: "Nhập tin nhắn...",
    openChat: "Mở chat",
    travelAssistantTitle: "Trợ lý Du lịch",
    exploreDestinationTitle: "Khám Phá Địa Điểm Du Lịch",
    askTravelQuestion: "Hãy nhập câu hỏi về du lịch!",
    describeDestination: "Hãy mô tả nơi bạn muốn đi (ví dụ: nơi nào đó nhiều đồi núi, có tuyết, có các hoạt động mùa đông...)",
    hanoiDesc: "Trái tim Việt Nam với nền văn hóa và lịch sử phong phú.",
    danangDesc: "Thành phố biển nổi tiếng với bãi biển và cầu cống.",
    hcmDesc: "Thành phố hiện đại đầy năng lượng và sôi động về đêm.",
    pleaseSignIn: "Vui lòng đăng nhập để nhận gợi ý địa điểm.",
    errorGettingSuggestion: "Xin lỗi, đã xảy ra lỗi khi lấy gợi ý. Vui lòng thử lại.",
    weatherOverview: "Tổng quan Thời tiết",
    weatherSubtext: "Kiểm tra cập nhật thời tiết mới nhất cho các điểm đến yêu thích của bạn.",
    clearSky: "Trời quang",
    sunny: "Nắng nóng",
    rainy: "Mưa",

    // Plan Page
    travelPlans: "Kế hoạch Du lịch",
    managePlans: "Quản lý các chuyến đi sắp tới và chuẩn bị cho hành trình của bạn.",
    destination: "Điểm đến",
    date: "Ngày",
    notes: "Ghi chú",
    tripPlanner: "Trợ lý Lập kế hoạch",
    tripPlannerDesc: "Hỏi trợ lý của chúng tôi để tạo lịch trình chi tiết, ước tính ngân sách, hoặc gợi ý điểm đến cho chuyến phiêu lưu tiếp theo!",
    plannerGreeting: "👋 Xin chào! Cần trợ giúp lên kế hoạch cho chuyến đi tiếp theo của bạn?",
    plannerExample: "Có, gợi ý cho tôi chuyến đi 3 ngày!",
    typeQuestion: "Nhập câu hỏi của bạn...",
    beachTrip: "Chuyến đi biển 3 ngày",
    hikingCold: "Đi bộ đường dài và thời tiết lạnh",
    createItineraryButton: "Tạo lịch trình",
    newChatButton: "Tạo đoạn chat mới",
    createItineraryTitle: "✨ Đang tạo lịch trình của bạn đến",
    createItineraryEstimate: "Lịch trình dự kiến hoàn thành trong khoảng 5 phút tới",
    processing: "Đang xử lý...",
    pleaseSignInFirst: "Vui lòng đăng nhập trước!",
    createItineraryError: "Không thể tạo lịch trình. Vui lòng thử lại!",
    pleaseSignInToStart: "Vui lòng đăng nhập để bắt đầu lên kế hoạch chuyến đi với trợ lý AI của chúng tôi.",
    pleaseSignInToChat: "Vui lòng đăng nhập để chat",
    authPromptText: "Vui lòng đăng nhập để bắt đầu lên kế hoạch chuyến đi với trợ lý AI của chúng tôi.",
    hideHistory: "Ẩn lịch sử",
    showHistory: "Hiện lịch sử",
    noHistory: "Không có lịch sử chat",
    
    // Travel Information
    travelInfo: "Thông tin chuyến du lịch",
    departurePoint: "Điểm khởi hành",
    departureDate: "Ngày khởi hành",
    duration: "Thời gian",
    travelers: "Số lượng người đi",
    budget: "Ngân sách",
    travelStyle: "Phong cách du lịch",
    planComplete: "✓ Hoàn thành thu thập thông tin chuyến đi!",
    
    // Itinerary List Page
    createdItineraries: "Lịch trình đã tạo",
    reviewItineraries: "Xem lại các chuyến đi bạn đã lên kế hoạch",
    noItineraries: "Chưa có lịch trình nào",
    startCreating: "Hãy bắt đầu tạo lịch trình cho chuyến đi của bạn!",
    createNewItinerary: "+ Tạo lịch trình mới",
    departureLabel: "📅 Khởi hành:",
    durationLabel: "⏱️ Thời gian:",
    travelersLabel: "👥 Số người:",
    budgetLabel: "💰 Ngân sách:",
    days: "ngày",
    people: "người",
    viewDetails: "Xem chi tiết",
    delete: "Xóa",
    confirmDelete: "Bạn có chắc muốn xóa lịch trình này?",
    deleteSuccessDB: "Đã xóa lịch trình khỏi database và localStorage!",
    deleteSuccessMock: "Đã xóa mock plan khỏi localStorage!",
    deleteSuccessLocal: "Đã xóa lịch trình khỏi localStorage!",
    deleteError: "Lỗi khi xóa lịch trình!",
    loading: "Đang tải...",
  },
  en: {
    // Header
    home: "Home",
    explore: "Explore",
    visited: "Visited",
    plan: "Plan",
    signIn: "Sign In",
    signOut: "Sign Out",
    signUp: "Sign Up",
    email: "Email",
    password: "Password",
    confirmPassword: "Confirm Password",
    alreadyHaveAccount: "Already have an account?",
    dontHaveAccount: "Don't have an account?",

    // Visited Page
    travelAssistant: "Travel Assistant",
    tellUsPlaces: "Tell us about the places you've visited!",
    greeting: "👋 Hello! Where have you been? Please tell me the place name!",
    enterPlaceName: "Enter place name...",
    send: "Send",
    toggle2D: "2D Mode",
    toggle3D: "3D Mode",

    // Home Page
    heroTitle: "NaviAgent Travel",
    heroSubtitle: "Plan smarter, travel further — Your intelligent travel assistant.",
    exploreNow: "Explore Now",
    featuresTitle: "Key Features",
    travelMapTitle: "🌍 Travel Map",
    travelMapDesc: "Explore and revisit your journey on an interactive 3D map. Pin the places you've been and relive your travel experiences vividly.",
    aiPlannerTitle: "🤖 AI Trip Planner",
    aiPlannerDesc: "Plan your trip smartly with AI assistance. Get itinerary suggestions, budget estimates, and destinations that match your preferences.",
    destinationGuideTitle: "📍 Destination Guide",
    destinationGuideDesc: "Discover thousands of destinations with detailed guides about culture, cuisine, weather, and amazing activities at each place.",
    planTitle: "🗂️ Professional Planning",
    planDesc: "Create and edit detailed travel plans — including itineraries, budgets, notes, and related service suggestions to help you prepare for your next journey.",

    // Explore Page
    gallery: "📸 Gallery",
    weather: "🌤️ Weather",
    closePanel: "Close",
    chatPlaceholder: "Type a message...",
    openChat: "Open chat",
    travelAssistantTitle: "Travel Assistant",
    exploreDestinationTitle: "Explore Travel Destinations",
    askTravelQuestion: "Ask me about travel!",
    describeDestination: "Describe where you want to go (e.g., a place with mountains, has snow, embraces winter activities...)",
    hanoiDesc: "The heart of Vietnam with rich culture and history.",
    danangDesc: "Coastal city known for beaches and bridges.",
    hcmDesc: "Vibrant modern city full of energy and nightlife.",
    pleaseSignIn: "Please sign in to get destination suggestions.",
    errorGettingSuggestion: "Sorry, there was an error getting suggestions. Please try again.",
    weatherOverview: "Weather Overview",
    weatherSubtext: "Check the latest weather updates for your favorite destinations.",
    clearSky: "Clear sky",
    sunny: "Sunny",
    rainy: "Rainy",

    // Plan Page
    travelPlans: "Travel Plans",
    managePlans: "Manage your upcoming trips and prepare your journey.",
    destination: "Destination",
    date: "Date",
    notes: "Notes",
    tripPlanner: "Trip Planner Assistant",
    tripPlannerDesc: "Ask our assistant to create a detailed itinerary, estimate budget, or suggest destinations for your next adventure!",
    plannerGreeting: "👋 Hi there! Need help planning your next trip?",
    plannerExample: "Yes, recommend a 3-day trip!",
    typeQuestion: "Type your question...",
    beachTrip: "3-day beach trip",
    hikingCold: "Hiking and cold weather",
    createItineraryButton: "Create Itinerary",
    newChatButton: "New Chat",
    createItineraryTitle: "✨ Creating your itinerary to",
    createItineraryEstimate: "Itinerary expected to complete in about 5 minutes",
    processing: "Processing...",
    pleaseSignInFirst: "Please sign in first!",
    createItineraryError: "Unable to create itinerary. Please try again!",
    pleaseSignInToStart: "Please sign in to start planning your trip with our AI assistant.",
    pleaseSignInToChat: "Please sign in to chat",
    authPromptText: "Please sign in to start planning your trip with our AI assistant.",
    hideHistory: "Hide history",
    showHistory: "Show history",
    noHistory: "No chat history",
    
    // Travel Information
    travelInfo: "Travel Information",
    departurePoint: "Departure Point",
    departureDate: "Departure Date",
    duration: "Duration",
    travelers: "Number of Travelers",
    budget: "Budget",
    travelStyle: "Travel Style",
    planComplete: "✓ Travel information collected successfully!",
    
    // Itinerary List Page
    createdItineraries: "Created Itineraries",
    reviewItineraries: "Review the trips you have planned",
    noItineraries: "No itineraries yet",
    startCreating: "Start creating an itinerary for your trip!",
    createNewItinerary: "+ Create New Itinerary",
    departureLabel: "📅 Departure:",
    durationLabel: "⏱️ Duration:",
    travelersLabel: "👥 Travelers:",
    budgetLabel: "💰 Budget:",
    days: "days",
    people: "people",
    viewDetails: "View Details",
    delete: "Delete",
    confirmDelete: "Are you sure you want to delete this itinerary?",
    deleteSuccessDB: "Itinerary deleted from database and localStorage!",
    deleteSuccessMock: "Mock plan deleted from localStorage!",
    deleteSuccessLocal: "Itinerary deleted from localStorage!",
    deleteError: "Error deleting itinerary!",
    loading: "Loading...",
  },
};

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("vi");

  useEffect(() => {
    const saved = localStorage.getItem("language");
    if (saved === "en" || saved === "vi") {
      setLanguageState(saved);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  };

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations.vi] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}
