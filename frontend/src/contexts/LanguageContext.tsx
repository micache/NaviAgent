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
    visited: "Đã đến",
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
    travelAssistant: "Trợ lý Du lịch",
    tellUsPlaces: "Hãy cho tôi biết địa điểm bạn đã đến!",
    greeting: "👋 Chào bạn! Bạn đã đến địa điểm nào rồi? Hãy cho tôi biết tên địa điểm nhé!",
    enterPlaceName: "Nhập tên địa điểm...",
    send: "Gửi",
    toggle2D: "Chế độ 2D",
    toggle3D: "Chế độ 3D",
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
