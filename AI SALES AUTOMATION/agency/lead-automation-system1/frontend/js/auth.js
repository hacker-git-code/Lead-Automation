/**
 * Authentication Service for Lead Automation System
 * Provides integration with Supabase for user authentication
 */

// Auth service object
const Auth = (function() {
    // Initialize Supabase client
    const SUPABASE_URL = 'https://your-project-ref.supabase.co'; // Replace with your Supabase URL
    const SUPABASE_ANON_KEY = 'your-anon-key'; // Replace with your Supabase anon key

    const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    // Token storage key
    const TOKEN_KEY = 'lead_automation_token';
    const USER_KEY = 'lead_automation_user';

    /**
     * Sign up a new user
     * @param {string} email User email address
     * @param {string} password User password
     * @param {string} fullName User's full name
     * @returns {Promise} Response with success/error
     */
    const signup = async (email, password, fullName) => {
        try {
            // Sign up with Supabase Auth
            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        full_name: fullName
                    }
                }
            });

            if (error) throw error;

            // Add user to users table with custom data
            // This will be handled by backend API
            await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    full_name: fullName
                })
            });

            return { success: true, message: 'User registered successfully' };
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, error: error.message || 'Signup failed' };
        }
    };

    /**
     * Log in an existing user
     * @param {string} email User email address
     * @param {string} password User password
     * @param {boolean} rememberMe Whether to remember the user
     * @returns {Promise} Response with success/error and user data
     */
    const login = async (email, password, rememberMe = false) => {
        try {
            // Sign in with Supabase Auth
            const { data, error } = await supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) throw error;

            // Get session and user data
            const session = data.session;
            const user = data.user;

            // Store token and user data
            sessionStorage.setItem(TOKEN_KEY, session.access_token);
            sessionStorage.setItem(USER_KEY, JSON.stringify({
                id: user.id,
                email: user.email,
                full_name: user.user_metadata?.full_name || ''
            }));

            // If remember me is checked, also store in localStorage
            if (rememberMe) {
                localStorage.setItem(TOKEN_KEY, session.access_token);
                localStorage.setItem(USER_KEY, JSON.stringify({
                    id: user.id,
                    email: user.email,
                    full_name: user.user_metadata?.full_name || ''
                }));
            }

            // Update last login via backend API
            await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify({
                    user_id: user.id
                })
            });

            return {
                success: true,
                user: {
                    id: user.id,
                    email: user.email,
                    full_name: user.user_metadata?.full_name || ''
                }
            };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message || 'Login failed' };
        }
    };

    /**
     * Log out the current user
     * @returns {Promise} Response with success/error
     */
    const logout = async () => {
        try {
            const { error } = await supabase.auth.signOut();

            if (error) throw error;

            // Clear stored tokens and user data
            sessionStorage.removeItem(TOKEN_KEY);
            sessionStorage.removeItem(USER_KEY);
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);

            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            return { success: false, error: error.message || 'Logout failed' };
        }
    };

    /**
     * Send password reset email
     * @param {string} email User email address
     * @returns {Promise} Response with success/error
     */
    const resetPassword = async (email) => {
        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: window.location.origin + '/reset-password.html'
            });

            if (error) throw error;

            return { success: true, message: 'Password reset email sent' };
        } catch (error) {
            console.error('Password reset error:', error);
            return { success: false, error: error.message || 'Password reset failed' };
        }
    };

    /**
     * Change user password
     * @param {string} newPassword New password
     * @returns {Promise} Response with success/error
     */
    const changePassword = async (newPassword) => {
        try {
            const { error } = await supabase.auth.updateUser({
                password: newPassword
            });

            if (error) throw error;

            return { success: true, message: 'Password updated successfully' };
        } catch (error) {
            console.error('Password change error:', error);
            return { success: false, error: error.message || 'Password change failed' };
        }
    };

    /**
     * Get the current logged in user
     * @returns {Object|null} User data or null if not logged in
     */
    const getCurrentUser = () => {
        // Check session storage first
        let userData = sessionStorage.getItem(USER_KEY);

        // If not in session storage, check local storage
        if (!userData) {
            userData = localStorage.getItem(USER_KEY);
        }

        return userData ? JSON.parse(userData) : null;
    };

    /**
     * Get the current auth token
     * @returns {string|null} Auth token or null if not logged in
     */
    const getToken = () => {
        // Check session storage first
        let token = sessionStorage.getItem(TOKEN_KEY);

        // If not in session storage, check local storage
        if (!token) {
            token = localStorage.getItem(TOKEN_KEY);
        }

        return token;
    };

    /**
     * Check if user is authenticated
     * @returns {boolean} True if user is authenticated
     */
    const isAuthenticated = () => {
        return !!getToken();
    };

    /**
     * Initialize auth service - check if token exists and validate
     */
    const init = async () => {
        const token = getToken();

        if (token) {
            // Validate token with Supabase
            const { data, error } = await supabase.auth.getUser(token);

            if (error || !data.user) {
                // Token is invalid, clear storage
                sessionStorage.removeItem(TOKEN_KEY);
                sessionStorage.removeItem(USER_KEY);
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem(USER_KEY);

                // Redirect to login if not already there
                if (!window.location.pathname.includes('/login.html') &&
                    !window.location.pathname.includes('/signup.html')) {
                    window.location.href = '/login.html';
                }
            } else {
                // Token is valid, user is authenticated
                // Update user data if different
                const currentUser = getCurrentUser();
                if (!currentUser || currentUser.id !== data.user.id) {
                    const userData = {
                        id: data.user.id,
                        email: data.user.email,
                        full_name: data.user.user_metadata?.full_name || ''
                    };

                    sessionStorage.setItem(USER_KEY, JSON.stringify(userData));

                    if (localStorage.getItem(TOKEN_KEY)) {
                        localStorage.setItem(USER_KEY, JSON.stringify(userData));
                    }
                }

                // Redirect to dashboard if on login page
                if (window.location.pathname.includes('/login.html') ||
                    window.location.pathname.includes('/signup.html')) {
                    window.location.href = '/index.html';
                }
            }
        } else {
            // No token, check if on protected page
            if (!window.location.pathname.includes('/login.html') &&
                !window.location.pathname.includes('/signup.html')) {
                window.location.href = '/login.html';
            }
        }
    };

    // Run init when script loads
    if (window.location.pathname !== '/login.html' &&
        window.location.pathname !== '/signup.html' &&
        window.location.pathname !== '/reset-password.html') {
        init();
    }

    // Public API
    return {
        signup,
        login,
        logout,
        resetPassword,
        changePassword,
        getCurrentUser,
        getToken,
        isAuthenticated,
        init
    };
})();

// Check for authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    // Protect pages from unauthenticated access
    if (window.location.pathname !== '/login.html' &&
        window.location.pathname !== '/signup.html' &&
        window.location.pathname !== '/reset-password.html') {

        if (!Auth.isAuthenticated()) {
            window.location.href = '/login.html';
        }
    }
});
