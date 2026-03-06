import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Home, Calendar, ShoppingCart, CheckSquare, FileText,
  DollarSign, Utensils, BookOpen, List, Users, Package, Lightbulb,
  Menu, X, LogOut, ChevronRight, Settings, Award
} from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';

const navItems = [
  { path: '/dashboard', icon: Home, label: 'Dashboard' },
  { path: '/calendar', icon: Calendar, label: 'Calendar' },
  { path: '/shopping', icon: ShoppingCart, label: 'Shopping List' },
  { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
  { path: '/chores', icon: Award, label: 'Chores & Rewards' },
  { path: '/notes', icon: FileText, label: 'Notes' },
  { path: '/budget', icon: DollarSign, label: 'Budget' },
  { path: '/meals', icon: Utensils, label: 'Meal Planner' },
  { path: '/recipes', icon: BookOpen, label: 'Recipe Box' },
  { path: '/grocery', icon: List, label: 'Grocery List' },
  { path: '/contacts', icon: Users, label: 'Contacts' },
  { path: '/pantry', icon: Package, label: 'Pantry' },
  { path: '/suggestions', icon: Lightbulb, label: 'Meal Ideas' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

const Layout = ({ children }) => {
  const { user, family, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const NavLink = ({ item }) => {
    const isActive = location.pathname === item.path;
    const Icon = item.icon;

    return (
      <Link
        to={item.path}
        className={`sidebar-link ${isActive ? 'active' : ''}`}
        onClick={() => setSidebarOpen(false)}
        data-testid={`nav-${item.path.slice(1)}`}
      >
        <Icon className="w-5 h-5" />
        <span className="font-medium">{item.label}</span>
        {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-cream flex">
      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-warm-white rounded-xl shadow-card"
        data-testid="mobile-menu-toggle"
      >
        {sidebarOpen ? <X className="w-6 h-6 text-navy" /> : <Menu className="w-6 h-6 text-navy" />}
      </button>

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-warm-white border-r border-sunny/30
          transform transition-transform duration-300 ease-in-out
          lg:relative lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-sunny/30">
            <Link to="/dashboard" className="flex items-center gap-3" data-testid="sidebar-logo">
              <div className="w-10 h-10 bg-terracotta rounded-xl flex items-center justify-center shadow-sm">
                <Home className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-heading font-bold text-navy text-lg">
                  {family?.name || 'Family Hub'}
                </h1>
                <p className="text-xs text-navy-light">Your digital home</p>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <ScrollArea className="flex-1 px-3 py-4">
            <nav className="space-y-1">
              {navItems.map((item) => (
                <NavLink key={item.path} item={item} />
              ))}
            </nav>
          </ScrollArea>

          {/* User section */}
          <div className="p-4 border-t border-sunny/30">
            <div className="flex items-center gap-3 mb-3">
              <Avatar className="w-10 h-10 border-2 border-sunny">
                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.avatar_seed || user?.id}`} />
                <AvatarFallback className="bg-sage text-white">
                  {user?.name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-navy truncate">{user?.name || 'Family Member'}</p>
                <p className="text-xs text-navy-light truncate capitalize">{user?.role || 'member'} • {user?.points || 0} pts</p>
              </div>
            </div>
            <Button
              variant="ghost"
              onClick={logout}
              className="w-full justify-start text-navy-light hover:text-terracotta hover:bg-terracotta/10"
              data-testid="logout-btn"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-navy/30 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="flex-1 min-h-screen overflow-auto pb-20 lg:pb-0">
        <div className="p-4 lg:p-8 pt-16 lg:pt-8">
          {children}
        </div>
      </main>

      {/* Mobile bottom navigation - Show 5 most used items */}
      <nav className="mobile-nav lg:hidden" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
        <div className="flex justify-around py-2 px-1">
          {[
            navItems[0],  // Dashboard
            navItems[1],  // Calendar
            navItems[3],  // Tasks
            navItems[4],  // Chores
            navItems[13]  // Settings
          ].map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-item ${isActive ? 'active' : 'text-navy-light'}`}
                data-testid={`mobile-nav-${item.path.slice(1)}`}
              >
                <div className={`mobile-nav-icon p-2 rounded-xl ${isActive ? 'bg-terracotta/10' : ''}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-xs">{item.label.split(' ')[0]}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default Layout;
