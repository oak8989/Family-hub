import React, { useState, useEffect } from 'react';
import { DollarSign, Plus, Trash2, TrendingUp, TrendingDown, PiggyBank, BarChart3 } from 'lucide-react';
import { budgetAPI } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, LineChart, Line, Area, AreaChart
} from 'recharts';

const incomeCategories = ['Salary', 'Freelance', 'Investments', 'Gifts', 'Other Income'];
const expenseCategories = ['Groceries', 'Utilities', 'Rent', 'Transportation', 'Entertainment', 'Healthcare', 'Education', 'Shopping', 'Dining', 'Other'];

const COLORS = ['#E07A5F', '#81B29A', '#F2CC8F', '#3D405B', '#F4F1DE', '#6B705C', '#A5A58D', '#CB997E', '#B7B7A4', '#FFE8D6'];

const BudgetPage = () => {
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState({ total_income: 0, total_expenses: 0, balance: 0, by_category: {}, by_month: {} });
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formType, setFormType] = useState('expense');
  const [formDescription, setFormDescription] = useState('');
  const [formAmount, setFormAmount] = useState('');
  const [formCategory, setFormCategory] = useState('');
  const [formDate, setFormDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const entriesRes = await budgetAPI.getEntries();
      const summaryRes = await budgetAPI.getSummary();
      setEntries(entriesRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      toast.error('Failed to load budget data');
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formDescription.trim() || !formAmount) {
      toast.error('Please fill all required fields');
      return;
    }

    try {
      await budgetAPI.createEntry({
        description: formDescription,
        amount: parseFloat(formAmount),
        category: formCategory,
        type: formType,
        date: formDate
      });
      toast.success('Entry added!');
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      toast.error('Failed to add entry');
    }
  };

  const resetForm = () => {
    setFormDescription('');
    setFormAmount('');
    setFormCategory('');
    setFormDate(new Date().toISOString().split('T')[0]);
  };

  const handleDelete = async (id) => {
    try {
      await budgetAPI.deleteEntry(id);
      loadData();
      toast.success('Entry deleted');
    } catch (error) {
      toast.error('Failed to delete entry');
    }
  };

  const currentCategories = formType === 'income' ? incomeCategories : expenseCategories;

  // Prepare chart data
  const categoryData = Object.entries(summary.by_category || {}).map(([name, data]) => ({
    name,
    income: data.income || 0,
    expense: data.expense || 0,
  })).filter(d => d.income > 0 || d.expense > 0);

  const expensePieData = categoryData
    .filter(d => d.expense > 0)
    .map(d => ({ name: d.name, value: d.expense }));

  const incomePieData = categoryData
    .filter(d => d.income > 0)
    .map(d => ({ name: d.name, value: d.income }));

  const monthlyData = Object.entries(summary.by_month || {})
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, data]) => ({
      month: new Date(month + '-01').toLocaleDateString('en-US', { month: 'short' }),
      income: data.income || 0,
      expense: data.expense || 0,
      balance: (data.income || 0) - (data.expense || 0),
    }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-medium text-navy">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="budget-page">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-navy flex items-center gap-3">
            <DollarSign className="w-8 h-8 text-green-500" />
            Family Budget
          </h1>
          <p className="text-navy-light mt-1">Track your family finances</p>
        </div>
        
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary" data-testid="add-entry-btn">
              <Plus className="w-4 h-4 mr-2" />
              Add Entry
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-warm-white border-sunny/50">
            <DialogHeader>
              <DialogTitle className="font-heading text-navy">Add Budget Entry</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-2 p-1 bg-cream rounded-lg">
                <button
                  type="button"
                  onClick={() => { setFormType('income'); setFormCategory(''); }}
                  className={`flex items-center justify-center gap-2 py-2 px-4 rounded-md font-medium transition-colors ${
                    formType === 'income' ? 'bg-green-500 text-white' : 'text-navy-light hover:bg-sunny/30'
                  }`}
                >
                  <TrendingUp className="w-4 h-4" />
                  Income
                </button>
                <button
                  type="button"
                  onClick={() => { setFormType('expense'); setFormCategory(''); }}
                  className={`flex items-center justify-center gap-2 py-2 px-4 rounded-md font-medium transition-colors ${
                    formType === 'expense' ? 'bg-terracotta text-white' : 'text-navy-light hover:bg-sunny/30'
                  }`}
                >
                  <TrendingDown className="w-4 h-4" />
                  Expense
                </button>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy mb-2">Description</label>
                <Input
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="What was it for?"
                  className="input-cozy"
                  data-testid="budget-description-input"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-navy mb-2">Amount</label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formAmount}
                    onChange={(e) => setFormAmount(e.target.value)}
                    placeholder="0.00"
                    className="input-cozy"
                    data-testid="budget-amount-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-navy mb-2">Category</label>
                  <Select value={formCategory} onValueChange={setFormCategory}>
                    <SelectTrigger className="input-cozy" data-testid="budget-category-select">
                      <SelectValue placeholder="Select" />
                    </SelectTrigger>
                    <SelectContent>
                      {currentCategories.map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy mb-2">Date</label>
                <Input
                  type="date"
                  value={formDate}
                  onChange={(e) => setFormDate(e.target.value)}
                  className="input-cozy"
                  data-testid="budget-date-input"
                />
              </div>
              
              <div className="flex gap-3">
                <Button type="submit" className="btn-primary flex-1" data-testid="save-budget-btn">
                  Add Entry
                </Button>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="border-sunny">
                  Cancel
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-green-700">Total Income</p>
                <p className="text-2xl font-bold text-green-800">${summary.total_income?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-red-700">Total Expenses</p>
                <p className="text-2xl font-bold text-red-800">${summary.total_expenses?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className={summary.balance >= 0 ? 'bg-sage/20 border-sage' : 'bg-terracotta/20 border-terracotta'}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                summary.balance >= 0 ? 'bg-sage/30' : 'bg-terracotta/30'
              }`}>
                <PiggyBank className={`w-6 h-6 ${summary.balance >= 0 ? 'text-sage' : 'text-terracotta'}`} />
              </div>
              <div>
                <p className={`text-sm ${summary.balance >= 0 ? 'text-sage' : 'text-terracotta'}`}>Balance</p>
                <p className={`text-2xl font-bold ${summary.balance >= 0 ? 'text-sage' : 'text-terracotta'}`}>
                  ${Math.abs(summary.balance || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Entries Tabs */}
      <Tabs defaultValue="charts" className="space-y-4">
        <TabsList className="bg-warm-white">
          <TabsTrigger value="charts" className="data-[state=active]:bg-terracotta data-[state=active]:text-white">
            <BarChart3 className="w-4 h-4 mr-2" /> Charts
          </TabsTrigger>
          <TabsTrigger value="entries" className="data-[state=active]:bg-terracotta data-[state=active]:text-white">
            <DollarSign className="w-4 h-4 mr-2" /> Entries
          </TabsTrigger>
        </TabsList>

        <TabsContent value="charts" className="space-y-6">
          {/* Monthly Trend */}
          {monthlyData.length > 0 && (
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="text-navy">Monthly Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F2CC8F" />
                    <XAxis dataKey="month" stroke="#3D405B" />
                    <YAxis stroke="#3D405B" />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Area type="monotone" dataKey="income" stackId="1" stroke="#81B29A" fill="#81B29A" fillOpacity={0.6} name="Income" />
                    <Area type="monotone" dataKey="expense" stackId="2" stroke="#E07A5F" fill="#E07A5F" fillOpacity={0.6} name="Expenses" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Pie Charts */}
          <div className="grid md:grid-cols-2 gap-6">
            {expensePieData.length > 0 && (
              <Card className="card-base">
                <CardHeader>
                  <CardTitle className="text-navy">Expenses by Category</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={expensePieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {expensePieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {incomePieData.length > 0 && (
              <Card className="card-base">
                <CardHeader>
                  <CardTitle className="text-navy">Income by Category</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={incomePieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {incomePieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[(index + 3) % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Category Bar Chart */}
          {categoryData.length > 0 && (
            <Card className="card-base">
              <CardHeader>
                <CardTitle className="text-navy">Income vs Expenses by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categoryData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#F2CC8F" />
                    <XAxis type="number" stroke="#3D405B" />
                    <YAxis dataKey="name" type="category" width={100} stroke="#3D405B" />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar dataKey="income" fill="#81B29A" name="Income" />
                    <Bar dataKey="expense" fill="#E07A5F" name="Expenses" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {categoryData.length === 0 && (
            <Card className="card-base">
              <CardContent className="p-8 text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 text-navy-light" />
                <p className="text-navy-light">Add budget entries to see charts</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="entries">
          <Card className="card-base">
            <CardHeader>
              <CardTitle className="text-navy">Recent Entries</CardTitle>
            </CardHeader>
            <CardContent>
              {entries.length === 0 ? (
                <div className="text-center py-8">
                  <PiggyBank className="w-16 h-16 mx-auto text-sunny mb-4" />
                  <p className="text-navy-light">No entries yet. Start tracking your budget!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {entries.sort((a, b) => new Date(b.date) - new Date(a.date)).map((entry) => (
                    <div
                      key={entry.id}
                      className={`flex items-center justify-between p-4 rounded-xl ${
                        entry.type === 'income' ? 'bg-green-50' : 'bg-red-50'
                      }`}
                      data-testid={`budget-entry-${entry.id}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          entry.type === 'income' ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {entry.type === 'income' ? (
                            <TrendingUp className="w-5 h-5 text-green-600" />
                          ) : (
                            <TrendingDown className="w-5 h-5 text-red-600" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-navy">{entry.description}</p>
                          <p className="text-sm text-navy-light">
                            {entry.category} • {new Date(entry.date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`text-lg font-bold ${
                          entry.type === 'income' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {entry.type === 'income' ? '+' : '-'}${entry.amount.toFixed(2)}
                        </span>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(entry.id)}
                          className="text-red-500 hover:text-red-600 hover:bg-red-100"
                          data-testid={`delete-entry-${entry.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BudgetPage;
