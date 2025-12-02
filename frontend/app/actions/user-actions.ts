'use server'

import { revalidatePath } from 'next/cache';

const LOGTO_ENDPOINT = process.env.LOGTO_ENDPOINT;
const LOGTO_APP_ID = process.env.LOGTO_APP_ID;
const LOGTO_APP_SECRET = process.env.LOGTO_APP_SECRET;

interface UpdateUserData {
    name?: string;
    phone?: string; // Logto expects 'phone' or 'customData' depending on config, but standard is usually root or custom. 
    // Standard OIDC 'phone_number' is often mapped. 
    // Logto Management API uses 'primaryPhone' or 'customData'. 
    // Let's assume we update 'name' and 'customData' or standard fields if supported.
    // Checking Logto docs, PATCH /api/users/{userId} supports: name, primaryEmail, primaryPhone, avatar, customData, etc.
    password?: string;
}

async function getManagementToken() {
    const tokenEndpoint = `${LOGTO_ENDPOINT}/oidc/token`;
    const auth = Buffer.from(`${LOGTO_APP_ID}:${LOGTO_APP_SECRET}`).toString('base64');

    const params = new URLSearchParams();
    params.append('grant_type', 'client_credentials');
    params.append('resource', `${LOGTO_ENDPOINT}/api`);
    params.append('scope', 'all');

    const response = await fetch(tokenEndpoint, {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${auth}`,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params,
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to get management token:', errorText);
        throw new Error('Failed to authenticate with management API');
    }

    const data = await response.json();
    return data.access_token;
}

export async function updateUserProfile(userId: string, data: UpdateUserData) {
    if (!userId) {
        return { success: false, message: 'User ID is required' };
    }

    try {
        const token = await getManagementToken();
        const updateBody: any = {};

        if (data.name) updateBody.name = data.name;
        if (data.phone) updateBody.primaryPhone = data.phone; // Try primaryPhone first
        if (data.password) updateBody.password = data.password;

        // If we have nothing to update
        if (Object.keys(updateBody).length === 0) {
            return { success: true, message: 'No changes to save' };
        }

        const response = await fetch(`${LOGTO_ENDPOINT}/api/users/${userId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateBody),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Failed to update user:', errorData);

            // Handle specific error for phone number (e.g., if it's not a valid format or duplicate)
            if (errorData.code === 'user.phone_number_invalid') {
                return { success: false, message: 'Invalid phone number format' };
            }

            return { success: false, message: errorData.message || 'Failed to update profile' };
        }

        revalidatePath('/dashboard/profile');
        return { success: true, message: 'Profile updated successfully' };

    } catch (error) {
        console.error('Error updating profile:', error);
        return { success: false, message: 'An unexpected error occurred' };
    }
}
