import React, { useState } from "react";
import "./index.css";

export default function CreateUserPage() {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    city: "",
    job: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setMessage("کاربر با موفقیت اضافه شد.");
        setFormData({ name: "", age: "", city: "", job: "" });
      } else {
        const errorData = await response.json();
        setMessage(`خطا: ${errorData.error}`);
      }
    } catch (error) {
      setMessage(`خطا در ارتباط با سرور: ${error.message}`);
    }
  };

  return (
    <div className="add-user-container" dir="rtl">
      <div className="add-user-title">افزودن کاربر جدید</div>
      <form className="add-user-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label> نام و نام خانوادگی:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>سن:</label>
          <input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>شهر:</label>
          <input
            type="text"
            name="city"
            value={formData.city}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>شغل:</label>
          <input
            type="text"
            name="job"
            value={formData.job}
            onChange={handleChange}
            required
          />
        </div>
        <button className="add-user-btn-submit" type="submit">افزودن</button>
      </form>
      {message && <div className="add-user-message">{message}</div>}
    </div>
  );
}