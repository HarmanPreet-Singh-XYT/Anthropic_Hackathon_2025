"use client"

import { useState, useEffect } from 'react';
import { getAuthUser, triggerSignIn } from '@/app/auth-actions'; // adjust path as needed

interface User {
    sub: string;
    email?: string;
    name?: string;
    avatar?: string;
    phone?: string;
}

export function useAuthClient() {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                // Call server action to get auth user
                const userData = await getAuthUser();

                if (userData) {
                    setUser(userData);
                } else {
                    // User not authenticated, trigger sign-in
                    console.log('[useAuthClient] User not authenticated, triggering sign-in');
                    await triggerSignIn();
                    setUser(null);
                }
            } catch (error) {
                console.error('[useAuthClient] Error fetching user:', error);
                // On error, also try to sign in
                try {
                    await triggerSignIn();
                } catch (signInError) {
                    console.error('[useAuthClient] Error signing in:', signInError);
                }
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchUser();
    }, []);

    return { user, isLoading };
}