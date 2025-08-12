// Authentication module for Lead Automation System
const Auth = (function() {
    // Supabase client
    let supabase = null;

    // Initialize Supabase
    function initSupabase() {
        if (!supabase) {
            const supabaseUrl = 'https://your-supabase-url.supabase.co';
            const supabaseKey = 'your-public-anon-key';

            try {
                supabase = supabaseClient.createClient(supabaseUrl, supabaseKey);
            } catch (error) {
                console.error('Failed to initialize Supabase client:', error);
                return false;
            }
        }
        return true;
    }

    // Check if user is logged in
    function isLoggedIn() {
        const token = localStorage.getItem('authToken');
        const expiry = localStorage.getItem('authExpiry');

        if (!token || !expiry) {
            return false;
        }

        // Check if token is expired
        if (new Date().getTime() > parseInt(expiry)) {
            // Token expired, clean up
            localStorage.removeItem('authToken');
            localStorage.removeItem('authExpiry');
            localStorage.removeItem('user');
            return false;
        }

        return true;
    }

    // Redirect to login if not authenticated
    function checkAuth() {
        if (!isLoggedIn()) {
            window.location.href = 'login.html';
        }
    }

    // Get current user
    function getCurrentUser() {
        if (!isLoggedIn()) {
            return null;
        }

        const userStr = localStorage.getItem('user');
        if (!userStr) {
            return null;
        }

        try {
            return JSON.parse(userStr);
        } catch (e) {
            console.error('Failed to parse user data:', e);
            return null;
        }
    }

    // Login function
    async function login(email, password, rememberMe = false) {
        if (!initSupabase()) {
            return { success: false, error: "Authentication service unavailable" };
        }

        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) {
                throw error;
            }

            if (!data || !data.session) {
                throw new Error("Invalid authentication response");
            }

            // Store authentication info
            const expiryTime = rememberMe ?
                new Date().getTime() + (30 * 24 * 60 * 60 * 1000) : // 30 days
                new Date().getTime() + (8 * 60 * 60 * 1000);        // 8 hours

            localStorage.setItem('authToken', data.session.access_token);
            localStorage.setItem('authExpiry', expiryTime.toString());

            // Get user profile
            const { data: userData, error: userError } = await supabase
                .from('users')
                .select('*')
                .eq('id', data.user.id)
                .single();

            if (userError) {
                console.error('Error fetching user profile:', userError);
            } else if (userData) {
                localStorage.setItem('user', JSON.stringify({
                    id: data.user.id,
                    email: data.user.email,
                    role: userData.role || 'user',
                    full_name: userData.full_name || data.user.email.split('@')[0]
                }));
            } else {
                // Fallback if user profile not found
                localStorage.setItem('user', JSON.stringify({
                    id: data.user.id,
                    email: data.user.email,
                    role: 'user',
                    full_name: data.user.email.split('@')[0]
                }));
            }

            return { success: true };

        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message || "Login failed" };
        }
    }

    // Signup function
    async function signup(email, password, fullName) {
        if (!initSupabase()) {
            return { success: false, error: "Authentication service unavailable" };
        }

        try {
            // Register with Supabase Auth
            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        full_name: fullName
                    }
                }
            });

            if (error) {
                throw error;
            }

            if (!data || !data.user) {
                throw new Error("Invalid registration response");
            }

            // Add user to users table
            const { error: profileError } = await supabase
                .from('users')
                .insert([
                    {
                        id: data.user.id,
                        email: data.user.email,
                        full_name: fullName,
                        role: 'user'
                    }
                ]);

            if (profileError) {
                console.error('Error creating user profile:', profileError);
                // We continue despite this error as the auth account is created
            }

            return { success: true };

        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, error: error.message || "Registration failed" };
        }
    }

    // Logout function
    async function logout() {
        if (!initSupabase()) {
            // Clean local storage anyway
            localStorage.removeItem('authToken');
            localStorage.removeItem('authExpiry');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
            return { success: true };
        }

        try {
            const { error } = await supabase.auth.signOut();

            if (error) {
                throw error;
            }

            // Clean local storage
            localStorage.removeItem('authToken');
            localStorage.removeItem('authExpiry');
            localStorage.removeItem('user');

            // Redirect to login
            window.location.href = 'login.html';
            return { success: true };

        } catch (error) {
            console.error('Logout error:', error);
            return { success: false, error: error.message || "Logout failed" };
        }
    }

    // Password reset request
    async function resetPassword(email) {
        if (!initSupabase()) {
            return { success: false, error: "Authentication service unavailable" };
        }

        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: window.location.origin + '/reset-password.html'
            });

            if (error) {
                throw error;
            }

            return { success: true };

        } catch (error) {
            console.error('Password reset error:', error);
            return { success: false, error: error.message || "Password reset failed" };
        }
    }

    // Public methods
    return {
        isLoggedIn,
        checkAuth,
        getCurrentUser,
        login,
        signup,
        logout,
        resetPassword
    };
})();

// Check authentication on non-auth pages
if (document.location.pathname !== '/login.html' &&
    document.location.pathname !== '/signup.html' &&
    document.location.pathname !== '/reset-password.html') {
    document.addEventListener('DOMContentLoaded', function() {
        Auth.checkAuth();

        // Update user name in navbar if logged in
        const user = Auth.getCurrentUser();
        if (user) {
            const userNameElement = document.querySelector('.nav-link');
            if (userNameElement) {
                userNameElement.textContent = 'Welcome, ' + (user.full_name || user.email);
            }
        }

        // Add logout handler
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                Auth.logout();
            });
        }
    });
}
