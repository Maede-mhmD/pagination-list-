import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DataTable from "./DataTable";
import CreateUserPage from "./CreateUser";


export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DataTable />} />
        <Route path="/create-user" element={<CreateUserPage />} />
      </Routes>
    </Router>
  );
}