/**
 * NutriLens API utility
 * All requests are sent to the FastAPI backend at http://localhost:8000
 */

const BASE_URL = 'http://localhost:8000';

/** Helper: get stored JWT token */
function getToken() {
    return localStorage.getItem('nutrilens_token');
}

/** Helper: build headers, optionally with Authorization */
function buildHeaders(includeAuth = true, isJson = true) {
    const headers = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    if (includeAuth) {
        const token = getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

/** Helper: handle response – throws error with detail message on failure */
async function handleResponse(res) {
    if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
            const data = await res.json();
            detail = data.detail || detail;
        } catch {/* ignore parse errors */ }
        throw new Error(detail);
    }
    return res.json();
}

// ─── AUTH ──────────────────────────────────────────────────────────────────

/**
 * POST /auth/signup
 * @param {{ name: string, email: string, password: string }} userData
 * @returns {{ access_token: string, token_type: string }}
 */
export async function signup(userData) {
    const res = await fetch(`${BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: buildHeaders(false),
        body: JSON.stringify(userData),
    });
    return handleResponse(res);
}

/**
 * POST /auth/login
 * @param {{ email: string, password: string }} credentials
 * @returns {{ access_token: string, token_type: string }}
 */
export async function login(credentials) {
    const res = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: buildHeaders(false),
        body: JSON.stringify(credentials),
    });
    return handleResponse(res);
}

/**
 * POST /auth/forgot-password
 * @param {{ email: string }} data
 */
export async function forgotPassword(data) {
    const res = await fetch(`${BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: buildHeaders(false),
        body: JSON.stringify(data),
    });
    return handleResponse(res);
}

/**
 * POST /auth/reset-password
 * @param {{ token: string, new_password: string }} data
 */
export async function resetPassword(data) {
    const res = await fetch(`${BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: buildHeaders(false),
        body: JSON.stringify(data),
    });
    return handleResponse(res);
}

// ─── USERS ─────────────────────────────────────────────────────────────────

/**
 * GET /users/me
 * @returns {{ id, name, email, created_at }}
 */
export async function getMe() {
    const res = await fetch(`${BASE_URL}/users/me`, {
        headers: buildHeaders(),
    });
    return handleResponse(res);
}

/**
 * PUT /users/me
 * @param {{ name?: string, email?: string }} data
 * @returns {{ id, name, email, created_at }}
 */
export async function updateMe(data) {
    const res = await fetch(`${BASE_URL}/users/me`, {
        method: 'PUT',
        headers: buildHeaders(),
        body: JSON.stringify(data),
    });
    return handleResponse(res);
}

// ─── SCANS ─────────────────────────────────────────────────────────────────

/**
 * POST /scans/precision
 * @param {{ nutritionImage: File, ingredientsImage: File, claim: string, category: string }} params
 */
export async function precisionScan({ nutritionImage, ingredientsImage, claim, category }) {
    const form = new FormData();
    form.append('nutrition_image', nutritionImage);
    form.append('ingredients_image', ingredientsImage);
    form.append('claim', claim);
    form.append('category', category);

    const token = getToken();
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    // Do NOT set Content-Type; browser handles multipart boundary

    const res = await fetch(`${BASE_URL}/scans/precision`, {
        method: 'POST',
        headers,
        body: form,
    });
    return handleResponse(res);
}

/**
 * POST /scans/quick
 * @param {{ image: File, claim: string, category: string }} params
 */
export async function quickScan({ image, claim, category }) {
    const form = new FormData();
    form.append('image', image);
    form.append('claim', claim);
    form.append('category', category);

    const token = getToken();
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${BASE_URL}/scans/quick`, {
        method: 'POST',
        headers,
        body: form,
    });
    return handleResponse(res);
}

/**
 * GET /scans/history
 * @returns {Array<ScanHistoryItem>}
 */
export async function getScanHistory() {
    const res = await fetch(`${BASE_URL}/scans/history`, {
        headers: buildHeaders(),
    });
    return handleResponse(res);
}

/**
 * GET /scans/:id
 * @param {number|string} scanId
 * @returns {ScanResponse}
 */
export async function getScanById(scanId) {
    const res = await fetch(`${BASE_URL}/scans/${scanId}`, {
        headers: buildHeaders(),
    });
    return handleResponse(res);
}
