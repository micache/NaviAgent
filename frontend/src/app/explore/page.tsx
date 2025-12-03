"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import sendIcon from "@/images/send.svg";
import { motion, AnimatePresence } from "framer-motion";
import "@/styles/explore.css";
import { useLanguage } from "@/contexts/LanguageContext";
import ReactMarkdown from "react-markdown";

export default function ExplorePage() {
  const { t } = useLanguage();
  const [mode, setMode] = useState<"gallery" | "weather">("gallery");
  const [showLeftPanel, setShowLeftPanel] = useState(true);

  // Chat state
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([
    { role: "assistant", content: t("describeDestination") }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const destinations = [
    {
      name: "Hà Nội",
      image: "/images/hanoi.jpg",
      description: t("hanoiDesc"),
    },
    {
      name: "Đà Nẵng",
      image: "/images/danang.jpg",
      description: t("danangDesc"),
    },
    {
      name: "TP. HCM",
      image: "/images/hcmcity.jpg",
      description: t("hcmDesc"),
    },
  ];

  const [index, setIndex] = useState(0);
  const current = destinations[index];

  const prevImg = () =>
    setIndex((prev) => (prev === 0 ? destinations.length - 1 : prev - 1));
  const nextImg = () =>
    setIndex((prev) => (prev === destinations.length - 1 ? 0 : prev + 1));

  // Gửi tin nhắn chat
  const handleSendChat = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || isLoading) return;

    const userMessage = chatInput.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setChatInput("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("user");
      if (!token) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Please sign in to get destination suggestions." },
        ]);
        setIsLoading(false);
        return;
      }

      const user = JSON.parse(token);
      const response = await fetch("http://localhost:8000/destinations/suggest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.access_token}`,
        },
        body: JSON.stringify({ description: userMessage }),
      });

      if (!response.ok) {
        throw new Error("Failed to get suggestion");
      }

      const data = await response.json();
      // Clean up markdown: remove trailing spaces that create line breaks
      const cleanedContent = data.reason.replace(/  +\n/g, '\n').trim();
      setMessages((prev) => [...prev, { role: "assistant", content: cleanedContent }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, there was an error getting suggestions. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="explore-layout">
      {/* ========== LEFT PANEL ========== */}
      {showLeftPanel && (
        <div className="explore-left">
          <div className="panel-header">
            <div className="mode-switch">
              <button
                className={mode === "gallery" ? "active" : ""}
                onClick={() => setMode("gallery")}
              >
                {t("gallery")}
              </button>
              <button
                className={mode === "weather" ? "active" : ""}
                onClick={() => setMode("weather")}
              >
                {t("weather")}
              </button>
            </div>
            <button 
              className="close-panel-btn"
              onClick={() => setShowLeftPanel(false)}
              title={t("closePanel")}
            >
              ✕
            </button>
          </div>

          <AnimatePresence mode="wait">
            {mode === "gallery" ? (
            <motion.div
              key="gallery"
              className="explore-gallery"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              <img
                src={current.image}
                alt={current.name}
                className="explore-photo"
              />
              <button onClick={prevImg} className="nav-btn left">
                ❮
              </button>
              <button onClick={nextImg} className="nav-btn right">
                ❯
              </button>

              <div className="explore-caption">
                <h2>{current.name}</h2>
                <p>{current.description}</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="weather"
              className="explore-weather"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              <h1 className="explore-title">{t("weatherOverview")}</h1>
              <p className="explore-subtext">
                {t("weatherSubtext")}
              </p>

              <div className="explore-grid">
                <div className="explore-card">
                  <h2>Hà Nội</h2>
                  <p>🌤 30°C | {t("clearSky")}</p>
                </div>
                <div className="explore-card">
                  <h2>Đà Nẵng</h2>
                  <p>☀️ 32°C | {t("sunny")}</p>
                </div>
                <div className="explore-card">
                  <h2>TP. HCM</h2>
                  <p>🌧 28°C | {t("rainy")}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
      )}

      {/* ========== RIGHT PANEL (CHATBOT + CHAT INPUT) ========== */}
      <div className={`explore-right ${!showLeftPanel ? "full-width" : ""}}`}>
        <div className="chat-header">
          <h2>{t("travelAssistantTitle")}</h2>
          {!showLeftPanel && (
            <button 
              className="show-panel-btn"
              onClick={() => setShowLeftPanel(true)}
            >
              Show Gallery & Weather
            </button>
          )}
        </div>
        {/* Hiển thị tin nhắn chat */}
        <div className="chat-messages">
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
        {/* Ô nhập chat và nút gửi */}
        <div className="chat-input-container">
          <form className="chat-input-row" onSubmit={handleSendChat}>
            <input
              type="text"
              className="chat-input"
              placeholder={t("chatPlaceholder")}
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
            />
            <button type="submit" className="chat-send-btn" title={t("send")}>
              <Image src={sendIcon} alt="Send" width={24} height={24} />
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
