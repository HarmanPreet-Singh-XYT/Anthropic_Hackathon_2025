"use client"
import React, { useState, useEffect, ChangeEvent } from 'react';
import { useAuthClient } from '@/hooks/useAuthClient';
import { updateUserProfile } from '@/app/actions/user-actions';
import {
  User, Shield, Camera, Save, LogOut,
  GraduationCap, ChevronRight, Lock,
  Smartphone, Mail, Building, Eye, EyeOff,
  Laptop, Key, Loader2, LucideIcon
} from 'lucide-react';

interface UserData {
  id: string;
  name?: string;
  email?: string;
  primaryEmail?: string;
  phone?: string;
  avatar?: string;
}

interface FormData {
  name: string;
  phone: string;
}

interface TabItem {
  id: string;
  name: string;
  icon: LucideIcon;
}

interface Session {
  device: string;
  location: string;
  active: boolean;
  time: string;
}

const ProfilePage: React.FC = () => {
  const [isDark, setIsDark] = useState<boolean>(true);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('general');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form state for editable fields
  const [formData, setFormData] = useState<FormData>({
    name: '',
    phone: ''
  });

  const { user, isLoading: isAuthLoading } = useAuthClient();

  // Sync user data from auth hook
  useEffect(() => {
    if (user) {
      setUserData({
        id: user.sub,
        name: user.name,
        email: user.email,
        primaryEmail: user.email,
        phone: user.phone,
        avatar: user.avatar
      });

      // Initialize form data with user data if not already editing
      if (!isEditing) {
        setFormData({
          name: user.name || '',
          phone: user.phone || ''
        });
      }

      setLoading(false);
    } else if (!isAuthLoading) {
      setLoading(false);
    }
  }, [user, isAuthLoading, isEditing]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    if (!userData?.id) return;

    try {
      const result = await updateUserProfile(userData.id, {
        name: formData.name,
        phone: formData.phone
      });

      if (!result.success) {
        throw new Error(result.message);
      }

      // Update local user data state
      setUserData({
        ...userData,
        name: formData.name,
        phone: formData.phone
      });

      setIsEditing(false);
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Error saving data:', err);
      alert(err instanceof Error ? err.message : 'Failed to update profile');
    }
  };

  const handlePasswordUpdate = async (): Promise<void> => {
    const newPasswordInput = document.querySelector('input[placeholder="New Secure Password"]') as HTMLInputElement;
    const newPassword = newPasswordInput?.value;

    if (!newPassword) {
      alert('Please enter a new password');
      return;
    }

    if (!userData?.id) return;

    try {
      const result = await updateUserProfile(userData.id, {
        password: newPassword
      });

      if (!result.success) {
        throw new Error(result.message);
      }

      alert('Password updated successfully!');
      newPasswordInput.value = ''; // Clear input
    } catch (err) {
      console.error('Error updating password:', err);
      alert(err instanceof Error ? err.message : 'Failed to update password');
    }
  };

  const handleSignOut = async (): Promise<void> => {
    try {
      window.location.href = '/api/logto/sign-out';
    } catch (err) {
      console.error('Sign out error:', err);
    }
  };

  const getInitials = (name?: string): string => {
    if (!name) return '??';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getUserRole = (userData: UserData | null): string => {
    return 'Scholar Level 1';
  };

  const getUserId = (userData: UserData | null): string => {
    return userData?.id
      ? `USR-${userData.id.substring(0, 3).toUpperCase()}-${userData.id.substring(3, 6).toUpperCase()}`
      : 'USR-000-000';
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400 font-bold">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
        <div className="text-center max-w-md">
          <div className="bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-2xl border border-red-200 dark:border-red-800">
            <h2 className="font-bold text-xl mb-2">Authentication Error</h2>
            <p className="text-sm mb-4">{error}</p>
            <button
              onClick={() => window.location.href = '/api/logto/sign-in'}
              className="px-6 py-2 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition-colors"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>
    );
  }

  const tabItems: TabItem[] = [
    { id: 'general', name: 'General', icon: User },
    { id: 'security', name: 'Security', icon: Shield },
  ];

  const sessions: Session[] = [
    { device: 'Current Device', location: 'Current Location', active: true, time: 'Active Now' },
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
      <div className="font-sans selection:bg-purple-500/30 selection:text-purple-600 dark:selection:text-purple-300 dark:text-slate-100">

        {/* Circuit Board Background Pattern */}
        <div className="fixed inset-0 pointer-events-none opacity-[0.03] dark:opacity-[0.05]"
          style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")` }}
        />

        {/* Glassmorphic Navbar */}
        <nav className="sticky top-0 z-50 w-full backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2 font-black text-xl tracking-tighter text-slate-900 dark:text-white">
              <div className="w-8 h-8 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
                <GraduationCap className="w-5 h-5" />
              </div>
              ScholarFit<span className="text-purple-600">.ai</span>
            </div>
            <button onClick={() => setIsDark(!isDark)} className="text-xs font-mono font-bold uppercase text-slate-500 hover:text-purple-500 transition-colors">
              {isDark ? "Light Mode" : "Dark Mode"}
            </button>
          </div>
        </nav>

        <main className="relative max-w-7xl mx-auto px-6 py-12">

          {/* Header */}
          <div className="mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700/50 text-blue-700 dark:text-blue-300 text-xs font-bold font-mono tracking-wider mb-4 animate-fade-in-up">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              OPERATOR PROFILE
            </div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white tracking-tighter">
              Account Configuration
            </h1>
          </div>

          <div className="grid lg:grid-cols-12 gap-8">

            {/* Sidebar Navigation */}
            <div className="lg:col-span-3 space-y-2">
              {tabItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between p-4 rounded-2xl border transition-all duration-200 group
                    ${activeTab === item.id
                      ? 'bg-white dark:bg-slate-900 border-purple-200 dark:border-purple-500/50 shadow-lg shadow-purple-500/10'
                      : 'border-transparent hover:bg-white/50 dark:hover:bg-slate-900/50'
                    }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className={`w-5 h-5 ${activeTab === item.id ? 'text-purple-600' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'}`} />
                    <span className={`font-bold ${activeTab === item.id ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400'}`}>
                      {item.name}
                    </span>
                  </div>
                  {activeTab === item.id && <ChevronRight className="w-4 h-4 text-purple-600" />}
                </button>
              ))}

              <div className="pt-8 mt-8 border-t border-slate-200 dark:border-slate-800">
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-3 p-4 rounded-2xl border border-transparent hover:bg-red-50 dark:hover:bg-red-900/10 text-red-600 dark:text-red-400 transition-colors font-bold text-sm"
                >
                  <LogOut className="w-5 h-5" /> Terminate Session
                </button>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="lg:col-span-9">
              <div className="bg-white dark:bg-slate-900/50 backdrop-blur-md rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden min-h-[600px]">

                {/* ID Badge Header */}
                <div className="h-32 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 relative">
                  <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                </div>

                <div className="px-8 pb-8">
                  {/* Avatar Section */}
                  <div className="relative flex justify-between items-end -mt-12 mb-8">
                    <div className="flex items-end gap-6">
                      <div className="relative group">
                        {userData?.avatar ? (
                          <img
                            src={userData.avatar}
                            alt={userData.name}
                            className="w-24 h-24 rounded-2xl border-4 border-white dark:border-slate-900 shadow-2xl object-cover"
                          />
                        ) : (
                          <div className="w-24 h-24 rounded-2xl bg-slate-900 border-4 border-white dark:border-slate-900 flex items-center justify-center text-3xl font-black text-white shadow-2xl">
                            {getInitials(userData?.name)}
                          </div>
                        )}
                        {activeTab === 'general' && (
                          <button className="absolute -bottom-2 -right-2 p-2 bg-white dark:bg-slate-800 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 text-slate-500 hover:text-purple-600 transition-colors">
                            <Camera className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="mb-2">
                        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                          {userData?.name || 'User'}
                        </h2>
                        <p className="text-slate-500 dark:text-slate-400 font-mono text-xs">
                          {getUserRole(userData)} • <span className="text-purple-600">{getUserId(userData)}</span>
                        </p>
                      </div>
                    </div>

                    {activeTab === 'general' && (
                      <button
                        onClick={() => isEditing ? setIsEditing(false) : setIsEditing(true)}
                        className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all
                          ${isEditing
                            ? 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                            : 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:scale-105 shadow-lg'
                          }`}
                      >
                        {isEditing ? 'Cancel Edit' : 'Edit Profile'}
                      </button>
                    )}
                  </div>

                  {/* GENERAL TAB */}
                  {activeTab === 'general' && (
                    <div className="grid md:grid-cols-2 gap-8 animate-fade-in-up">
                      <div className="space-y-6">
                        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest font-mono border-b border-slate-200 dark:border-slate-800 pb-2 mb-4">Identity</h3>

                        <div className="space-y-2">
                          <label className="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono uppercase">Display Name</label>
                          <div className="relative">
                            <User className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
                            <input
                              name="name"
                              disabled={!isEditing}
                              value={formData.name}
                              onChange={handleInputChange}
                              className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-11 pr-4 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all disabled:opacity-60 disabled:cursor-not-allowed"
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono uppercase">Email Uplink</label>
                          <div className="relative">
                            <Mail className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
                            <input
                              disabled
                              value={userData?.primaryEmail || userData?.email || ''}
                              className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-11 pr-4 font-bold text-slate-500 dark:text-slate-400 cursor-not-allowed"
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono uppercase">Mobile</label>
                          <div className="relative">
                            <Smartphone className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
                            <input
                              name="phone"
                              disabled={!isEditing}
                              value={formData.phone}
                              onChange={handleInputChange}
                              placeholder="+1 (555) 000-0000"
                              className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-11 pr-4 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all disabled:opacity-60"
                            />
                          </div>
                        </div>
                      </div>

                      <div className="space-y-6">
                        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest font-mono border-b border-slate-200 dark:border-slate-800 pb-2 mb-4">Academic Context</h3>

                        <div className="bg-slate-50 dark:bg-slate-950/30 rounded-xl p-6 border border-slate-200 dark:border-slate-800 text-center">
                          <Building className="w-8 h-8 text-slate-400 mx-auto mb-3" />
                          <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                            Academic information will be added in future updates
                          </p>
                        </div>
                      </div>

                      {isEditing && (
                        <div className="md:col-span-2 flex justify-end mt-4">
                          <button
                            onClick={handleSave}
                            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] text-white rounded-xl font-bold shadow-lg shadow-blue-500/25 transition-all"
                          >
                            <Save className="w-4 h-4" /> Save Configuration
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                  {/* SECURITY TAB */}
                  {activeTab === 'security' && (
                    <div className="space-y-10 animate-fade-in-up">

                      <div>
                        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest font-mono border-b border-slate-200 dark:border-slate-800 pb-2 mb-6">Encryption Keys (Password)</h3>
                        <div className="grid md:grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono uppercase">Current Password</label>
                            <div className="relative">
                              <Lock className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
                              <input
                                type={showPassword ? "text" : "password"}
                                className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-11 pr-10 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none"
                                placeholder="••••••••"
                              />
                            </div>
                          </div>
                          <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 dark:text-slate-400 font-mono uppercase">New Password</label>
                            <div className="relative">
                              <Key className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
                              <input
                                type={showPassword ? "text" : "password"}
                                className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl py-3 pl-11 pr-10 font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 outline-none"
                                placeholder="New Secure Password"
                              />
                              <button
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-3.5 text-slate-400 hover:text-purple-500"
                              >
                                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </button>
                            </div>
                          </div>
                        </div>
                        <div className="flex justify-end mt-4">
                          <button
                            onClick={handlePasswordUpdate}
                            className="px-6 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-xl font-bold text-sm hover:opacity-90"
                          >
                            Update Credentials
                          </button>
                        </div>
                      </div>

                      <div className="bg-slate-50 dark:bg-slate-950/30 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-start gap-4">
                          <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-xl">
                            <Shield className="w-6 h-6 text-green-600 dark:text-green-400" />
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-900 dark:text-white text-lg">Two-Factor Authentication</h4>
                            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mt-1">
                              Secure your account using an authenticator app (Google Auth / Authy).
                            </p>
                          </div>
                        </div>
                        <button className="px-6 py-2 border border-slate-300 dark:border-slate-700 rounded-xl font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-sm">
                          Configure 2FA
                        </button>
                      </div>

                      <div>
                        <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest font-mono border-b border-slate-200 dark:border-slate-800 pb-2 mb-6">Active Sessions</h3>
                        <div className="space-y-4">
                          {sessions.map((session, i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-xl">
                              <div className="flex items-center gap-4">
                                <Laptop className="w-5 h-5 text-slate-400" />
                                <div>
                                  <div className="font-bold text-slate-900 dark:text-white text-sm">{session.device}</div>
                                  <div className="text-xs text-slate-500 font-mono">{session.location}</div>
                                </div>
                              </div>
                              <div className="text-right">
                                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold border border-green-200 dark:border-green-800">
                                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                  Active
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                    </div>
                  )}

                </div>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
};

export default ProfilePage;