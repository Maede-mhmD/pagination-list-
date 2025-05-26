import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./index.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    const response = await fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    if (response.ok) {
      setMessage("ورود موفقیت‌آمیز بود");
      // می‌توانی کاربر را به صفحه اصلی هدایت کنی
    } else {
      setMessage(data.error || "خطا در ورود");
    }
  };

  return (
    <div className="loging-user-container" dir="rtl">
        <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="نام کاربری"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="رمز عبور"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />
      <button type="submit">ورود</button>
      {message && <div>{message}</div>}
      </form>
      <Link to="/" className = "back-to-main-page">بازگشت به صفحه اصلی  </Link> 
      </div>
  );
}