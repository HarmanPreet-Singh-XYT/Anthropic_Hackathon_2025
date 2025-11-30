'use server'

import { getLogtoContext, signIn } from '@logto/next/server-actions';
import { logtoConfig } from '@/app/logto';

export async function getAuthUser() {
    const { isAuthenticated, claims } = await getLogtoContext(logtoConfig);

    if (!isAuthenticated || !claims?.sub) {
        return null;
    }

    return {
        sub: claims.sub,
        email: claims.email || undefined,
        name: claims.name || undefined,
        avatar: claims.picture || undefined,
        phone: claims.phone_number || undefined,
    };
}

export async function triggerSignIn() {
    await signIn(logtoConfig);
}