
import React from 'react';
import { getLogtoContext, signIn } from '@logto/next/server-actions';
import { logtoConfig } from '@/app/logto'; // Adjust path as needed
import { redirect } from 'next/navigation';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export async function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, claims } = await getLogtoContext(logtoConfig);

    if (!isAuthenticated) {
        console.log('[ProtectedRoute] User not authenticated, redirecting to sign-in');
        
        // Trigger sign-in using server action
        await signIn(logtoConfig);
        
        // This line may not be reached due to signIn redirect, but just in case
        return null;
    }

    console.log('[ProtectedRoute] User authenticated:', claims?.sub);

    // User is authenticated, render children
    return <>{children}</>;
}

// Server-side hook to get user data (use in Server Components)
export async function getAuthUser() {
    const { isAuthenticated, claims } = await getLogtoContext(logtoConfig);
    
    if (!isAuthenticated) {
        return null;
    }
    
    return {
        sub: claims?.sub,
        email: claims?.email,
        name: claims?.name,
    };
}