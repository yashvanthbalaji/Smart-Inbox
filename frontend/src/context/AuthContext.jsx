import React, { createContext, useContext, useState } from 'react';
import { setAuthToken } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Token is kept in React state only (not localStorage per project rules)
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = (newToken) => {
    setToken(newToken);
    // Wire the token into the axios client so all API calls carry it automatically
    setAuthToken(newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    // Clear Authorization header from axios
    setAuthToken(null);
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider');
  }
  return context;
}
