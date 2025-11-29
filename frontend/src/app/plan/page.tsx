"use client";
import "@/styles/plan.css";

export default function PlanPage() {
  const plans = [
    { id: 1, place: "Phú Quốc", date: "2025-11-02", note: "3-day beach trip" },
    {
      id: 2,
      place: "Sa Pa",
      date: "2026-01-10",
      note: "Hiking and cold weather",
    },
  ];

  return (
    <section className="plan-layout">
      {/* ===== LEFT: Travel Plans ===== */}
      <div className="plan-left">
        <h1 className="plan-title">Travel Plans 📅</h1>
        <p className="plan-subtext">
          Manage your upcoming trips and prepare your journey.
        </p>

        <table className="plan-table">
          <thead>
            <tr>
              <th>Destination</th>
              <th>Date</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((p) => (
              <tr key={p.id}>
                <td>{p.place}</td>
                <td>{p.date}</td>
                <td>{p.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ===== RIGHT: Chatbot Assistant ===== */}
      <div className="plan-right">
        <h2>💬 Trip Planner Assistant</h2>
        <p>
          Ask our assistant to create a detailed itinerary, estimate budget, or
          suggest destinations for your next adventure!
        </p>

        <div className="chat-box">
          <div className="chat-message bot">
            👋 Hi there! Need help planning your next trip?
          </div>
          <div className="chat-message user">Yes, recommend a 3-day trip!</div>

          <div className="chat-input">
            <input type="text" placeholder="Type your question..." />
            <button>Send</button>
          </div>
        </div>
      </div>
    </section>
  );
}
