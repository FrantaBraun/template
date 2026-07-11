import { Route, Routes } from "react-router-dom"
import HomePage from "./pages/HomePage"
import Layout from "./components/Layout"
import Login from "./pages/Login"
import Version from "./pages/Version"


function App() {
  return (<Layout>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<Login />} />
      {/* Publicly accessible, hidden from regular nav */}
      <Route path="/version" element={<Version />} />
    </Routes>

  </Layout>
  )
}

export default App
