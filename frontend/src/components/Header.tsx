"use client";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import "@/styles/header.css";
import Link from "next/link";
import Image from "next/image";
import passwordShow from "@/images/password-show.svg";
import passwordHide from "@/images/password-hide.svg";

export default function Header() {
  const pathname = usePathname(); // 👉 lấy đường dẫn hiện tại
  const [scrolled, setScrolled] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [user, setUser] = useState<{ email: string } | null>(null);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const loggedUser = localStorage.getItem("user");
    if (loggedUser) {
      setUser(JSON.parse(loggedUser));
    }
  }, []);

  useEffect(() => {
    // Chỉ gắn listener khi đang ở trang Home
    if (pathname !== "/") {
      setScrolled(false); // đảm bảo header trắng khi không ở home
      return;
    }
    // thêm console.log trong handler để debug giá trị thực khi scroll
    const handleScroll = () => {
      const isScrolled = window.scrollY > 80;
      setScrolled((prev) => (prev === isScrolled ? prev : isScrolled));
    };
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [pathname]);

  // Nếu không phải trang Home → header luôn là nền trắng
  const isHome = pathname === "/";
  const headerClass = isHome
    ? scrolled
      ? "main-header solid"
      : "main-header transparent"
    : "main-header solid";

  const handleAuthSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isSignUp) {
      // Xử lý Sign Up
      if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
      }
      const newUser = { email };
      localStorage.setItem("user", JSON.stringify(newUser));
      setUser(newUser);
      closeModal();
      alert("Account created successfully!");
    } else {
      // Xử lý Sign In - Check admin credentials
      if (email === "admin@gmail.com" && password === "admin") {
        const loggedUser = { email };
        localStorage.setItem("user", JSON.stringify(loggedUser));
        setUser(loggedUser);
        closeModal();
        alert("Welcome, Admin!");
      } else {
        alert("Invalid email or password!");
      }
    }
  };

  const toggleAuthMode = () => {
    setIsSignUp(!isSignUp);
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  const closeModal = () => {
    setShowAuthModal(false);
    setIsSignUp(false);
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
    alert("Logged out successfully!");
  };

  return (
    <>
      <header className={headerClass}>
        <div className="logo">🌍 AstrAgent</div>
        <nav>
          <Link href="/">Home</Link>
          <Link href="/explore">Explore</Link>
          <Link href="/visited">Visited</Link>
          <Link href="/plan">Plan</Link>
          {user ? (
              <button className="sign-out-btn" onClick={handleLogout}>
                Sign Out
              </button>
          ) : (
            <button 
              className="sign-in-btn"
              onClick={() => setShowAuthModal(true)}
            >
              Sign In
            </button>
          )}
        </nav>
      </header>

      {showAuthModal && (
        <div className="auth-modal-overlay" onClick={closeModal}>
          <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={closeModal}>
              ×
            </button>
            <h2>{isSignUp ? "Sign Up" : "Sign In"}</h2>
            <form onSubmit={handleAuthSubmit}>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="Enter your email"
                />
              </div>
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    className="toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label="Toggle password visibility"
                  >
                    <Image
                      src={showPassword ? passwordShow : passwordHide}
                      alt="Toggle password visibility"
                      width={20}
                      height={20}
                    />
                  </button>
                </div>
              </div>
              {isSignUp && (
                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <div className="password-input-wrapper">
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      id="confirmPassword"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      placeholder="Confirm your password"
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label="Toggle confirm password visibility"
                    >
                      <Image
                        src={showConfirmPassword ? passwordShow : passwordHide}
                        alt="Toggle password visibility"
                        width={20}
                        height={20}
                      />
                    </button>
                  </div>
                </div>
              )}
              <button type="submit" className="auth-submit-btn">
                {isSignUp ? "Sign Up" : "Sign In"}
              </button>
            </form>
            <p className="auth-toggle">
              {isSignUp ? (
                <>
                  Already have an account?{" "}
                  <span onClick={toggleAuthMode}>Sign In</span>
                </>
              ) : (
                <>
                  Don't have an account?{" "}
                  <span onClick={toggleAuthMode}>Sign Up</span>
                </>
              )}
            </p>
          </div>
        </div>
      )}
    </>
  );
}
