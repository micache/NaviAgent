import "@/styles/home.css";
import Image from "next/image";
import "@/styles/features.css";

export default function HomePage() {
  return (
    <main className="home-page">
      {/* Hero section */}
      <section className="hero">
        <div className="hero-overlay">
          <h1 className="hero-title">NaviAgent Travel</h1>
          <p className="hero-subtitle">
            Plan smarter, travel further — Trợ lý du lịch thông minh của bạn.
          </p>
          <a href="#features" className="hero-btn">
            Khám phá ngay
          </a>
        </div>
      </section>

      {/* Features section */}
      <div className="features-section">
        <h2 className="features-title">Tính năng nổi bật</h2>

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
            <h3>🌍 Travel Map</h3>
            <p>
              Khám phá và nhìn lại hành trình của bạn trên bản đồ 3D tương tác.
              Ghim những nơi bạn từng đến và xem lại hành trình du lịch của mình
              một cách sinh động.
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
            <h3>🤖 AI Trip Planner</h3>
            <p>
              Nhập điểm đến, ngân sách, sở thích và để AI tự động xây dựng lịch
              trình hoàn hảo — từ timeline đến chi phí chi tiết cho chuyến đi.
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
            <h3>🎯 Destination Finder</h3>
            <p>
              Chưa biết đi đâu? Hệ thống thông minh gợi ý điểm đến lý tưởng dựa
              trên sở thích và ngân sách của bạn.
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
            <h3>🗂️ Xây dựng kế hoạch chuyên nghiệp</h3>
            <p>
              Tạo và chỉnh sửa kế hoạch du lịch chi tiết — bao gồm lịch trình,
              chi phí, lưu ý và gợi ý dịch vụ liên quan, giúp bạn sẵn sàng cho
              hành trình tiếp theo.
            </p>
          </div>
        </section>
        <button className="explore-btn">Create Plan</button>
      </div>
    </main>
  );
}
