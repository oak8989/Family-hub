import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { Home, User, Lock, Mail, Users, KeyRound, ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const AuthPage = () => {
  const { login, pinLogin, register, createFamily } = useAuth();
  const [mode, setMode] = useState('pin'); // pin, login, register, setup
  const [loading, setLoading] = useState(false);
  
  // Form states
  const [pin, setPin] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [familyName, setFamilyName] = useState('');
  const [familyPin, setFamilyPin] = useState('');

  const handlePinLogin = async (e) => {
    e.preventDefault();
    if (pin.length < 4) {
      toast.error('PIN must be at least 4 digits');
      return;
    }
    setLoading(true);
    try {
      await pinLogin(pin);
      toast.success('Welcome to your Family Hub!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid PIN');
    }
    setLoading(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(name, email, password);
      toast.success('Account created! Please login.');
      setMode('login');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    }
    setLoading(false);
  };

  const handleSetupFamily = async (e) => {
    e.preventDefault();
    if (familyPin.length < 4) {
      toast.error('Family PIN must be at least 4 digits');
      return;
    }
    setLoading(true);
    try {
      // First login
      await login(email, password);
      // Then create family
      await createFamily(familyName, familyPin);
      toast.success('Family created! Share the PIN with your family members.');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Setup failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-cream flex">
      {/* Left side - Hero image */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1511895426328-dc8714191300?q=80&w=2070&auto=format&fit=crop"
          alt="Happy family"
          className="object-cover w-full h-full"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-terracotta/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-12 bg-gradient-to-t from-navy/80 to-transparent">
          <h2 className="text-4xl font-heading font-bold text-white mb-4">
            Your Family's Digital Home
          </h2>
          <p className="text-white/90 text-lg max-w-md">
            Keep everyone organized, connected, and happy with our all-in-one family hub.
          </p>
        </div>
      </div>

      {/* Right side - Auth forms */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-terracotta rounded-2xl mb-4 shadow-warm">
              <Home className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-heading font-bold text-navy">Family Hub</h1>
            <p className="text-navy-light mt-2">Welcome home!</p>
          </div>

          {/* Auth Card */}
          <div className="card-cozy">
            <Tabs value={mode} onValueChange={setMode} className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-cream rounded-xl p-1 mb-6">
                <TabsTrigger
                  value="pin"
                  className="rounded-lg data-[state=active]:bg-terracotta data-[state=active]:text-white"
                  data-testid="pin-tab"
                >
                  <KeyRound className="w-4 h-4 mr-2" />
                  Family PIN
                </TabsTrigger>
                <TabsTrigger
                  value="login"
                  className="rounded-lg data-[state=active]:bg-terracotta data-[state=active]:text-white"
                  data-testid="login-tab"
                >
                  <User className="w-4 h-4 mr-2" />
                  Account
                </TabsTrigger>
              </TabsList>

              {/* PIN Login */}
              <TabsContent value="pin">
                <form onSubmit={handlePinLogin} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Enter Family PIN
                    </label>
                    <Input
                      type="password"
                      value={pin}
                      onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
                      placeholder="••••"
                      maxLength={6}
                      className="input-cozy text-center text-2xl tracking-widest"
                      data-testid="pin-input"
                    />
                    <p className="text-sm text-navy-light mt-2 text-center font-handwritten">
                      Ask a family member for the PIN!
                    </p>
                  </div>
                  <Button
                    type="submit"
                    disabled={loading || pin.length < 4}
                    className="btn-primary w-full"
                    data-testid="pin-submit"
                  >
                    {loading ? 'Entering...' : 'Enter Home'}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </form>
              </TabsContent>

              {/* Account Login */}
              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-light" />
                      <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        className="input-cozy pl-10"
                        data-testid="login-email"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-light" />
                      <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="input-cozy pl-10"
                        data-testid="login-password"
                      />
                    </div>
                  </div>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full"
                    data-testid="login-submit"
                  >
                    {loading ? 'Logging in...' : 'Sign In'}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </form>

                <div className="mt-6 pt-6 border-t border-sunny/30">
                  <p className="text-center text-navy-light text-sm">
                    New here?{' '}
                    <button
                      onClick={() => setMode('register')}
                      className="text-terracotta font-medium hover:underline"
                      data-testid="goto-register"
                    >
                      Create an account
                    </button>
                  </p>
                </div>
              </TabsContent>

              {/* Register */}
              <TabsContent value="register">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Your Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-light" />
                      <Input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="John Doe"
                        className="input-cozy pl-10"
                        data-testid="register-name"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-light" />
                      <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        className="input-cozy pl-10"
                        data-testid="register-email"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-light" />
                      <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="input-cozy pl-10"
                        data-testid="register-password"
                      />
                    </div>
                  </div>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full"
                    data-testid="register-submit"
                  >
                    {loading ? 'Creating...' : 'Create Account'}
                    <Sparkles className="w-4 h-4 ml-2" />
                  </Button>
                </form>

                <div className="mt-6 pt-6 border-t border-sunny/30">
                  <p className="text-center text-navy-light text-sm">
                    Already have an account?{' '}
                    <button
                      onClick={() => setMode('login')}
                      className="text-terracotta font-medium hover:underline"
                      data-testid="goto-login"
                    >
                      Sign in
                    </button>
                  </p>
                </div>
              </TabsContent>

              {/* Setup Family */}
              <TabsContent value="setup">
                <form onSubmit={handleSetupFamily} className="space-y-4">
                  <div className="bg-sage/10 rounded-xl p-4 mb-4">
                    <p className="text-sage text-sm flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Create your family hub and invite members with a shared PIN
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Family Name</label>
                    <Input
                      type="text"
                      value={familyName}
                      onChange={(e) => setFamilyName(e.target.value)}
                      placeholder="The Smiths"
                      className="input-cozy"
                      data-testid="family-name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">Family PIN</label>
                    <Input
                      type="password"
                      value={familyPin}
                      onChange={(e) => setFamilyPin(e.target.value.replace(/\D/g, ''))}
                      placeholder="••••"
                      maxLength={6}
                      className="input-cozy"
                      data-testid="family-pin"
                    />
                    <p className="text-xs text-navy-light mt-1">
                      Share this PIN with family members for easy access
                    </p>
                  </div>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full"
                    data-testid="setup-submit"
                  >
                    {loading ? 'Setting up...' : 'Create Family Hub'}
                    <Home className="w-4 h-4 ml-2" />
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </div>

          {/* Setup CTA for new accounts */}
          {mode === 'login' && (
            <div className="mt-6 text-center">
              <button
                onClick={() => setMode('setup')}
                className="text-sm text-navy-light hover:text-terracotta transition-colors"
                data-testid="goto-setup"
              >
                <Users className="w-4 h-4 inline mr-1" />
                Want to create a new family hub?
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
