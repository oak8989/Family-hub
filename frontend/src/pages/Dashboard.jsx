import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Calendar, ShoppingCart, CheckSquare, FileText, MessageCircle,
  DollarSign, Utensils, BookOpen, List, Users, Image, Package, Lightbulb,
  ArrowRight, Plus
} from 'lucide-react';
import { calendarAPI, tasksAPI, shoppingAPI, budgetAPI, notesAPI } from '../lib/api';

const modules = [
  { path: '/calendar', icon: Calendar, label: 'Calendar', color: 'bg-terracotta', desc: 'Family events' },
  { path: '/shopping', icon: ShoppingCart, label: 'Shopping', color: 'bg-sage', desc: 'Shared list' },
  { path: '/tasks', icon: CheckSquare, label: 'Tasks', color: 'bg-sunny', desc: 'To-dos' },
  { path: '/notes', icon: FileText, label: 'Notes', color: 'bg-purple-400', desc: 'Shared notes' },
  { path: '/messages', icon: MessageCircle, label: 'Messages', color: 'bg-blue-400', desc: 'Family chat' },
  { path: '/budget', icon: DollarSign, label: 'Budget', color: 'bg-green-500', desc: 'Track finances' },
  { path: '/meals', icon: Utensils, label: 'Meals', color: 'bg-orange-400', desc: 'Plan meals' },
  { path: '/recipes', icon: BookOpen, label: 'Recipes', color: 'bg-pink-400', desc: 'Recipe box' },
  { path: '/grocery', icon: List, label: 'Grocery', color: 'bg-teal-400', desc: 'Quick list' },
  { path: '/contacts', icon: Users, label: 'Contacts', color: 'bg-indigo-400', desc: 'Address book' },
  { path: '/photos', icon: Image, label: 'Photos', color: 'bg-rose-400', desc: 'Family gallery' },
  { path: '/pantry', icon: Package, label: 'Pantry', color: 'bg-amber-500', desc: 'Inventory' },
  { path: '/suggestions', icon: Lightbulb, label: 'Ideas', color: 'bg-cyan-500', desc: 'Meal ideas' },
];

const Dashboard = () => {
  const { user, family } = useAuth();
  const [stats, setStats] = useState({
    events: 0,
    tasks: 0,
    shopping: 0,
    balance: 0,
    notes: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [eventsRes, tasksRes, shoppingRes, budgetRes, notesRes] = await Promise.all([
          calendarAPI.getEvents().catch(() => ({ data: [] })),
          tasksAPI.getTasks().catch(() => ({ data: [] })),
          shoppingAPI.getItems().catch(() => ({ data: [] })),
          budgetAPI.getSummary().catch(() => ({ data: { balance: 0 } })),
          notesAPI.getNotes().catch(() => ({ data: [] }))
        ]);

        setStats({
          events: eventsRes.data?.length || 0,
          tasks: tasksRes.data?.filter(t => !t.completed)?.length || 0,
          shopping: shoppingRes.data?.filter(i => !i.checked)?.length || 0,
          balance: budgetRes.data?.balance || 0,
          notes: notesRes.data?.length || 0
        });
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
      setLoading(false);
    };

    loadStats();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-8" data-testid="dashboard">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-heading font-bold text-navy">
            {getGreeting()}, {user?.name?.split(' ')[0] || 'Friend'}!
          </h1>
          <p className="text-navy-light mt-1 font-handwritten text-xl">
            Welcome to {family?.name || 'your Family Hub'}
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link to="/calendar" className="module-card card-hover" data-testid="stat-events">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-terracotta/10 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-terracotta" />
            </div>
            <div>
              <p className="text-2xl font-heading font-bold text-navy">
                {loading ? '...' : stats.events}
              </p>
              <p className="text-sm text-navy-light">Events</p>
            </div>
          </div>
        </Link>

        <Link to="/tasks" className="module-card card-hover" data-testid="stat-tasks">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-sage/10 rounded-xl flex items-center justify-center">
              <CheckSquare className="w-6 h-6 text-sage" />
            </div>
            <div>
              <p className="text-2xl font-heading font-bold text-navy">
                {loading ? '...' : stats.tasks}
              </p>
              <p className="text-sm text-navy-light">Open Tasks</p>
            </div>
          </div>
        </Link>

        <Link to="/shopping" className="module-card card-hover" data-testid="stat-shopping">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-sunny/30 rounded-xl flex items-center justify-center">
              <ShoppingCart className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-heading font-bold text-navy">
                {loading ? '...' : stats.shopping}
              </p>
              <p className="text-sm text-navy-light">To Buy</p>
            </div>
          </div>
        </Link>

        <Link to="/budget" className="module-card card-hover" data-testid="stat-budget">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className={`text-2xl font-heading font-bold ${stats.balance >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                {loading ? '...' : `$${Math.abs(stats.balance).toFixed(0)}`}
              </p>
              <p className="text-sm text-navy-light">Balance</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Modules Grid */}
      <div>
        <h2 className="text-xl font-heading font-bold text-navy mb-4">Family Modules</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {modules.map((module, index) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.path}
                to={module.path}
                className="module-card card-hover group"
                style={{ animationDelay: `${index * 50}ms` }}
                data-testid={`module-${module.path.slice(1)}`}
              >
                <div className={`w-12 h-12 ${module.color} rounded-xl flex items-center justify-center mb-3 shadow-sm group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-heading font-bold text-navy">{module.label}</h3>
                <p className="text-sm text-navy-light">{module.desc}</p>
                <ArrowRight className="w-4 h-4 text-terracotta mt-2 opacity-0 group-hover:opacity-100 transition-opacity" />
              </Link>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card-cozy">
        <h2 className="text-xl font-heading font-bold text-navy mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/calendar"
            className="btn-secondary flex items-center gap-2"
            data-testid="quick-add-event"
          >
            <Plus className="w-4 h-4" />
            Add Event
          </Link>
          <Link
            to="/shopping"
            className="btn-secondary flex items-center gap-2"
            data-testid="quick-add-shopping"
          >
            <Plus className="w-4 h-4" />
            Shopping Item
          </Link>
          <Link
            to="/tasks"
            className="btn-secondary flex items-center gap-2"
            data-testid="quick-add-task"
          >
            <Plus className="w-4 h-4" />
            New Task
          </Link>
          <Link
            to="/pantry"
            className="btn-secondary flex items-center gap-2"
            data-testid="quick-scan"
          >
            <Package className="w-4 h-4" />
            Scan Item
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
