async function handleLogout() {
  try {
    // Clear credentials from localStorage
    localStorage.removeItem('invoice_api_email');
    localStorage.removeItem('invoice_api_password');

    const res = await fetch('/logout', {
      method: 'GET',
      credentials: 'include' // Important to send session cookie
    });

    if (res.redirected) {
      // If server responds with a redirect, follow it
      window.location.href = res.url;
    } else {
      // Optional: fallback if redirect doesn't auto-follow
      window.location.href = '/sign_in';
    }
  } catch (error) {
    console.error('Logout failed:', error);
    alert('Failed to logout');
  }
}
