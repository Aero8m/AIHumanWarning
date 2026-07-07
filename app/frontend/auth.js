var AUTH_KEY = 'aihw_token';
var USER_KEY = 'aihw_user';

function setToken(token) {
    localStorage.setItem(AUTH_KEY, token);
}

function getToken() {
    return localStorage.getItem(AUTH_KEY);
}

function clearToken() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
}

function setUser(user) {
    localStorage.setItem(USER_KEY, user);
}

function getUser() {
    return localStorage.getItem(USER_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    clearToken();
    window.location.hash = 'page-auth';
}
