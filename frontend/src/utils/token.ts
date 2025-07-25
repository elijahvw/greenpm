// Utility functions for JWT token handling

export const isTokenExpired = (token: string): boolean => {
  try {
    // Decode JWT token (without verification)
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    const payload = JSON.parse(jsonPayload);
    const currentTime = Math.floor(Date.now() / 1000);
    
    // Get login time from localStorage
    const loginTime = localStorage.getItem('loginTime');
    const loginTimeMs = loginTime ? parseInt(loginTime) : 0;
    const timeSinceLogin = loginTimeMs ? (Date.now() - loginTimeMs) / 1000 : 0;
    
    console.log('🔍 Token payload:', payload);
    console.log('🔍 Current time:', currentTime, '(' + new Date(currentTime * 1000).toISOString() + ')');
    console.log('🔍 Token expires at:', payload.exp, '(' + new Date(payload.exp * 1000).toISOString() + ')');
    console.log('🔍 Time until expiration:', payload.exp - currentTime, 'seconds');
    console.log('🔍 Login time:', loginTimeMs ? new Date(loginTimeMs).toISOString() : 'unknown');
    console.log('🔍 Time since login:', Math.floor(timeSinceLogin), 'seconds');
    
    return payload.exp < currentTime;
  } catch (error) {
    console.error('❌ Error parsing token:', error);
    return true; // Assume expired if we can't parse it
  }
};

export const getTokenTimeUntilExpiration = (token: string): number => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    const payload = JSON.parse(jsonPayload);
    const currentTime = Math.floor(Date.now() / 1000);
    
    return payload.exp - currentTime; // seconds until expiration
  } catch (error) {
    return 0;
  }
};