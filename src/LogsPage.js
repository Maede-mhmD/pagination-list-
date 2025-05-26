import React, { useEffect, useState } from "react";
import "./LogsPage.css";

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/logs", {
      credentials: "include"
    })
      .then(res => {
        if (!res.ok) throw new Error("خطا در دریافت لاگ‌ها");
        return res.json();
      })
      .then(data => {
        setLogs(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="logs-container" dir="rtl">
      <h2>لاگ اکشن کاربران</h2>
      {loading && <div>در حال بارگذاری...</div>}
      {error && <div className="error">{error}</div>}
      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>اکشن</th>
              <th>شماره ردیف </th>
              <th>توضیحات</th>
              <th>زمان</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{log.action}</td>
                <td>{log.affected_id || "-"}</td>
                <td>{log.details}</td>
                <td>{log.timestamp ? new Date(log.timestamp).toLocaleString("fa-IR", { timeZone:"Asia/Tehran" }) : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}