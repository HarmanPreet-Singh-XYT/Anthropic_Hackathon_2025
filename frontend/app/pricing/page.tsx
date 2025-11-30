"use client"
import React, { useState, useEffect } from 'react';
import {
  Check, X, Sparkles, Zap, Brain, Target, Shield,
  ArrowRight, Moon, Sun, ChevronDown, Loader2, Settings
} from 'lucide-react';
import { getBillingPlans, createCheckoutSession, createPortalSession, getBillingDetails, BillingPlan } from '@/lib/api';
import { useAuthClient } from '@/hooks/useAuthClient';

const PricingPage = () => {
  const [isAnnual, setIsAnnual] = useState(true);
  const [isDark, setIsDark] = useState(true);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [currentPlanSlug, setCurrentPlanSlug] = useState<string | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<string | null>(null);

  const { user, isLoading: isAuthLoading } = useAuthClient();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch billing plans
        const plansData = await getBillingPlans();
        setPlans(plansData.plans);

        // Fetch user's current subscription if authenticated
        if (user?.sub) {
          try {
            const billingDetails = await getBillingDetails(user.sub);
            if (billingDetails.subscription) {
              setSubscriptionStatus(billingDetails.subscription.status);
              // Match the current plan by comparing plan details
              const currentPlan = plansData.plans.find(
                p => p.name === billingDetails.subscription?.plan.name
              );
              if (currentPlan) {
                setCurrentPlanSlug(currentPlan.slug);
              }
            }
          } catch (error) {
            console.error('Failed to fetch billing details:', error);
            // Continue even if billing details fail
          }
        }
      } catch (error) {
        console.error('Failed to fetch pricing data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (!isAuthLoading) {
      fetchData();
    }
  }, [user, isAuthLoading]);

  const handleSubscribe = async (planSlug: string) => {
    if (!user?.sub) {
      // Redirect to login
      window.location.href = '/api/logto/sign-in';
      return;
    }

    try {
      setCheckoutLoading(planSlug);
      const baseUrl = window.location.origin;
      const { url } = await createCheckoutSession(
        user.sub,
        planSlug,
        `${baseUrl}/dashboard?checkout=success`,
        `${baseUrl}/pricing?checkout=canceled`
      );
      window.location.href = url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to start checkout. Please try again.');
      setCheckoutLoading(null);
    }
  };

  const handleManagePlan = async () => {
    if (!user?.sub) {
      window.location.href = '/api/logto/sign-in';
      return;
    }

    try {
      setCheckoutLoading('manage');
      const baseUrl = window.location.origin;
      const { url } = await createPortalSession(
        user.sub,
        `${baseUrl}/pricing`
      );
      window.location.href = url;
    } catch (error) {
      console.error('Failed to create portal session:', error);
      alert('Failed to open billing portal. Please try again.');
      setCheckoutLoading(null);
    }
  };

  const getButtonForPlan = (planSlug: string) => {
    const isCurrentPlan = currentPlanSlug === planSlug;
    const isFreePlan = planSlug === 'free' || planSlug === 'basic';

    if (isCurrentPlan && subscriptionStatus === 'active') {
      return {
        text: 'Current Plan',
        disabled: true,
        onClick: () => { },
        className: 'w-full py-4 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400 font-bold cursor-not-allowed'
      };
    }

    if (isCurrentPlan) {
      return {
        text: 'Manage Plan',
        disabled: checkoutLoading === 'manage',
        onClick: handleManagePlan,
        className: 'w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold shadow-lg hover:shadow-purple-500/40 hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2'
      };
    }

    if (isFreePlan) {
      return {
        text: 'Start Free',
        disabled: false,
        onClick: () => window.location.href = '/dashboard',
        className: 'w-full py-3.5 rounded-xl border border-slate-200 dark:border-slate-700 font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors'
      };
    }

    return {
      text: currentPlanSlug ? 'Change Plan' : 'Get Started Now',
      disabled: checkoutLoading === planSlug,
      onClick: () => handleSubscribe(planSlug),
      className: 'w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold shadow-lg shadow-purple-900/50 hover:shadow-purple-500/40 hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2'
    };
  };

  const toggleTheme = () => setIsDark(!isDark);

  const features = [
    {
      category: "Intelligence & Discovery (Scout Agent)",
      items: [
        { name: "Scholarship Scraping Sources", basic: "Public DBs", pro: "Hidden + Niche", ultra: "Global Deep Web" },
        { name: "Winner Profile Analysis", basic: "Limited", pro: "Full History", ultra: "Real-time" },
        { name: "Criterion Decoding", basic: "Standard", pro: "Implicit Bias", ultra: "Committee DNA" },
      ]
    },
    {
      category: "Narrative Engine (Ghostwriter Agent)",
      items: [
        { name: "Essay Generation", basic: "None", pro: "10 / mo", ultra: "Unlimited" },
        { name: "Tone Matching", basic: "-", pro: "Standard", ultra: "Chameleon Mode" },
        { name: "Bridge Story Extraction", basic: "-", pro: "Yes", ultra: "Deep Interview" },
      ]
    },
    {
      category: "Technical Stack (RAG Pipeline)",
      items: [
        { name: "LLM Intelligence", basic: "GPT-3.5", pro: "Claude 3.5 Sonnet", ultra: "Claude 3.5 Opus" },
        { name: "Context Window", basic: "8k Tokens", pro: "32k Tokens", ultra: "128k Tokens" },
        { name: "Vector Database History", basic: "7 Days", pro: "Forever", ultra: "Forever" },
      ]
    }
  ];

  const faqs = [
    { q: "Is using AI for scholarships considered cheating?", a: "Not with ScholarFit. Unlike generic AI writers that fabricate content, our Interviewer Agent extracts your authentic life stories. We help you articulate your actual experiences better, acting as a coach and editor rather than a fake author." },
    { q: "Can I cancel my subscription anytime?", a: "Absolutely. You can cancel from your dashboard or the Stripe customer portal. Your subscription will remain active until the end of your billing cycle." },
    { q: "How secure is my personal data?", a: "We use enterprise-grade encryption. Your essays and resume data are stored in isolated vector environments and are never used to train public models. You own your IP." },
    { q: "Does this work for international students?", a: "Yes. The Scout Agent is configured to identify global opportunities and filter specifically for visa-status eligibility." },
  ];

  // Find the pro plan for the highlighted card
  const proPlan = plans.find(p => p.slug === 'pro');
  const proPriceMonthly = proPlan ? (proPlan.price_cents / 100).toFixed(0) : '29';

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
      <div className="font-sans selection:bg-purple-500/30 selection:text-purple-600 dark:selection:text-purple-300 dark:text-slate-100 transition-colors duration-300">

        {/* Navbar */}
        <nav className="fixed top-0 w-full z-50 border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2 font-black text-xl tracking-tighter">
              <div className="w-8 h-8 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white">
                <Brain className="w-5 h-5" />
              </div>
              <span className="text-slate-900 dark:text-white">ScholarFit<span className="text-purple-600">.ai</span></span>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {isDark ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
            </button>
          </div>
        </nav>

        {/* Background Grid */}
        <div className="fixed inset-0 pointer-events-none opacity-[0.03] dark:opacity-[0.05]"
          style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")` }}
        />

        {/* Hero Section */}
        <div className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto text-center">

          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700/50 text-blue-700 dark:text-blue-300 text-xs font-bold font-mono tracking-wider animate-fade-in-up mb-8 hover:scale-105 transition-transform cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            RAG PIPELINE OPTIMIZED
          </div>

          <h1 className="text-5xl md:text-7xl font-black text-slate-900 dark:text-white tracking-tighter mb-6">
            Unlock Your <br className="hidden md:block" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 animate-gradient-x">
              Full Scholarship Potential
            </span>
          </h1>

          <p className="text-xl text-slate-600 dark:text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed mb-10">
            Don't just apply. <span className="text-slate-900 dark:text-white font-serif italic">Compete.</span> Use our multi-agent swarm to analyze hidden criteria, conduct deep interviews, and craft narratives that win.
          </p>

          {/* Toggle Switch */}
          <div className="flex items-center justify-center gap-4 mb-16 select-none">
            <span className={`text-sm font-bold ${!isAnnual ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-500'}`}>Monthly</span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative w-16 h-9 bg-slate-200 dark:bg-slate-700 rounded-full p-1 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors"
            >
              <div className={`w-7 h-7 bg-white rounded-full shadow-md flex items-center justify-center transform transition-all duration-300 ${isAnnual ? 'translate-x-7' : 'translate-x-0'}`}>
                {isAnnual && <Sparkles className="w-3.5 h-3.5 text-purple-600" />}
              </div>
            </button>
            <span className={`text-sm font-bold flex items-center gap-2 ${isAnnual ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-500'}`}>
              Yearly <span className="text-[10px] uppercase font-black text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900/50 px-2 py-0.5 rounded-full tracking-wider border border-green-200 dark:border-green-800">Save 20%</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        {loading ? (
          <div className="max-w-7xl mx-auto px-6 py-20 flex justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-purple-600" />
          </div>
        ) : (
          <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8 relative z-10">

            {/* Card 1: Free Plan */}
            <div className="bg-white dark:bg-slate-900/50 backdrop-blur-sm border border-slate-200 dark:border-slate-800 rounded-3xl p-8 hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group relative">
              {currentPlanSlug === 'free' && subscriptionStatus === 'active' && (
                <div className="absolute top-6 right-6">
                  <span className="bg-green-500/20 text-green-600 dark:text-green-400 text-xs font-bold px-3 py-1 rounded-full border border-green-500/30 flex items-center gap-1">
                    <Check className="w-3 h-3" /> ACTIVE
                  </span>
                </div>
              )}
              <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Target className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              </div>
              <h3 className="text-xl font-black tracking-tight text-slate-900 dark:text-white mb-2">The Scout</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 h-10">Essential tools for students just starting the discovery phase.</p>
              <div className="flex items-baseline gap-1 mb-8">
                <span className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">$0</span>
                <span className="text-slate-400 font-mono">/forever</span>
              </div>
              <button
                onClick={getButtonForPlan('free').onClick}
                disabled={getButtonForPlan('free').disabled}
                className={getButtonForPlan('free').className}
              >
                {getButtonForPlan('free').text}
              </button>
              <ul className="space-y-4 text-sm">
                <li className="flex gap-3 text-slate-600 dark:text-slate-300"><Check className="w-5 h-5 text-slate-400 flex-shrink-0" /> Scout Agent Access</li>
                <li className="flex gap-3 text-slate-600 dark:text-slate-300"><Check className="w-5 h-5 text-slate-400 flex-shrink-0" /> Resume Parsing</li>
                <li className="flex gap-3 text-slate-400 dark:text-slate-600"><X className="w-5 h-5 flex-shrink-0" /> No Essay Generation</li>
              </ul>
            </div>

            {/* Card 2: Pro Plan (Highlighted) */}
            <div className="bg-slate-900 dark:bg-slate-950 border border-purple-500/30 rounded-3xl p-8 relative overflow-hidden transform md:-translate-y-4 shadow-2xl shadow-purple-500/20">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
              <div className="absolute top-6 right-6 flex gap-2">
                {currentPlanSlug === proPlan?.slug && subscriptionStatus === 'active' && (
                  <span className="bg-green-500/20 text-green-300 text-xs font-bold px-3 py-1 rounded-full border border-green-500/30 flex items-center gap-1">
                    <Check className="w-3 h-3" /> ACTIVE
                  </span>
                )}
                <span className="bg-purple-500/20 text-purple-300 text-xs font-bold px-3 py-1 rounded-full border border-purple-500/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> POPULAR
                </span>
              </div>

              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/30">
                <Brain className="w-6 h-6 text-white" />
              </div>

              <h3 className="text-xl font-black tracking-tight text-white mb-2">The Scholar</h3>
              <p className="text-sm text-slate-400 mb-6 h-10">Complete AI suite to dominate the application process.</p>

              <div className="flex items-baseline gap-1 mb-8">
                <span className="text-5xl font-black text-white tracking-tighter">${proPriceMonthly}</span>
                <span className="text-slate-500 font-mono">/mo</span>
              </div>

              <button
                onClick={() => proPlan && getButtonForPlan(proPlan.slug).onClick()}
                disabled={!proPlan || getButtonForPlan(proPlan?.slug || 'pro').disabled}
                className={getButtonForPlan(proPlan?.slug || 'pro').className}
              >
                {checkoutLoading === (proPlan?.slug || 'pro') || checkoutLoading === 'manage' ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    {currentPlanSlug === proPlan?.slug && subscriptionStatus === 'active' && (
                      <Check className="w-4 h-4" />
                    )}
                    {getButtonForPlan(proPlan?.slug || 'pro').text}
                  </>
                )}
              </button>

              <ul className="space-y-4 text-sm">
                <li className="flex gap-3 text-white"><div className="bg-green-500/20 rounded-full p-0.5"><Check className="w-3.5 h-3.5 text-green-400" strokeWidth={3} /></div> Unlimited RAG Matching</li>
                <li className="flex gap-3 text-white"><div className="bg-green-500/20 rounded-full p-0.5"><Check className="w-3.5 h-3.5 text-green-400" strokeWidth={3} /></div> Interviewer Agent (Deep)</li>
                <li className="flex gap-3 text-white"><div className="bg-green-500/20 rounded-full p-0.5"><Check className="w-3.5 h-3.5 text-green-400" strokeWidth={3} /></div> {proPlan?.tokens_per_period || 2000} AI Credits/mo</li>
                <li className="flex gap-3 text-white"><div className="bg-green-500/20 rounded-full p-0.5"><Check className="w-3.5 h-3.5 text-green-400" strokeWidth={3} /></div> Claude 3.5 Sonnet Model</li>
              </ul>
            </div>

            {/* Card 3: Enterprise/Waitlist */}
            <div className="bg-white dark:bg-slate-900/50 backdrop-blur-sm border border-slate-200 dark:border-slate-800 rounded-3xl p-8 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group">
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <h3 className="text-xl font-black tracking-tight text-slate-900 dark:text-white mb-2">The Laureate</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 h-10">Maximum velocity for Ivy League & Prestigious grants.</p>
              <div className="flex items-baseline gap-1 mb-8">
                <span className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">$99</span>
                <span className="text-slate-400 font-mono">/mo</span>
              </div>
              <button className="w-full py-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-transparent font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors mb-8">
                Join Waitlist
              </button>
              <ul className="space-y-4 text-sm">
                <li className="flex gap-3 text-slate-600 dark:text-slate-300"><Check className="w-5 h-5 text-emerald-500 flex-shrink-0" /> Unlimited Ghostwriter</li>
                <li className="flex gap-3 text-slate-600 dark:text-slate-300"><Check className="w-5 h-5 text-emerald-500 flex-shrink-0" /> Human-in-Loop Review</li>
                <li className="flex gap-3 text-slate-600 dark:text-slate-300"><Check className="w-5 h-5 text-emerald-500 flex-shrink-0" /> Priority Processing</li>
              </ul>
            </div>
          </div>
        )}

        {/* Feature Matrix */}
        <div className="max-w-7xl mx-auto px-6 py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white tracking-tight mb-4">
              X-Ray Vision into the Capabilities
            </h2>
            <p className="text-slate-600 dark:text-slate-400">Comparing agent authorization levels across plans.</p>
          </div>

          <div className="overflow-hidden rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800">
                    <th className="p-6 font-bold text-slate-900 dark:text-white">Feature</th>
                    <th className="p-6 font-mono text-slate-500 dark:text-slate-400">SCOUT</th>
                    <th className="p-6 font-mono text-purple-600 dark:text-purple-400 font-bold">SCHOLAR</th>
                    <th className="p-6 font-mono text-emerald-600 dark:text-emerald-400 font-bold">LAUREATE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {features.map((section, idx) => (
                    <React.Fragment key={idx}>
                      <tr className="bg-slate-50/50 dark:bg-slate-900/50">
                        <td colSpan={4} className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                          {section.category}
                        </td>
                      </tr>
                      {section.items.map((item, i) => (
                        <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="p-6 font-medium text-slate-700 dark:text-slate-200">{item.name}</td>
                          <td className="p-6 text-slate-500 dark:text-slate-400 font-mono text-xs">{item.basic}</td>
                          <td className="p-6 text-slate-900 dark:text-white font-mono text-xs font-bold bg-purple-50/50 dark:bg-purple-900/10">{item.pro}</td>
                          <td className="p-6 text-slate-900 dark:text-white font-mono text-xs">{item.ultra}</td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Money Back Guarantee */}
        <div className="max-w-4xl mx-auto px-6 mb-24">
          <div className="bg-slate-900 dark:bg-white rounded-3xl p-1 flex shadow-2xl">
            <div className="flex-1 bg-white dark:bg-slate-950 rounded-[20px] p-8 md:p-12 border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row items-center gap-8 text-center md:text-left">
              <div className="w-20 h-20 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                <Shield className="w-10 h-10 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">30-Day "Application Sent" Guarantee</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  If ScholarFit doesn't help you submit at least 5 high-quality applications in your first month, we'll refund your subscription in full. No questions asked. We only win when you apply.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto px-6 py-20 border-t border-slate-200 dark:border-slate-800">
          <h2 className="text-3xl font-black text-center text-slate-900 dark:text-white mb-12 tracking-tight">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
              >
                <button
                  onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-6 text-left"
                >
                  <span className="font-bold text-slate-900 dark:text-white pr-8">{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform duration-300 ${activeFaq === idx ? 'rotate-180' : ''}`} />
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ease-in-out ${activeFaq === idx ? 'max-h-48 opacity-100' : 'max-h-0 opacity-0'}`}
                >
                  <p className="px-6 pb-6 text-slate-600 dark:text-slate-400 leading-relaxed border-t border-slate-100 dark:border-slate-800/50 pt-4">
                    {faq.a}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <footer className="relative bg-slate-950 text-slate-400 overflow-hidden border-t border-slate-800 mt-20">
          <div className="absolute inset-0 opacity-[0.05]"
            style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%239C92AC' fill-opacity='1' fill-rule='evenodd'/%3E%3C/svg%3E")` }}
          />

          <div className="relative max-w-7xl mx-auto px-6 py-16 grid grid-cols-2 md:grid-cols-4 gap-12 text-sm">

            <div className="col-span-2 md:col-span-1 space-y-4">
              <div className="flex items-center gap-2 font-black text-white tracking-tighter">
                <Brain className="w-5 h-5 text-purple-500" />
                <span>ScholarFit.ai</span>
              </div>
              <p className="text-slate-500 leading-relaxed">
                Transforming scholarship applications through intelligent narrative alignment and multi-agent orchestration.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Platform</h4>
              <ul className="space-y-3">
                <li className="hover:text-purple-400 transition-colors cursor-pointer">Agent Swarm</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer">RAG Pipeline</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer">Integrations</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer flex items-center gap-2">
                  Pricing <span className="bg-purple-500/20 text-purple-400 text-[10px] px-1.5 py-0.5 rounded border border-purple-500/30">Live</span>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Resources</h4>
              <ul className="space-y-3">
                <li className="hover:text-blue-400 transition-colors cursor-pointer">Documentation</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">API Reference</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">Success Stories</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">System Status</li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Legal</h4>
              <ul className="space-y-3">
                <li className="hover:text-white transition-colors cursor-pointer">Privacy Policy</li>
                <li className="hover:text-white transition-colors cursor-pointer">Terms of Service</li>
                <li className="hover:text-white transition-colors cursor-pointer">Data Security</li>
                <li className="hover:text-white transition-colors cursor-pointer">Refund Policy</li>
              </ul>
            </div>
          </div>

          <div className="relative border-t border-slate-800/50">
            <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-slate-600 text-xs">
                © 2024 ScholarFit AI Inc. All rights reserved. Built with Anthropic Claude 3.5.
              </p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs font-mono text-green-500">SYSTEMS OPERATIONAL</span>
              </div>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
};

export default PricingPage;