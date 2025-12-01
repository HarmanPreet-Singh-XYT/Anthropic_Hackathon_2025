"use client"

import { useState, useEffect } from 'react';
import { getAuthUser } from '@/app/auth-actions';

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
                    // User not authenticated, but don't force sign-in
                    // Let the consuming component decide what to do
                    console.log('[useAuthClient] User not authenticated');
                    setUser(null);
                }
            } catch (error) {
                console.error('[useAuthClient] Error fetching user:', error);
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchUser();
    }, []);

    return { user, isLoading };
}