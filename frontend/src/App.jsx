import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ChatBot from "./Chatbot";
import Login from "./pages/Login";
import Register from "./pages/Register";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = () => {
      const hasToken = !!localStorage.getItem("access");
      setIsLoggedIn(hasToken);
      setIsLoading(false);

    };

    const timer = setTimeout(checkAuthStatus, 1000);
    
    return () => clearTimeout(timer);
  }, []); 

  if (isLoading) {
    return <h1>loading the chotbot</h1>;
  }

  return (
    <Router>
      {!isLoggedIn ? (
        <div className="main-container">
          <div className="auth-container">
            {isRegistering ? (
              <>
                <Register onRegister={() => setIsRegistering(false)} />
                <p>
                  Already have an account?{" "}
                  <button onClick={() => setIsRegistering(false)}>Login</button>
                </p>
              </>
            ) : (
              <>
                <Login onLogin={() => setIsLoggedIn(true)} />
                <p>
                  Don't have an account?{" "}
                  <button onClick={() => setIsRegistering(true)}>Register</button>
                </p>
              </>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="main-content">
          <Routes>
            <Route path="/" element={<ChatBot />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
          </div>
        </>
      )}
    </Router>
  );
}

export default App;