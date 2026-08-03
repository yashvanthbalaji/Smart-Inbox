import React, { createContext, useContext, useState } from 'react';
import { setAuthToken } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Token is kept in sessionStorage to survive page refresh without using localStorage
  const [token, setToken] = useState(() => sessionStorage.getItem('token'));
  const [user, setUser] = useState(null);

  // Wire token on initial load or token changes
  if (token) {
    setAuthToken(token);
  }

  const login = (newToken) => {
    sessionStorage.setItem('token', newToken);
    setToken(newToken);
    setAuthToken(newToken);
  };

  const logout = () => {
    sessionStorage.removeItem('token');
    setToken(null);
    setUser(null);
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
