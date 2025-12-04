"use client";
import "@/styles/home.css";
import Image from "next/image";
import "@/styles/features.css";
import { useLanguage } from "@/contexts/LanguageContext";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <main className="home-page">
      {/* Hero section */}
      <section className="hero">
        <div className="hero-overlay">
          <h1 className="hero-title">{t("heroTitle")}</h1>
          <p className="hero-subtitle">
            {t("heroSubtitle")}
          </p>
          <a href="#features" className="hero-btn">
            {t("exploreNow")}
          </a>
        </div>
      </section>

      {/* Features section */}
      <div className="features-section">
        <h2 className="features-title">{t("featuresTitle")}</h2>

        {/* 1️⃣ Travel Map */}
        <section className="feature-row">
          <div className="feature-image">
            <Image
              src="/images/earth2.png"
              alt="Travel Map"
              width={200}
              height={200}
            />
          </div>
          <div className="feature-text">
            <h3>{t("travelMapTitle")}</h3>
            <p>
              {t("travelMapDesc")}
            </p>
          </div>
        </section>

        {/* 2️⃣ AI Trip Planner */}
        <section className="feature-row reverse">
          <div className="feature-image">
            <Image
              src="/images/aitrip.jpg"
              alt="AI Trip Planner"
              width={200}
              height={200}
            />
          </div>
          <div className="feature-text">
            <h3>{t("aiPlannerTitle")}</h3>
            <p>
              {t("aiPlannerDesc")}
            </p>
          </div>
        </section>

        {/* 3️⃣ Destination Finder */}
        <section className="feature-row">
          <div className="feature-image">
            <Image
              src="/images/destination.jpg"
              alt="Destination Finder"
              width={200}
              height={200}
            />
          </div>
          <div className="feature-text">
            <h3>{t("destinationGuideTitle")}</h3>
            <p>
              {t("destinationGuideDesc")}
            </p>
          </div>
        </section>

        {/* 4️⃣ Professional Planning */}
        <section className="feature-row reverse">
          <div className="feature-image">
            <Image
              src="/images/plan3.png"
              alt="Professional Planning"
              width={200}
              height={200}
            />
          </div>
          <div className="feature-text">
            <h3>{t("planTitle")}</h3>
            <p>
              {t("planDesc")}
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
