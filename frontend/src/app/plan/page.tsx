"use client";
import "@/styles/plan.css";
import { useLanguage } from "@/contexts/LanguageContext";

export default function PlanPage() {
  const { t } = useLanguage();
  
  const plans = [
    { id: 1, place: "Phú Quốc", date: "2025-11-02", note: t("beachTrip") },
    {
      id: 2,
      place: "Sa Pa",
      date: "2026-01-10",
      note: t("hikingCold"),
    },
  ];

  return (
    <section className="plan-layout">
      {/* ===== LEFT: Travel Plans ===== */}
      <div className="plan-left">
        <h1 className="plan-title">{t("travelPlans")}</h1>
        <p className="plan-subtext">
          {t("managePlans")}
        </p>

        <table className="plan-table">
          <thead>
            <tr>
              <th>{t("destination")}</th>
              <th>{t("date")}</th>
              <th>{t("notes")}</th>
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
        <h2>{t("tripPlanner")}</h2>
        <p>
          {t("tripPlannerDesc")}
        </p>

        <div className="chat-box">
          <div className="chat-message bot">
            {t("plannerGreeting")}
          </div>
          <div className="chat-message user">{t("plannerExample")}</div>

          <div className="chat-input">
            <input type="text" placeholder={t("typeQuestion")} />
            <button>{t("send")}</button>
          </div>
        </div>
      </div>
    </section>
  );
}
