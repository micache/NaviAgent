"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import sendIcon from "@/images/send.svg";
import { motion, AnimatePresence } from "framer-motion";
import "@/styles/explore.css";
import { useLanguage } from "@/contexts/LanguageContext";
import ReactMarkdown from "react-markdown";

const NAVIAGENT_API_URL = process.env.NEXT_PUBLIC_NAVIAGENT_API_URL || "http://localhost:8001";

export default function ExplorePage() {
  const { t } = useLanguage();

  // Chat state
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([
    { role: "assistant", content: t("describeDestination") }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [suggestedDestinations, setSuggestedDestinations] = useState<Array<{name: string, country: string, image: string, description: string}>>([]);

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
  const displayDestinations = suggestedDestinations.length > 0 ? suggestedDestinations : destinations;
  const current = displayDestinations[index];

  // Auto-play gallery (5 seconds interval)
  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev === displayDestinations.length - 1 ? 0 : prev + 1));
    }, 5000);
    return () => clearInterval(interval);
  }, [displayDestinations.length]);

  const prevImg = () =>
    setIndex((prev) => (prev === 0 ? displayDestinations.length - 1 : prev - 1));
  const nextImg = () =>
    setIndex((prev) => (prev === displayDestinations.length - 1 ? 0 : prev + 1));

  // Helper function to remove Vietnamese accents
  const removeVietnameseAccents = (str: string): string => {
    return str
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/đ/g, 'd')
      .replace(/Đ/g, 'D');
  };

  // Helper function to find matching image file
  const findImageFile = (cityName: string, countryName: string): string => {
    // List of available image files (based on your public/images/destinations folder)
    const availableImages: {[key: string]: string} = {
      'da nang': 'Da_Nang_Vietnam.jpg',
      'danang': 'Da_Nang_Vietnam.jpg',
      'da lat': 'Da_Lat_Vietnam.jpg',
      'dalat': 'Da_Lat_Vietnam.jpg',
      'ha long': 'Ha_Long_Vietnam.jpg',
      'halong': 'Ha_Long_Vietnam.jpg',
      'hanoi': 'Hanoi_Vietnam.png',
      'ha noi': 'Hanoi_Vietnam.png',
      'hoi an': 'Hoi_An_Vietnam.jpg',
      'hoian': 'Hoi_An_Vietnam.jpg',
      'harbin': 'Harbin_China.jpg',
      'hue': 'Hue_Vietnam.jpg',
      'nha trang': 'Nha_Trang_Vietnam.jpg',
      'nhatrang': 'Nha_Trang_Vietnam.jpg',
      'phu quoc': 'Phu_Quoc_Vietnam.webp',
      'phuquoc': 'Phu_Quoc_Vietnam.webp',
      'sapa': 'Sapa_Vietnam.jpg',
      'sa pa': 'Sapa_Vietnam.jpg',
      'ho chi minh': 'Ho_Chi_Minh_City_Vietnam.jpg',
      'hcm': 'Ho_Chi_Minh_City_Vietnam.jpg',
      'saigon': 'Ho_Chi_Minh_City_Vietnam.jpg',
      'tokyo': 'Tokyo_Japan.jpg',
      'kyoto': 'Kyoto_Japan.jpg',
      'osaka': 'Osaka_Japan.jpg',
      'fukuoka': 'Fukuoka_Japan.jpg',
      'sapporo': 'Sapporo_Japan.jpg',
      'nagoya': 'Nagoya_Japan.jpg',
      'nara': 'Nara_Japan.jpg',
      'kobe': 'Kobe_Japan.jpg',
      'yokohama': 'Yokohama_Japan.jpg',
      'seoul': 'Seoul_South_Korea.jpg',
      'busan': 'Busan_South_Korea.jpg',
      'jeju': 'Jeju_City_South_Korea.jpg',
      'jeju city': 'Jeju_City_South_Korea.jpg',
      'incheon': 'Incheon_South_Korea.jpg',
      'daegu': 'Daegu_South_Korea.jpg',
      'taipei': 'Taipei_Taiwan.jpg',
      'kaohsiung': 'Kaohsiung_Taiwan.jpg',
      'taichung': 'Taichung_Taiwan.jpg',
      'tainan': 'Tainan_Taiwan.jpg',
      'hualien': 'Hualien_Taiwan.jpg',
      'beijing': 'Beijing_China.jpg',
      'shanghai': 'Shanghai_China.jpg',
      'guangzhou': 'Guangzhou_China.jpg',
      'shenzhen': 'Shenzhen_China.jpg',
      'chengdu': 'Chengdu_China.jpg',
      'hangzhou': 'Hangzhou_China.jpg',
      'guilin': 'Guilin_China.jpg',
      'xian': 'Xian_China.jpg',
      "xi'an": 'Xian_China.jpg',
      'suzhou': 'Suzhou_China.jpg',
      'hong kong': 'Hong_Kong_China.jpg',
      'hongkong': 'Hong_Kong_China.jpg',
      'macau': 'Macau_China.jpg',
      'chiang mai': 'Chiang_Mai_Thailand.jpg',
      'chiangmai': 'Chiang_Mai_Thailand.jpg',
    };

    // Normalize city name for lookup
    const normalizedCity = removeVietnameseAccents(cityName).toLowerCase().trim();
    
    // Try exact match first
    if (availableImages[normalizedCity]) {
      return availableImages[normalizedCity];
    }

    // Try partial match
    for (const [key, value] of Object.entries(availableImages)) {
      if (key.includes(normalizedCity) || normalizedCity.includes(key)) {
        return value;
      }
    }

    // If not found in local images, use Unsplash for placeholder
    // Return a special marker that we'll detect later
    return `UNSPLASH:${cityName}`;
  };

  // Fetch image from Unsplash API
  const fetchUnsplashImage = async (cityName: string): Promise<string> => {
    try {
      const query = encodeURIComponent(`${cityName} travel landmark`);
      const accessKey = process.env.NEXT_PUBLIC_UNSPLASH_ACCESS_KEY || 'YOUR_ACCESS_KEY';
      
      const response = await fetch(
        `https://api.unsplash.com/search/photos?query=${query}&per_page=1&orientation=landscape`,
        {
          headers: {
            'Authorization': `Client-ID ${accessKey}`,
            'Accept-Version': 'v1'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Unsplash API error');
      }

      const data = await response.json();
      if (data.results && data.results.length > 0) {
        // Return the regular size image URL
        return data.results[0].urls.regular;
      }

      return '/images/destination.jpg';
    } catch (error) {
      console.error('Failed to fetch Unsplash image:', error);
      return '/images/destination.jpg';
    }
  };

  // Gửi tin nhắn chat
  const handleSendChat = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || isLoading) return;

    const userMessage = chatInput.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setChatInput("");
    setIsLoading(true);

    try {
      const token = sessionStorage.getItem("user");
      if (!token) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: t("pleaseSignIn") },
        ]);
        setIsLoading(false);
        return;
      }

      const user = JSON.parse(token);
      const response = await fetch(`${NAVIAGENT_API_URL}/destinations/suggest`, {
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

      // Parse destinations from response
      const destRegex = /🌍\s*\*\*([^,]+),\s*([^*]+)\*\*/g;
      const parsed: Array<{name: string, country: string, image: string, description: string}> = [];
      let match;
      while ((match = destRegex.exec(cleanedContent)) !== null) {
        const name = match[1].trim();
        const country = match[2].trim();
        
        // Find matching image file
        const filename = findImageFile(name, country);
        console.log(`Parsed: ${name}, ${country} -> ${filename}`);
        
        // Check if we need to fetch from Unsplash
        let imagePath = `/images/destinations/${filename}`;
        if (filename.startsWith('UNSPLASH:')) {
          const cityName = filename.replace('UNSPLASH:', '');
          imagePath = await fetchUnsplashImage(cityName);
          console.log(`Using Unsplash image for ${cityName}: ${imagePath}`);
        }
        
        parsed.push({ name: `${name}, ${country}`, country, image: imagePath, description: '' });
      }
      if (parsed.length > 0) {
        setSuggestedDestinations(parsed);
        setIndex(0); // Reset to first image
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: t("errorGettingSuggestion") },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="explore-layout">
      {/* ========== LEFT PANEL ========== */}
      <div className="explore-left">
        <div className="gallery-header">
          <h2>{t("exploreDestinationTitle")}</h2>
        </div>
        <div className="explore-gallery">
              <AnimatePresence mode="wait">
                <motion.img
                  key={index}
                  src={current.image}
                  alt={current.name}
                  className="explore-photo"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.5 }}
                />
              </AnimatePresence>
              <button onClick={prevImg} className="nav-btn left">
                ❮
              </button>
              <button onClick={nextImg} className="nav-btn right">
                ❯
              </button>

              <div className="explore-caption">
                <h2>{current.name}</h2>
              </div>
          </div>
        </div>

      {/* ========== RIGHT PANEL (CHATBOT + CHAT INPUT) ========== */}
      <div className="explore-right">
        <div className="chat-header center">
          <div className="chat-title">
            <Image
              src="/images/beach.jpg"
              alt="Travel assistant"
              width={40}
              height={40}
              className="chat-title-icon"
            />
            <h2>{t("travelAssistantTitle")}</h2>
          </div>
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
