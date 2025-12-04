import "@/styles/globals.css";
import "@/styles/home.css";
import "@/styles/explore.css";
import "@/styles/header.css";
import "@/styles/visited.css";
import "@/styles/plan.css";
import Header from "@/components/Header";

export const metadata = {
  title: "AstrAgent Travel",
  description: "Your personal travel planner with 3D map and weather info.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
      </body>
    </html>
  );
}
