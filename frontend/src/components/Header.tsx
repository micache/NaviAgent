"use client";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import "@/styles/header.css";
import Link from "next/link";
import Image from "next/image";
import passwordShow from "@/images/password-show.svg";
import passwordHide from "@/images/password-hide.svg";

// API URLs for different backend services
const USER_API_URL = process.env.NEXT_PUBLIC_USER_API_URL || "http://localhost:8000";
// const RECEPTION_API_URL = process.env.NEXT_PUBLIC_RECEPTION_API_URL || "http://localhost:8001";
// const TRAVEL_PLANNER_API_URL = process.env.NEXT_PUBLIC_TRAVEL_PLANNER_API_URL || "http://localhost:8002";
// const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || "http://localhost:8003";

// Email validation regex - must contain @
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 6;

interface AuthUser {
  email: string;
  access_token: string;
}

export default function Header() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    // Check if user is logged in from localStorage
    const loggedUser = localStorage.getItem("user");
    if (loggedUser) {
      try {
        setUser(JSON.parse(loggedUser));
      } catch {
        localStorage.removeItem("user");
      }
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

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setIsLoading(true);

    // Validate email format
    if (!EMAIL_REGEX.test(email)) {
      setErrorMessage("Please enter a valid email address");
      setIsLoading(false);
      return;
    }

    // Validate password length
    if (password.length < MIN_PASSWORD_LENGTH) {
      setErrorMessage(`Password must be at least ${MIN_PASSWORD_LENGTH} characters`);
      setIsLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        // Sign Up - call /auth/register
        if (password !== confirmPassword) {
          setErrorMessage("Passwords do not match!");
          setIsLoading(false);
          return;
        }

        const response = await fetch(`${USER_API_URL}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || "Registration failed");
        }

        // After successful registration, auto login
        const loginResponse = await fetch(`${USER_API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!loginResponse.ok) {
          // Registration succeeded but login failed - user can login manually
          alert("Account created! Please sign in.");
          toggleAuthMode();
          setIsLoading(false);
          return;
        }

        const loginData = await loginResponse.json();
        
        // Validate response has access_token
        if (!loginData.access_token) {
          throw new Error("Invalid server response: missing access token");
        }

        const newUser: AuthUser = {
          email,
          access_token: loginData.access_token,
        };
        localStorage.setItem("user", JSON.stringify(newUser));
        setUser(newUser);
        closeModal();
      } else {
        // Sign In - call /auth/login
        const response = await fetch(`${USER_API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || "Invalid email or password");
        }

        const data = await response.json();
        
        // Validate response has access_token
        if (!data.access_token) {
          throw new Error("Invalid server response: missing access token");
        }

        const loggedUser: AuthUser = {
          email,
          access_token: data.access_token,
        };
        localStorage.setItem("user", JSON.stringify(loggedUser));
        setUser(loggedUser);
        closeModal();
      }
    } catch (error) {
      // Handle network errors vs API errors
      if (error instanceof TypeError && error.message.includes("fetch")) {
        setErrorMessage("Cannot connect to server. Please check your connection.");
      } else {
        setErrorMessage(error instanceof Error ? error.message : "An error occurred");
      }
    } finally {
      setIsLoading(false);
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
    setErrorMessage("");
  };

  const handleLogout = async () => {
    if (!user) return;
    
    try {
      await fetch(`${USER_API_URL}/auth/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${user.access_token}`,
        },
      });
    } catch {
      // Logout locally even if API call fails
    }
    
    localStorage.removeItem("user");
    setUser(null);
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
            {errorMessage && (
              <div className="auth-error">{errorMessage}</div>
            )}
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
              <button type="submit" className="auth-submit-btn" disabled={isLoading}>
                {isLoading ? "Loading..." : (isSignUp ? "Sign Up" : "Sign In")}
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
