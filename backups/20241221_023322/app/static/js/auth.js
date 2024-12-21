// Firebase Authentication Functions

// Sign in with email and password
export async function signIn(email, password) {
    try {
        if (!window.auth) {
            throw new Error('Firebase Auth not initialized');
        }
        const userCredential = await window.auth.signInWithEmailAndPassword(email, password);
        if (userCredential.user) {
            // Get the ID token
            const idToken = await userCredential.user.getIdToken();
            
            // Send token to your backend
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: idToken })
            });

            if (!response.ok) {
                throw new Error('Failed to authenticate with server');
            }

            const data = await response.json();
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        }
    } catch (error) {
        console.error('Sign in error:', error);
        throw error;
    }
}

// Sign out
export async function signOut() {
    try {
        if (!window.auth) {
            throw new Error('Firebase Auth not initialized');
        }
        await window.auth.signOut();
        // Clear server session
        await fetch('/logout', {
            method: 'GET'
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Sign out error:', error);
        throw error;
    }
}

// Initialize auth state observer
export function initAuthStateObserver(callback) {
    if (!window.auth) {
        console.error('Firebase Auth not initialized');
        return;
    }
    
    window.auth.onAuthStateChanged((user) => {
        if (callback) {
            callback(user);
        }
        
        // Update UI based on auth state
        const userMenuButton = document.getElementById('user-menu-button');
        const loginButton = document.getElementById('login-button');
        const logoutButton = document.getElementById('logout-button');
        
        if (user) {
            // User is signed in
            if (userMenuButton) userMenuButton.style.display = 'block';
            if (loginButton) loginButton.style.display = 'none';
            if (logoutButton) {
                logoutButton.style.display = 'block';
                // Add click event listener for logout
                logoutButton.addEventListener('click', async () => {
                    try {
                        await signOut();
                    } catch (error) {
                        console.error('Logout error:', error);
                    }
                });
            }
        } else {
            // User is signed out
            if (userMenuButton) userMenuButton.style.display = 'none';
            if (loginButton) loginButton.style.display = 'block';
            if (logoutButton) logoutButton.style.display = 'none';
        }
    });
}
