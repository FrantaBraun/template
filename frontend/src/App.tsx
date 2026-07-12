import { Route, Routes } from "react-router-dom"
import HomePage from "./pages/HomePage"
import Layout from "./components/Layout"
import Account from "./pages/Account"
import Consent from "./pages/Consent"
import ConsentRejected from "./pages/ConsentRejected"
import Login from "./pages/Login"
import Register from "./pages/Register"
import OAuthCallback from "./pages/OAuthCallback"
import Version from "./pages/Version"


function App() {
  return (<Layout>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/account" element={<Account />} />
      <Route path="/oauth/callback" element={<OAuthCallback />} />
      <Route path="/consent" element={<Consent />} />
      <Route path="/consent-rejected" element={<ConsentRejected />} />
      {/* Publicly accessible, hidden from regular nav */}
      <Route path="/version" element={<Version />} />
      <Route path="/consent-callback" element={<Version />} />
    </Routes>

  </Layout>
  )
}

export default App
