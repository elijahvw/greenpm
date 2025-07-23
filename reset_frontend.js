// Reset script to run in browser console
console.log('🧹 Resetting Green PM Frontend...');

// Clear all storage
localStorage.clear();
sessionStorage.clear();

// Clear all cookies
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});

// Clear service worker cache
if ('caches' in window) {
    caches.keys().then(names => {
        names.forEach(name => {
            caches.delete(name);
        });
    });
}

// Clear any React state by forcing a hard reload
console.log('✅ Frontend reset complete! Reloading...');
setTimeout(() => {
    window.location.href = 'http://localhost:3000/login';
}, 1000);