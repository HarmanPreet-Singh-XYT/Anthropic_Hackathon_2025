"use client"
import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Brain, Menu, X, User, LogOut, CreditCard,
    Settings, HelpCircle, ChevronDown, GraduationCap
} from 'lucide-react';
import { useAuthClient } from '@/hooks/useAuthClient';
import { triggerSignIn, triggerSignOut } from '@/app/auth-actions';

interface NavigationProps {
    variant?: 'landing' | 'default' | 'dashboard';
    className?: string;
}

export function Navigation({ variant = 'default', className = '' }: NavigationProps) {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
    const [moreDropdownOpen, setMoreDropdownOpen] = useState(false);
    const { user, isLoading } = useAuthClient();
    const pathname = usePathname();

    const isLanding = variant === 'landing';
    const isDashboard = variant === 'dashboard';

    const handleSignIn = () => {
        triggerSignIn();
    };

    const handleSignOut = async () => {
        await triggerSignOut();
        setProfileDropdownOpen(false);
    };

    const getInitials = (name?: string) => {
        if (!name) return 'U';
        const parts = name.split(' ');
        if (parts.length >= 2) {
            return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    };

    // Navigation links for landing page
    const landingLinks = [
        { href: '#how-it-works', label: 'Process' },
        { href: '#features', label: 'Features' },
        { href: '/support', label: 'Support' },
        { href: '/pricing', label: 'Pricing' },
    ];

    // Navigation links for unauthenticated users (non-landing pages)
    const publicLinks = [
        { href: '/#features', label: 'Features' },
        { href: '/pricing', label: 'Pricing' },
        { href: '/support', label: 'Support' },
    ];

    // Navigation links for authenticated users
    const authLinks = [
        { href: '/', label: 'Home' },
        { href: '/pricing', label: 'Pricing' },
        { href: '/support', label: 'Support' },
    ];

    // Determine which links to show
    const currentLinks = isLanding ? landingLinks : (user ? authLinks : publicLinks);

    return (
        <nav
            className={`fixed top-0 w-full z-50 transition-colors duration-300 ${isLanding
                ? 'bg-black/50 backdrop-blur-xl border-b border-white/5'
                : 'bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800'
                } ${className}`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link
                        href={user ? '/dashboard' : '/'}
                        className="flex items-center gap-2 font-black text-xl tracking-tighter hover:opacity-80 transition-opacity"
                    >
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isLanding
                            ? 'bg-white/10 border border-white/20'
                            : 'bg-gradient-to-tr from-blue-600 to-purple-600'
                            } shadow-lg`}>
                            <Brain className="w-5 h-5 text-white" />
                        </div>
                        <span className={isLanding ? 'text-white' : 'text-slate-900 dark:text-white'}>
                            ScholarMatch<span className="text-purple-600">.ai</span>
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {currentLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`font-medium text-sm transition-colors ${isLanding
                                    ? 'text-white/60 hover:text-white'
                                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                                    } ${pathname === link.href ? (isLanding ? 'text-white' : 'text-slate-900 dark:text-white') : ''}`}
                            >
                                {link.label}
                            </Link>
                        ))}

                        {/* More Dropdown - Only on Landing Page */}

                    </div>

                    {/* Right Side - Auth Actions */}
                    <div className="hidden md:flex items-center gap-4">
                        {isLoading ? (
                            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
                        ) : user ? (
                            <div className="relative">
                                <button
                                    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                                    className={`flex items-center gap-2 px-3 py-2 rounded-full transition-all ${isLanding
                                        ? 'bg-white/10 hover:bg-white/20 border border-white/20'
                                        : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
                                        }`}
                                >
                                    {user.avatar ? (
                                        <img
                                            src={user.avatar}
                                            alt={user.name || 'User'}
                                            className="w-6 h-6 rounded-full object-cover"
                                        />
                                    ) : (
                                        <div className="w-6 h-6 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold">
                                            {getInitials(user.name)}
                                        </div>
                                    )}
                                    <span className={`text-sm font-medium ${isLanding ? 'text-white' : 'text-slate-900 dark:text-white'}`}>
                                        {user.name?.split(' ')[0] || 'User'}
                                    </span>
                                    <ChevronDown className={`w-4 h-4 ${isLanding ? 'text-white/60' : 'text-slate-500'}`} />
                                </button>

                                {/* Dropdown Menu */}
                                {profileDropdownOpen && (
                                    <>
                                        <div
                                            className="fixed inset-0 z-40"
                                            onClick={() => setProfileDropdownOpen(false)}
                                        />
                                        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 py-2 z-50">
                                            <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                                                <p className="text-sm font-bold text-slate-900 dark:text-white">{user.name || 'User'}</p>
                                                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{user.email}</p>
                                            </div>
                                            <Link
                                                href="/dashboard/profile"
                                                className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                                onClick={() => setProfileDropdownOpen(false)}
                                            >
                                                <User className="w-4 h-4" />
                                                Profile
                                            </Link>
                                            <Link
                                                href="/subscription"
                                                className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                                onClick={() => setProfileDropdownOpen(false)}
                                            >
                                                <CreditCard className="w-4 h-4" />
                                                Subscription
                                            </Link>
                                            <Link
                                                href="/support"
                                                className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                                onClick={() => setProfileDropdownOpen(false)}
                                            >
                                                <HelpCircle className="w-4 h-4" />
                                                Support
                                            </Link>
                                            <div className="border-t border-slate-200 dark:border-slate-800 my-2" />
                                            <button
                                                onClick={handleSignOut}
                                                className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors w-full text-left"
                                            >
                                                <LogOut className="w-4 h-4" />
                                                Sign Out
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                        ) : (
                            <>
                                <button
                                    onClick={handleSignIn}
                                    className={`text-sm font-medium transition-colors ${isLanding
                                        ? 'text-white/80 hover:text-white'
                                        : 'text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                                        }`}
                                >
                                    Sign In
                                </button>
                                <button
                                    onClick={handleSignIn}
                                    className={`px-5 py-2.5 rounded-full font-bold text-sm transition-all hover:shadow-lg ${isLanding
                                        ? 'bg-white text-black hover:bg-white/90 hover:shadow-white/20'
                                        : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-purple-500/40'
                                        } active:scale-95 flex items-center gap-2`}
                                >
                                    Get Started
                                </button>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className={`md:hidden p-2 rounded-lg transition-colors ${isLanding
                            ? 'text-white hover:bg-white/10'
                            : 'text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                            }`}
                    >
                        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className={`md:hidden border-t ${isLanding
                    ? 'border-white/10 bg-black/90'
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950'
                    } backdrop-blur-xl`}>
                    <div className="px-4 py-4 space-y-2">
                        {currentLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`block px-4 py-3 rounded-xl font-medium transition-colors ${isLanding
                                    ? 'text-white/80 hover:bg-white/10 hover:text-white'
                                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                                    } ${pathname === link.href ? (isLanding ? 'bg-white/10 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white') : ''}`}
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                {link.label}
                            </Link>
                        ))}

                        {user ? (
                            <>
                                <div className={`border-t my-2 ${isLanding ? 'border-white/10' : 'border-slate-200 dark:border-slate-800'}`} />
                                <Link
                                    href="/dashboard/profile"
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${isLanding
                                        ? 'text-white/80 hover:bg-white/10'
                                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                                        }`}
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <User className="w-4 h-4" />
                                    Profile
                                </Link>
                                <Link
                                    href="/subscription"
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${isLanding
                                        ? 'text-white/80 hover:bg-white/10'
                                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                                        }`}
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    <CreditCard className="w-4 h-4" />
                                    Subscription
                                </Link>
                                <button
                                    onClick={() => {
                                        handleSignOut();
                                        setMobileMenuOpen(false);
                                    }}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors w-full text-left ${isLanding
                                        ? 'text-red-400 hover:bg-red-500/10'
                                        : 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10'
                                        }`}
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </button>
                            </>
                        ) : (
                            <>
                                <div className={`border-t my-2 ${isLanding ? 'border-white/10' : 'border-slate-200 dark:border-slate-800'}`} />
                                <button
                                    onClick={() => {
                                        handleSignIn();
                                        setMobileMenuOpen(false);
                                    }}
                                    className={`w-full px-4 py-3 rounded-xl font-bold transition-colors ${isLanding
                                        ? 'bg-white text-black hover:bg-white/90'
                                        : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg'
                                        }`}
                                >
                                    Get Started
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
}
