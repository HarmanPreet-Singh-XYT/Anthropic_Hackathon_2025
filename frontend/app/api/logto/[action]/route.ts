import LogtoClient from '@logto/next/edge';
import { logtoConfig } from '../../../logto';
import { NextRequest } from 'next/server';

const logtoClient = new LogtoClient(logtoConfig);

export async function GET(request: NextRequest, { params }: { params: Promise<{ action: string }> }) {
    const { action } = await params;

    switch (action) {
        case 'sign-in':
            return logtoClient.handleSignIn()(request);
        case 'sign-out':
            return logtoClient.handleSignOut()(request);
        case 'callback':
            return logtoClient.handleSignInCallback()(request);
        case 'user':
            return logtoClient.handleUser()(request);
        default:
            return new Response('Not Found', { status: 404 });
    }
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ action: string }> }) {
    const { action } = await params;

    switch (action) {
        case 'sign-in':
            return logtoClient.handleSignIn()(request);
        case 'sign-out':
            return logtoClient.handleSignOut()(request);
        case 'callback':
            return logtoClient.handleSignInCallback()(request);
        case 'user':
            return logtoClient.handleUser()(request);
        default:
            return new Response('Not Found', { status: 404 });
    }
}

