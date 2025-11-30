import { LogtoNextConfig } from '@logto/next';

export const logtoConfig: LogtoNextConfig = {
  appId: process.env.LOGTO_APP_ID!,
  appSecret: process.env.LOGTO_APP_SECRET!,
  endpoint: process.env.LOGTO_ENDPOINT!, // Example: http://localhost:3001
  baseUrl: process.env.NEXT_PUBLIC_APP_URL!, // Example: http://localhost:3000
  cookieSecret: process.env.LOGTO_COOKIE_SECRET!,
  cookieSecure: process.env.NODE_ENV === 'production',
  scopes: ['email', 'phone', 'profile'],
};
