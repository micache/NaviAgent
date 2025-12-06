"use client";
import "@/styles/visited.css";
import { useEffect, useRef, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

// API URL from environment variable
const NAVIAGENT_API_URL = process.env.NEXT_PUBLIC_NAVIAGENT_API_URL || "http://localhost:8001";

interface Place {
  id: string;
  name: string;
  lat: number;
  lng: number;
  images?: string[];
}

interface ChatMsg {
  role: "bot" | "user";
  content: string;
}

export default function VisitedPage() {
  const { t } = useLanguage();
  const globeRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMapRef = useRef<any>(null);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [imgIndex, setImgIndex] = useState(0);
  const [is3D, setIs3D] = useState(false);
  const [places, setPlaces] = useState<Place[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize chat with translated greeting
  useEffect(() => {
    setChatMessages([{ role: "bot", content: t("greeting") }]);
  }, [t]);

  // Check authentication
  useEffect(() => {
    const userStr = localStorage.getItem("user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setIsAuthenticated(!!user.access_token);
      } catch (e) {
        setIsAuthenticated(false);
      }
    }
  }, []);

  // Load trips from API
  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const userStr = localStorage.getItem("user");
      if (!userStr) {
        console.log("No user found in localStorage");
        return;
      }

      const user = JSON.parse(userStr);
      const token = user.access_token;

      if (!token) {
        console.log("No access token in user object");
        return;
      }

      console.log("Loading trips with token:", token.substring(0, 20) + "...");

      const res = await fetch(`${NAVIAGENT_API_URL}/trips/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      console.log("Response status:", res.status);

      if (res.ok) {
        const trips = await res.json();
        const converted = trips
          .filter((t: any) => t.address)
          .map((t: any) => {
            // Parse address if it's JSON string
            let addr = t.address;
            if (typeof addr === "string") {
              try {
                addr = JSON.parse(addr);
              } catch (e) {
                addr = { name: t.address, lat: 0, lng: 0 };
              }
            }
            return {
              id: t.id,
              name: addr.name || addr,
              lat: addr.lat || 0,
              lng: addr.lng || 0,
            };
          });
        setPlaces(converted);
      }
    } catch (err) {
      console.error("Failed to load trips:", err);
    }
  };

  // Initialize 3D Globe
  useEffect(() => {
    if (!is3D) return;

    let world: any = null;

    (async () => {
      const Globe = (await import("globe.gl")).default;
      const container = globeRef.current;
      if (!container) return;

      // Clear container first
      container.innerHTML = "";

      // Show loading state
      container.style.opacity = '0';

      world = new Globe(container)
        .globeImageUrl("//unpkg.com/three-globe/example/img/earth-day.jpg")
        .width(container.offsetWidth)
        .height(container.offsetHeight)
        .htmlElementsData(places)
        .htmlElement((d: any) => {
          const el = document.createElement('div');
          el.innerHTML = '📍';
          el.style.cursor = 'pointer';
          el.style.userSelect = 'none';
          el.style.fontSize = '20px';
          el.style.lineHeight = '20px';
          el.style.width = '20px';
          el.style.height = '20px';
          el.style.display = 'block';
          // Sử dụng margin để căn chỉnh chính xác
          el.style.marginLeft = '-5px';  // Dịch phải (tăng giá trị)
          el.style.marginTop = '-8px';
          el.onclick = () => {
            setSelectedPlace(d as Place);
            setImgIndex(0);
          };

          // Add tooltip
          const tooltip = document.createElement('div');
          tooltip.innerHTML = d.name;
          tooltip.style.position = 'absolute';
          tooltip.style.background = 'rgba(0, 0, 0, 0.8)';
          tooltip.style.color = 'white';
          tooltip.style.padding = '4px 8px';
          tooltip.style.borderRadius = '4px';
          tooltip.style.fontSize = '12px';
          tooltip.style.pointerEvents = 'none';
          tooltip.style.whiteSpace = 'nowrap';
          tooltip.style.display = 'none';
          tooltip.style.marginTop = '8px';
          tooltip.style.marginLeft = '-50%';
          tooltip.style.left = '50%';
          tooltip.style.transform = 'translateX(-50%)';

          el.onmouseenter = () => {
            tooltip.style.display = 'block';
          };
          el.onmouseleave = () => {
            tooltip.style.display = 'none';
          };

          el.appendChild(tooltip);
          return el;
        })
        .htmlAltitude(0.01);

      // Add country borders
      const bordersPromise = fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
        .then(res => res.json())
        .then(countries => {
          world
            .polygonsData(countries.features)
            .polygonCapColor(() => 'rgba(0, 0, 0, 0)')
            .polygonSideColor(() => 'rgba(0, 100, 0, 0.1)')
            .polygonStrokeColor(() => '#2c3e50')
            .polygonAltitude(0.001);
        })
        .catch(err => console.warn('Failed to load country borders:', err));

      // Set initial view
      world.pointOfView({ lat: 15, lng: 108, altitude: 2.4 });
      world.controls().autoRotate = true;
      world.controls().autoRotateSpeed = 0.25;

      // Wait for borders to load and globe to render, then show
      await bordersPromise;

      // Wait for globe to finish initial render
      await new Promise(resolve => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            resolve(null);
          });
        });
      });

      // Now fade in
      container.style.transition = 'opacity 0.3s ease-in';
      container.style.opacity = '1';

      const handleResize = () => {
        if (world) {
          world.width(container.offsetWidth).height(container.offsetHeight);
        }
      };
      window.addEventListener("resize", handleResize);
    })();

    return () => {
      if (world && world._destructor) {
        world._destructor();
      }
      if (globeRef.current) {
        globeRef.current.innerHTML = "";
      }
    };
  }, [is3D, places]);

  // Initialize 2D Map (Leaflet)
  useEffect(() => {
    if (is3D) return;

    const initMap = async () => {
      try {
        const L = (await import("leaflet")).default;

        const container = mapRef.current;
        if (!container) return;

        // Clean up existing map first
        if (leafletMapRef.current) {
          try {
            leafletMapRef.current.remove();
            leafletMapRef.current = null;
          } catch (e) {
            console.warn("Error removing existing map:", e);
          }
        }

        // Remove Leaflet internal reference
        if ((container as any)._leaflet_id) {
          delete (container as any)._leaflet_id;
        }

        // Create Leaflet map centered on Hanoi with zoom to see East Asia
        leafletMapRef.current = L.map(container, {
          center: [21.0285, 105.8542],
          zoom: 3,
          dragging: true,
          touchZoom: true,
          scrollWheelZoom: true,
          doubleClickZoom: true,
          boxZoom: true,
          keyboard: true,
          zoomControl: true,
        });

        // Add OpenStreetMap tiles
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(leafletMapRef.current);

        // Store markers for zoom updates
        const markers: any[] = [];

        // Create custom pin icon with dynamic size based on zoom
        const createPinIcon = (zoom: number) => {
          // Scale icon size based on zoom level (zoom 3-19)
          // At zoom 3: size 16px, at zoom 10: size 32px, at zoom 19: size 48px
          const baseSize = Math.max(16, Math.min(48, 16 + (zoom - 3) * 2));
          return L.divIcon({
            html: `<div style="font-size: ${baseSize}px; line-height: 1; text-align: center; margin-left: -${baseSize/4}px;">📍</div>`,
            className: 'custom-pin-icon',
            iconSize: [baseSize, baseSize],
            iconAnchor: [baseSize / 2, baseSize * 0.85],
            popupAnchor: [0, -baseSize * 0.85],
          });
        };

        // Add markers
        places.forEach((place) => {
          const marker = L.marker([place.lat, place.lng], {
            icon: createPinIcon(leafletMapRef.current.getZoom()),
          }).addTo(leafletMapRef.current);
          marker.bindPopup(`<b>${place.name}</b>`);
          marker.on("click", () => {
            setSelectedPlace(place);
            setImgIndex(0);
          });
          markers.push({ marker, place });
        });

        // Update icon sizes on zoom
        leafletMapRef.current.on('zoomend', () => {
          const currentZoom = leafletMapRef.current.getZoom();
          markers.forEach(({ marker }) => {
            marker.setIcon(createPinIcon(currentZoom));
          });
        });

        console.log("Leaflet map loaded successfully");

      } catch (error) {
        console.error("Failed to initialize Leaflet:", error);
      }
    };

    initMap();

    return () => {
      if (leafletMapRef.current) {
        try {
          leafletMapRef.current.remove();
          leafletMapRef.current = null;
        } catch (e) {
          console.warn("Error removing map:", e);
        }
      }
      if (mapRef.current && (mapRef.current as any)._leaflet_id) {
        delete (mapRef.current as any)._leaflet_id;
      }
    };
  }, [is3D, places]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMsg = inputValue.trim();
    setChatMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Call geocoding API to get coordinates
      const geoRes = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(userMsg)}&format=json&limit=1`
      );
      const geoData = await geoRes.json();

      if (geoData.length === 0) {
        setChatMessages((prev) => [
          ...prev,
          { role: "bot", content: "❌ Không tìm thấy địa điểm này. Bạn có thể thử lại với tên khác không?" },
        ]);
        setIsLoading(false);
        return;
      }

      const { display_name, lat, lon } = geoData[0];
      const latitude = parseFloat(lat);
      const longitude = parseFloat(lon);

      // Prepare address JSON
      const addressData = {
        name: display_name,
        lat: latitude,
        lng: longitude,
      };

      // Add to database
      const userStr = localStorage.getItem("user");
      console.log("User data:", userStr);

      if (!userStr) {
        setChatMessages((prev) => [
          ...prev,
          { role: "bot", content: "❌ Bạn cần đăng nhập để lưu địa điểm! Vui lòng đăng nhập lại." },
        ]);
        setIsLoading(false);
        return;
      }

      const user = JSON.parse(userStr);
      const token = user.access_token;

      if (!token) {
        setChatMessages((prev) => [
          ...prev,
          { role: "bot", content: "❌ Token không hợp lệ! Vui lòng đăng nhập lại." },
        ]);
        setIsLoading(false);
        return;
      }

      const res = await fetch(`${NAVIAGENT_API_URL}/trips/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          address: addressData,
          status: "visited",
        }),
      });

      if (res.ok) {
        const newTrip = await res.json();

        // Add marker immediately without reloading
        const newPlace: Place = {
          id: newTrip.id,
          name: display_name,
          lat: latitude,
          lng: longitude,
        };

        setPlaces((prev) => [...prev, newPlace]);

        // Add marker to current map
        if (!is3D && leafletMapRef.current) {
          const L = (await import("leaflet")).default;

          // Create pin icon
          const pinIcon = L.divIcon({
            html: '<div style="font-size: 32px; line-height: 1;">📍</div>',
            className: 'custom-pin-icon',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
          });

          const marker = L.marker([latitude, longitude], {
            icon: pinIcon,
          }).addTo(leafletMapRef.current);
          marker.bindPopup(`<b>${display_name}</b>`);
          marker.on("click", () => {
            setSelectedPlace(newPlace);
            setImgIndex(0);
          });

          // Pan to new location
          leafletMapRef.current.setView([latitude, longitude], 8, {
            animate: true,
            duration: 1,
          });
        }

        setChatMessages((prev) => [
          ...prev,
          { role: "bot", content: `✅ Tuyệt vời! Đã thêm "${display_name}" vào bản đồ của bạn! 📍` },
        ]);
      } else {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "API failed");
      }
    } catch (err: any) {
      console.error("Error adding place:", err);
      setChatMessages((prev) => [
        ...prev,
        { role: "bot", content: `❌ Có lỗi xảy ra: ${err.message || "Vui lòng thử lại!"}` },
      ]);
    }

    setIsLoading(false);
  };

  const nextImg = () => {
    if (!selectedPlace?.images) return;
    setImgIndex((i) => (i + 1) % selectedPlace.images!.length);
  };

  const prevImg = () => {
    if (!selectedPlace?.images) return;
    setImgIndex((i) => (i === 0 ? selectedPlace.images!.length - 1 : i - 1));
  };

  return (
    <section className="visited-layout">
      <div className="visited-left">
        <div className="visited-header">
          <h1 className="visited-title">{t("visited")} 🌐</h1>
          <button className="toggle-map-btn" onClick={() => setIs3D(!is3D)}>
            {is3D ? `🗺️ ${t("toggle2D")}` : `🌍 ${t("toggle3D")}`}
          </button>
        </div>

        {is3D ? (
          <div ref={globeRef} className="visited-globe"></div>
        ) : (
          <div ref={mapRef} className="visited-map"></div>
        )}

        {selectedPlace?.images && (
          <div className="visited-gallery">
            <button onClick={prevImg} className="nav-btn left">
              ❮
            </button>
            <img
              src={selectedPlace.images[imgIndex]}
              alt={selectedPlace.name}
              className="place-photo"
            />
            <button onClick={nextImg} className="nav-btn right">
              ❯
            </button>
            <div className="caption">
              {selectedPlace.name} — {imgIndex + 1} / {selectedPlace.images.length}
            </div>
          </div>
        )}
      </div>

      <div className="visited-right">
        <h2>💬 {t("travelAssistant")}</h2>
        <p>{t("tellUsPlaces")}</p>
        <div className="chat-box">
          <div className="chat-messages">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isLoading && <div className="chat-message bot">⏳ Đang xử lý...</div>}
          </div>
          <div className="chat-input">
            <input
              type="text"
              placeholder={t("enterPlaceName")}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              {t("send")}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
