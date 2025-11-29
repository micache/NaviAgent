"use client";
import "@/styles/visited.css";
import { useEffect, useRef, useState } from "react";

interface Place {
  name: string;
  lat: number;
  lng: number;
  images: string[];
}

export default function VisitedPage() {
  const globeRef = useRef<HTMLDivElement>(null);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [imgIndex, setImgIndex] = useState(0);

  const places: Place[] = [
    {
      name: "Hà Nội",
      lat: 21.0285,
      lng: 105.8542,
      images: [
        "/images/hanoi1.jpg",
        "/images/hanoi2.jpg",
        "/images/hanoi3.jpg",
      ],
    },
    {
      name: "Đà Nẵng",
      lat: 16.0471,
      lng: 108.2068,
      images: [
        "/images/danang1.jpg",
        "/images/danang2.jpg",
        "/images/danang3.jpg",
      ],
    },
    {
      name: "TP. HCM",
      lat: 10.7626,
      lng: 106.6602,
      images: ["/images/hcm1.jpg", "/images/hcm2.jpg", "/images/hcm3.jpg"],
    },
  ];

  useEffect(() => {
    (async () => {
      const Globe = (await import("globe.gl")).default;
      const container = globeRef.current!;
      const world = new Globe(container)
        .globeImageUrl("//unpkg.com/three-globe/example/img/earth-day.jpg")
        .width(container.offsetWidth)
        .height(container.offsetHeight)
        .pointsData(places)
        .pointAltitude(0.03)
        .pointRadius(0.45)
        .pointColor(() => "red")
        .pointLabel((d: any) => d.name)
        .onPointClick((point: any) => {
          const p = point as Place;
          setSelectedPlace(p);
          setImgIndex(0);
        });

      requestAnimationFrame(() => {
        world.pointOfView({ lat: 15, lng: 108, altitude: 2.4 });
      });
      world.controls().autoRotate = true;
      world.controls().autoRotateSpeed = 0.25;

      const handleResize = () => {
        world.width(container.offsetWidth).height(container.offsetHeight);
      };
      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    })();
  }, []);

  const nextImg = () => {
    if (!selectedPlace) return;
    setImgIndex((i) => (i + 1) % selectedPlace.images.length);
  };

  const prevImg = () => {
    if (!selectedPlace) return;
    setImgIndex((i) => (i === 0 ? selectedPlace.images.length - 1 : i - 1));
  };

  return (
    <section className="visited-layout">
      <div className="visited-left">
        <h1 className="visited-title">Visited Places 🌐</h1>
        <div ref={globeRef} className="visited-globe"></div>

        {selectedPlace && (
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
              {selectedPlace.name} — {imgIndex + 1} /{" "}
              {selectedPlace.images.length}
            </div>
          </div>
        )}
      </div>

      <div className="visited-right">
        <h2>💬 Travel Assistant</h2>
        <p>
          Ask your AI travel buddy for insights and memories of your journeys!
        </p>
        <div className="chat-box">
          <div className="chat-message bot">
            👋 Hi! Want to review your trips?
          </div>
          <div className="chat-message user">
            Yes, show me my Vietnam trips!
          </div>
          <div className="chat-input">
            <input type="text" placeholder="Type a message..." />
            <button>Send</button>
          </div>
        </div>
      </div>
    </section>
  );
}
