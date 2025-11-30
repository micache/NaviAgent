"use client";

import { useState } from "react";
import Image from "next/image";
import sendIcon from "@/images/send.svg";
import { motion, AnimatePresence } from "framer-motion";
import "@/styles/explore.css";

export default function ExplorePage() {
  const [mode, setMode] = useState<"gallery" | "weather">("gallery");
  const [showLeftPanel, setShowLeftPanel] = useState(false);

  // Chat state
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<string[]>([]);

  const destinations = [
    {
      name: "Hà Nội",
      image: "/images/hanoi.jpg",
      description: "The heart of Vietnam with culture and history.",
    },
    {
      name: "Đà Nẵng",
      image: "/images/danang.jpg",
      description: "Coastal city known for beaches and bridges.",
    },
    {
      name: "TP. HCM",
      image: "/images/hcmcity.jpg",
      description: "Vibrant modern city full of energy and nightlife.",
    },
  ];

  const [index, setIndex] = useState(0);
  const current = destinations[index];

  const prevImg = () =>
    setIndex((prev) => (prev === 0 ? destinations.length - 1 : prev - 1));
  const nextImg = () =>
    setIndex((prev) => (prev === destinations.length - 1 ? 0 : prev + 1));

  // Gửi tin nhắn chat
  const handleSendChat = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim()) return;
    setMessages((prev) => [...prev, chatInput.trim()]);
    setChatInput("");
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
                📸 Gallery
              </button>
              <button
                className={mode === "weather" ? "active" : ""}
                onClick={() => setMode("weather")}
              >
                🌤️ Weather
              </button>
            </div>
            <button 
              className="close-panel-btn"
              onClick={() => setShowLeftPanel(false)}
              title="Close panel"
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
              <h1 className="explore-title">Weather Overview ☁️</h1>
              <p className="explore-subtext">
                Check the latest weather updates for your favorite destinations.
              </p>

              <div className="explore-grid">
                <div className="explore-card">
                  <h2>Hà Nội</h2>
                  <p>🌤 30°C | Clear sky</p>
                </div>
                <div className="explore-card">
                  <h2>Đà Nẵng</h2>
                  <p>☀️ 32°C | Sunny</p>
                </div>
                <div className="explore-card">
                  <h2>TP. HCM</h2>
                  <p>🌧 28°C | Rainy</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
      )}

      {/* ========== RIGHT PANEL (CHATBOT + CHAT INPUT) ========== */}
      <div className={`explore-right ${!showLeftPanel ? "full-width" : ""}`}>
        <div className="chat-header">
          <h2>💬 Travel Assistant</h2>
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
          {messages.length === 0 ? (
            <p className="chat-placeholder">Hãy nhập câu hỏi về du lịch!</p>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className="chat-message">{msg}</div>
            ))
          )}
        </div>
        {/* Ô nhập chat và nút gửi */}
        <div className="chat-input-container">
          <form className="chat-input-row" onSubmit={handleSendChat}>
            <input
              type="text"
              className="chat-input"
              placeholder="Nhập tin nhắn..."
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
            />
            <button type="submit" className="chat-send-btn" title="Gửi">
              <Image src={sendIcon} alt="Send" width={24} height={24} />
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
