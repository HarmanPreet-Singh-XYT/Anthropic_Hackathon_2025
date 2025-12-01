"use client"
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
    CreditCard, Calendar, Zap, ArrowUpRight, Download,
    CheckCircle2, XCircle, Clock, Loader2, AlertCircle,
    TrendingUp, Activity, Package, Settings,
    ExternalLink
} from 'lucide-react';
import {
    getBillingDetails,
    createPortalSession,
    cancelSubscription,
    BillingDetailsResponse
} from '@/lib/api';
import { useAuthClient } from '@/hooks/useAuthClient';
import { triggerSignIn } from '@/app/auth-actions';

const SubscriptionPage = () => {
    const router = useRouter();
    const { user, isLoading: isAuthLoading } = useAuthClient();
    const [billingData, setBillingData] = useState<BillingDetailsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [cancelLoading, setCancelLoading] = useState(false);
    const [portalLoading, setPortalLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'overview' | 'payments' | 'usage'>('overview');

    useEffect(() => {
        const fetchBillingData = async () => {
            if (!user?.sub) return;

            try {
                setLoading(true);
                const data = await getBillingDetails(user.sub);
                setBillingData(data);
            } catch (err) {
                console.error('Failed to fetch billing details:', err);
                setError(err instanceof Error ? err.message : 'Failed to load billing data');
            } finally {
                setLoading(false);
            }
        };

        if (!isAuthLoading) {
            if (user) {
                fetchBillingData();
            } else {
                triggerSignIn();
            }
        }
    }, [user, isAuthLoading]);

    const handleOpenPortal = async () => {
        if (!user?.sub) return;

        try {
            setPortalLoading(true);
            const { url } = await createPortalSession(user.sub, window.location.href);
            window.location.href = url;
        } catch (err) {
            console.error('Failed to open portal:', err);
            alert('Failed to open billing portal. Please try again.');
            setPortalLoading(false);
        }
    };

    const handleCancelSubscription = async () => {
        if (!user?.sub) return;

        const confirmed = confirm(
            'Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.'
        );

        if (!confirmed) return;

        try {
            setCancelLoading(true);
            const result = await cancelSubscription(user.sub);
            alert(result.message);
            const data = await getBillingDetails(user.sub);
            setBillingData(data);
        } catch (err) {
            console.error('Failed to cancel subscription:', err);
            alert('Failed to cancel subscription. Please try again.');
        } finally {
            setCancelLoading(false);
        }
    };

    // Dark Mode Loading
    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
            </div>
        );
    }

    // Dark Mode Error
    if (error) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-center max-w-md">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-2">Error Loading Billing</h2>
                    <p className="text-slate-400 mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-3 bg-purple-600 text-white rounded-xl font-bold hover:bg-purple-500 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const subscription = billingData?.subscription;
    const wallet = billingData?.wallet;
    const paymentHistory = billingData?.payment_history || [];
    const transactionHistory = billingData?.transaction_history || [];
    const usageHistory = billingData?.usage_history || [];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-300">
            {/* Header - Dark Mode */}
            <div className="bg-slate-900 border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-white">Subscription & Billing</h1>
                            <p className="text-slate-400 mt-1">Manage your plan, payments, and usage</p>
                        </div>
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="px-4 py-2 text-slate-400 hover:text-white font-medium transition-colors border border-transparent hover:border-slate-700 rounded-lg"
                        >
                            ← Back to Dashboard
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Current Plan Card */}
                <div className="bg-gradient-to-br from-purple-800 to-indigo-900 rounded-3xl p-8 mb-8 text-white shadow-xl border border-purple-500/20">
                    <div className="flex items-start justify-between mb-6">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <Package className="w-8 h-8" />
                                <h2 className="text-2xl font-bold">{subscription?.plan?.name || 'Free'} Plan</h2>
                            </div>
                            <p className="text-purple-200">
                                {subscription?.status === 'active' ? 'Active subscription' : 'No active subscription'}
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold mb-1">
                                ${((subscription?.plan?.price_cents || 0) / 100).toFixed(2)}
                            </div>
                            <div className="text-purple-200 text-sm">
                                per {subscription?.plan?.interval || 'month'}
                            </div>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6 mb-6">
                        <div className="bg-black/20 backdrop-blur-md rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-5 h-5 text-yellow-300" />
                                <span className="text-sm text-purple-100">Token Balance</span>
                            </div>
                            <div className="text-2xl font-bold">{wallet?.balance_tokens || 0}</div>
                            <div className="text-xs text-purple-200 mt-1">
                                {subscription?.plan?.tokens_per_period || 0} per {subscription?.plan?.interval || 'month'}
                            </div>
                        </div>

                        <div className="bg-black/20 backdrop-blur-md rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-2">
                                <Calendar className="w-5 h-5 text-blue-300" />
                                <span className="text-sm text-purple-100">Next Billing</span>
                            </div>
                            <div className="text-lg font-bold">
                                {subscription?.current_period_end
                                    ? new Date(subscription.current_period_end).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric'
                                    })
                                    : 'N/A'}
                            </div>
                        </div>

                        <div className="bg-black/20 backdrop-blur-md rounded-xl p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-2">
                                <CheckCircle2 className="w-5 h-5 text-green-300" />
                                <span className="text-sm text-purple-100">Status</span>
                            </div>
                            <div className="text-lg font-bold capitalize">{subscription?.status || 'inactive'}</div>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={handleOpenPortal}
                            disabled={portalLoading}
                            className="flex-1 bg-white text-purple-900 font-bold py-3 px-6 rounded-xl hover:bg-slate-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {portalLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Loading...
                                </>
                            ) : (
                                <>
                                    <Settings className="w-4 h-4" />
                                    Manage Subscription
                                </>
                            )}
                        </button>
                        <button
                            onClick={() => router.push('/pricing')}
                            className="flex-1 bg-purple-600/50 border border-purple-400/50 text-white font-bold py-3 px-6 rounded-xl hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
                        >
                            <ArrowUpRight className="w-4 h-4" />
                            View All Plans
                        </button>
                    </div>
                </div>

                {/* Tabs - Dark Mode */}
                <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 mb-6">
                    <div className="flex border-b border-slate-800">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`flex-1 px-6 py-4 font-bold transition-colors ${activeTab === 'overview'
                                ? 'text-purple-400 border-b-2 border-purple-500'
                                : 'text-slate-500 hover:text-slate-300'
                                }`}
                        >
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('payments')}
                            className={`flex-1 px-6 py-4 font-bold transition-colors ${activeTab === 'payments'
                                ? 'text-purple-400 border-b-2 border-purple-500'
                                : 'text-slate-500 hover:text-slate-300'
                                }`}
                        >
                            Payment History
                        </button>
                        <button
                            onClick={() => setActiveTab('usage')}
                            className={`flex-1 px-6 py-4 font-bold transition-colors ${activeTab === 'usage'
                                ? 'text-purple-400 border-b-2 border-purple-500'
                                : 'text-slate-500 hover:text-slate-300'
                                }`}
                        >
                            Usage History
                        </button>
                    </div>
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        {/* Transaction History */}
                        <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                    <TrendingUp className="w-6 h-6 text-purple-400" />
                                    Recent Transactions
                                </h3>
                                <span className="text-sm text-slate-500">Last 30 days</span>
                            </div>

                            {transactionHistory.length === 0 ? (
                                <p className="text-center text-slate-500 py-8">No transactions yet</p>
                            ) : (
                                <div className="space-y-3">
                                    {transactionHistory.slice(0, 10).map((tx) => (
                                        <div
                                            key={tx.id}
                                            className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl hover:bg-slate-800 transition-colors border border-slate-800"
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center border ${tx.type === 'credit' ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'
                                                    }`}>
                                                    {tx.type === 'credit' ? (
                                                        <TrendingUp className="w-5 h-5 text-green-400" />
                                                    ) : (
                                                        <Activity className="w-5 h-5 text-red-400" />
                                                    )}
                                                </div>
                                                <div>
                                                    <div className="font-bold text-slate-200">{tx.description}</div>
                                                    <div className="text-sm text-slate-500">
                                                        {new Date(tx.date).toLocaleDateString('en-US', {
                                                            month: 'short',
                                                            day: 'numeric',
                                                            year: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className={`text-lg font-bold ${tx.type === 'credit' ? 'text-green-400' : 'text-red-400'
                                                    }`}>
                                                    {tx.type === 'credit' ? '+' : '-'}{tx.amount} tokens
                                                </div>
                                                <div className="text-sm text-slate-500">
                                                    Balance: {tx.balance_after}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Plan Features */}
                        {subscription?.plan?.features && Object.keys(subscription.plan.features).length > 0 && (
                            <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 p-6">
                                <h3 className="text-xl font-bold text-white mb-4">Plan Features</h3>
                                <div className="grid md:grid-cols-2 gap-4">
                                    {Object.entries(subscription.plan.features).map(([key, value]) => (
                                        <div key={key} className="flex items-center gap-3 p-3 bg-slate-800/50 border border-slate-800 rounded-lg">
                                            <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                                            <div>
                                                <div className="font-medium text-slate-200 capitalize">
                                                    {key.replace(/_/g, ' ')}
                                                </div>
                                                <div className="text-sm text-slate-500">
                                                    {typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : String(value)}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'payments' && (
                    <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <CreditCard className="w-6 h-6 text-purple-400" />
                                Payment History
                            </h3>
                            <button className="text-sm font-medium text-purple-400 hover:text-purple-300 flex items-center gap-1">
                                <Download className="w-4 h-4" />
                                Export
                            </button>
                        </div>

                        {paymentHistory.length === 0 ? (
                            <p className="text-center text-slate-500 py-8">No payments yet</p>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-slate-800">
                                            <th className="text-left py-3 px-4 text-sm font-bold text-slate-400">Date</th>
                                            <th className="text-left py-3 px-4 text-sm font-bold text-slate-400">Description</th>
                                            <th className="text-left py-3 px-4 text-sm font-bold text-slate-400">Amount</th>
                                            <th className="text-left py-3 px-4 text-sm font-bold text-slate-400">Status</th>
                                            <th className="text-left py-3 px-4 text-sm font-bold text-slate-400">Invoice</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {paymentHistory.map((payment) => (
                                            <tr key={payment.id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                                                <td className="py-4 px-4 text-sm text-slate-400">
                                                    {new Date(payment.date).toLocaleDateString('en-US', {
                                                        month: 'short',
                                                        day: 'numeric',
                                                        year: 'numeric'
                                                    })}
                                                </td>
                                                <td className="py-4 px-4 text-sm text-slate-200 font-medium">
                                                    {payment.description}
                                                </td>
                                                <td className="py-4 px-4 text-sm font-bold text-slate-200">
                                                    ${(payment.amount_cents / 100).toFixed(2)} {payment.currency}
                                                </td>
                                                <td className="py-4 px-4">
                                                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold border ${payment.status === 'succeeded'
                                                        ? 'bg-green-500/10 text-green-400 border-green-500/20'
                                                        : payment.status === 'failed'
                                                            ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                                            : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                                                        }`}>
                                                        {payment.status === 'succeeded' && <CheckCircle2 className="w-3 h-3" />}
                                                        {payment.status === 'failed' && <XCircle className="w-3 h-3" />}
                                                        {payment.status === 'pending' && <Clock className="w-3 h-3" />}
                                                        {payment.status}
                                                    </span>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <button className="text-purple-400 hover:text-purple-300 text-sm font-medium flex items-center gap-1">
                                                        <ExternalLink className="w-4 h-4" />
                                                        View
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'usage' && (
                    <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Activity className="w-6 h-6 text-purple-400" />
                                Usage History
                            </h3>
                            <span className="text-sm text-slate-500">Last 30 days</span>
                        </div>

                        {usageHistory.length === 0 ? (
                            <p className="text-center text-slate-500 py-8">No usage recorded yet</p>
                        ) : (
                            <div className="space-y-3">
                                {usageHistory.map((usage) => (
                                    <div
                                        key={usage.id}
                                        className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl hover:bg-slate-800 transition-colors border border-slate-800"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                                                <Zap className="w-5 h-5 text-purple-400" />
                                            </div>
                                            <div>
                                                <div className="font-bold text-slate-200">{usage.feature}</div>
                                                <div className="text-sm text-slate-500">
                                                    {new Date(usage.date).toLocaleDateString('en-US', {
                                                        month: 'short',
                                                        day: 'numeric',
                                                        year: 'numeric',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    })}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-lg font-bold text-slate-200">
                                                {usage.amount} tokens
                                            </div>
                                            {usage.cost_cents > 0 && (
                                                <div className="text-sm text-slate-500">
                                                    ${(usage.cost_cents / 100).toFixed(2)}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Danger Zone - Dark Mode */}
                {subscription?.status === 'active' && (
                    <div className="bg-slate-900 rounded-2xl shadow-sm border border-red-500/20 p-6 mt-8">
                        <h3 className="text-xl font-bold text-red-400 mb-2">Danger Zone</h3>
                        <p className="text-slate-400 mb-4">
                            Cancel your subscription. You'll retain access until the end of your billing period.
                        </p>
                        <button
                            onClick={handleCancelSubscription}
                            disabled={cancelLoading}
                            className="px-6 py-3 bg-red-600/10 border border-red-600/50 text-red-500 font-bold rounded-xl hover:bg-red-600 hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {cancelLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Canceling...
                                </>
                            ) : (
                                <>
                                    <XCircle className="w-4 h-4" />
                                    Cancel Subscription
                                </>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SubscriptionPage;