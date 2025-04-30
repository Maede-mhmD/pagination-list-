// App.js - با تغییرات برای مدیریت بهتر خطاها
import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import "./index.css";

export default function DataTable() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [filters, setFilters] = useState({ name: "", city: "", job: "", age: "" });
  const [connectionStatus, setConnectionStatus] = useState('در حال اتصال...');
  
  const itemsPerPage = 5;
  // برای اطمینان از آدرس صحیح API
  const apiUrl = "http://127.0.0.1:5000/api/users";

  // تست اولیه اتصال به سرور
  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/");
        if (response.ok) {
          setConnectionStatus('اتصال به سرور برقرار است');
          console.log('اتصال به سرور برقرار است');
        } else {
          setConnectionStatus(`خطا در اتصال: ${response.status}`);
          console.error(`خطا در اتصال: ${response.status}`);
        }
      } catch (err) {
        setConnectionStatus(`خطا در اتصال: ${err.message}`);
        console.error('خطا در اتصال:', err);
      }
    };
    
    testConnection();
  }, []);

  // تابع برای دریافت داده‌ها از API با مدیریت بهتر خطاها
  const fetchData = async () => {
    setLoading(true);
    try {
      // ساخت پارامترهای URL برای فیلترها و صفحه‌بندی
      const queryParams = new URLSearchParams({
        page: currentPage,
        per_page: itemsPerPage,
        name: filters.name,
        city: filters.city,
        job: filters.job,
        age: filters.age
      });
      
      console.log(`درخواست به آدرس: ${apiUrl}?${queryParams}`);
      
      const response = await fetch(`${apiUrl}?${queryParams}`);
      console.log('وضعیت پاسخ:', response.status);
      
      if (!response.ok) {
        throw new Error(`خطا در دریافت اطلاعات از سرور: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('داده‌های دریافتی:', result);
      
      setData(result.items || []);
      setTotalPages(result.total_pages || 0);
      setTotalItems(result.total_items || 0);
      setError(null);
    } catch (err) {
      console.error('خطای کامل:', err);
      setError(`خطا در دریافت داده‌ها: ${err.message}`);
      setData([]);
      setTotalPages(0);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  };

  // اجرای تابع دریافت داده‌ها هنگام تغییر صفحه یا فیلترها
  useEffect(() => {
    fetchData();
  }, [currentPage, filters]);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({ name: "", city: "", job: "", age: "" });
    setCurrentPage(1);
  };

  return (
    <div className="container" dir="rtl">
      <h1 className="title">لیست اطلاعات کاربران</h1>
      
      {/* نمایش وضعیت اتصال */}
      {/* <div className={`connection-status ${connectionStatus.includes('خطا') ? 'error' : 'success'}`}>
        {connectionStatus}
      </div> */}

      <div className="filter-box">
        <div className="filter-field">
          <label>نام:</label>
          <div className="input-icon">
            <input
              type="text"
              value={filters.name}
              onChange={(e) => handleFilterChange("name", e.target.value)}
            />
            <Search size={16} />
          </div>
        </div>

        <div className="filter-field">
          <label>شهر:</label>
          <div className="input-icon">
            <input
              type="text"
              value={filters.city}
              onChange={(e) => handleFilterChange("city", e.target.value)}
            />
            <Search size={16} />
          </div>
        </div>

        <div className="filter-field">
          <label>شغل:</label>
          <div className="input-icon">
            <input
              type="text"
              value={filters.job}
              onChange={(e) => handleFilterChange("job", e.target.value)}
            />
            <Search size={16} />
          </div>
        </div>

        <div className="filter-field">
          <label>سن:</label>
          <div className="input-icon">
            <input
              type="number"
              value={filters.age}
              onChange={(e) => handleFilterChange("age", e.target.value)}
            />
            <Search size={16} />
          </div>
        </div>

        <button className="clear-btn" onClick={clearFilters}>
          پاک کردن فیلترها
        </button>
      </div>

      <div className="table-wrapper">
        {loading ? (
          <div className="loading">در حال بارگذاری...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ردیف</th>
                <th>نام</th>
                <th>سن</th>
                <th>شهر</th>
                <th>شغل</th>
              </tr>
            </thead>
            <tbody>
              {data.length > 0 ? (
                data.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.name}</td>
                    <td>{item.age}</td>
                    <td>{item.city}</td>
                    <td>{item.job}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="no-data">
                    هیچ داده‌ای یافت نشد
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {totalPages > 0 && (
        <div className="pagination">
          <span>
            نمایش {(currentPage - 1) * itemsPerPage + 1} تا{" "}
            {Math.min(currentPage * itemsPerPage, totalItems)} از{" "}
            {totalItems} مورد
          </span>

          <div className="page-buttons">
            <button onClick={() => goToPage(1)} disabled={currentPage === 1}>
              ابتدا
            </button>
            <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
              قبلی
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => goToPage(page)}
                className={currentPage === page ? "active" : ""}
              >
                {page}
              </button>
            ))}

            <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>
              بعدی
            </button>
            <button onClick={() => goToPage(totalPages)} disabled={currentPage === totalPages}>
              انتها
            </button>
          </div>
        </div>
      )}
      
      {/* دکمه برای تلاش مجدد در صورت خطا */}
      {error && (
        <div className="retry-section">
          <button className="retry-btn" onClick={fetchData}>
            تلاش مجدد
          </button>
        </div>
      )}
    </div>
  );
}