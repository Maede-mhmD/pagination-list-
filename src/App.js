import { Routes, Route } from "react-router-dom";
import DataTable from "./DataTable";
import CreateUserPage from "./CreateUser";
import Login from "./Login";      
import LogsPage from "./LogsPage";
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DataTable />} />
      <Route path="/create-user" element={<CreateUserPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/logs" element={<LogsPage />} />
    </Routes>
  );
}