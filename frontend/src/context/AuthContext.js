import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, familyAPI } from '../lib/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [family, setFamily] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      loadFamily();
    }
    setLoading(false);
  }, []);

  const loadFamily = async () => {
    try {
      const response = await familyAPI.get();
      setFamily(response.data);
    } catch (error) {
      console.error('Failed to load family:', error);
    }
  };

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const { token, user: userData } = response.data;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
    await loadFamily();
    return response.data;
  };

  const pinLogin = async (pin) => {
    const response = await authAPI.pinLogin(pin);
    const { token, family: familyData } = response.data;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify({ id: 'guest', name: 'Family Member' }));
    setUser({ id: 'guest', name: 'Family Member' });
    setFamily(familyData);
    setIsAuthenticated(true);
    return response.data;
  };

  const register = async (name, email, password) => {
    const response = await authAPI.register({ name, email, password });
    return response.data;
  };

  const createFamily = async (name, pin) => {
    const response = await familyAPI.create({ name, pin });
    setFamily(response.data);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setFamily(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    family,
    loading,
    isAuthenticated,
    login,
    pinLogin,
    register,
    createFamily,
    logout,
    loadFamily,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
