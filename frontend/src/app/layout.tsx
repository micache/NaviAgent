import "@/styles/globals.css";
import "@/styles/home.css";
import "@/styles/explore.css";
import "@/styles/header.css";
import "@/styles/visited.css";
import "@/styles/plan.css";
import Header from "@/components/Header";
import { LanguageProvider } from "@/contexts/LanguageContext";

export const metadata = {
  title: "NaviAgent Travel",
  description: "Your personal travel planner with 3D map and weather info.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body>
        <LanguageProvider>
          <Header />
          {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
