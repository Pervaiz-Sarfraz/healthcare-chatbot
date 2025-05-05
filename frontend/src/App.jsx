import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Loader from "./comp/Loader";
import ChatBot from "./Chatbot";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = () => {
      const accessToken = localStorage.getItem("access");
      setIsLoggedIn(!!accessToken);
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  if (isLoading) {
    return <Loader />;
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={!isLoggedIn ? <Login onLogin={() => setIsLoggedIn(true)} /> : <Navigate to="/" />} 
        />
        <Route 
          path="/register" 
          element={!isLoggedIn ? <Register onRegister={() => setIsLoggedIn(true)} /> : <Navigate to="/" />} 
        />
        <Route 
          path="/" 
          element={isLoggedIn ? <ChatBot /> : <Navigate to="/login" />} 
        />
      </Routes>
    </Router>
  );
}

export default App;