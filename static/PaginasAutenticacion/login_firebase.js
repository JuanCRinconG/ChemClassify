/**
 * Firebase Auth on the login page: sign-in or create account, then POST idToken to Flask.
 * Reads config from <script type="application/json" id="chem-firebase-config-json"> (Jinja tojson).
 *
 * Diagnosis: open DevTools (F12) → Console. Look for [ChemAuth:firebase] vs [ChemAuth:session].
 *
 * Institutional email rules from #chem-login-email-rules-json run before any Firebase call.
 */
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js';
import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
} from 'https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js';

/** @returns {string|null} null = unknown code (caller may show code + console) */
function mapFirebaseAuthError(code) {
    switch (code) {
        case 'auth/email-already-in-use':
            return 'That email is already registered. Try Sign in instead.';
        case 'auth/invalid-email':
            return 'Invalid email address.';
        case 'auth/weak-password':
            return 'Password is too weak (use at least 6 characters).';
        case 'auth/user-not-found':
        case 'auth/wrong-password':
        case 'auth/invalid-credential':
            return 'Wrong email or password, or use Create account if you are new.';
        case 'auth/too-many-requests':
            return 'Too many attempts. Try again later.';
        case 'auth/network-request-failed':
            return 'Network error talking to Firebase. Check your connection and try again.';
        case 'auth/operation-not-allowed':
            return 'Email/password sign-in is disabled in the Firebase project (Console → Authentication → Sign-in method).';
        case 'auth/invalid-api-key':
            return 'Invalid Firebase web API key. Check CHEMCLASSIFY_FIREBASE_* env or FirebaseClienteWeb config.';
        case 'auth/configuration-not-found':
            return 'Firebase Auth is not configured for this app (check Firebase project and web app registration).';
        default:
            return null;
    }
}

async function postIdTokenToFlask(idToken) {
    const loginUrl = document.getElementById('chem-login-form')?.getAttribute('data-login-url');
    if (!loginUrl) {
        throw new Error('Missing login URL');
    }
    const res = await fetch(loginUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }),
        credentials: 'same-origin',
    });
    const data = await res.json().catch(function () {
        return {};
    });
    if (!res.ok) {
        console.error('[ChemAuth:session]', {
            httpStatus: res.status,
            serverBody: data,
                hint:
                res.status === 400
                    ? 'Server rejected the request (e.g. token or policy).'
                    : 'Token rejected or server error.',
        });
        throw new Error(data.error || res.statusText || 'Server rejected the session (HTTP ' + res.status + ').');
    }
    if (data.redirect) {
        window.location.assign(data.redirect);
        return;
    }
    console.error('[ChemAuth:session]', { unexpected: true, data });
    throw new Error('Unexpected server response (no redirect).');
}

/**
 * @returns {object | null}
 */
function readLoginEmailRules() {
    const el = document.getElementById('chem-login-email-rules-json');
    if (!el) {
        return null;
    }
    try {
        return JSON.parse((el.textContent || '').trim());
    } catch (e) {
        console.error('[ChemAuth:rules]', 'Invalid JSON in #chem-login-email-rules-json', e);
        return null;
    }
}

/** Mirrors DominioPermitido.dominio_en_cuenta_es_permitido */
function dominioInstitucionalPermitido(dominioTrasArroba, dominioPermitido, permitirSubdominios) {
    const d = dominioTrasArroba.trim().toLowerCase();
    const permitido = dominioPermitido.trim().toLowerCase().replace(/^@/, '');
    if (!d || !permitido) {
        return false;
    }
    if (d === permitido) {
        return true;
    }
    if (permitirSubdominios && d.endsWith('.' + permitido)) {
        return true;
    }
    return false;
}

/**
 * Mirrors ValidacionFormatoIdentificacion.validar_identificador_cuenta (same messages).
 * @returns {string|null} error message or null if valid
 */
function validarIdentificadorCuentaCliente(cuenta, rules) {
    if (!rules || !rules.ejemploCorreo || !rules.dominioPermitido) {
        return 'Missing email validation rules from server.';
    }
    const ejemplo = rules.ejemploCorreo;
    const dominioCfg = rules.dominioPermitido;
    const permitirSub = Boolean(rules.permitirSubdominios);

    cuenta = (cuenta || '').trim();
    if (!cuenta) {
        return null;
    }

    if (cuenta.indexOf('@') === -1) {
        return 'Ingresa un correo con @ y tu dominio institucional (e.g. ' + ejemplo + ').';
    }
    if (cuenta.split('@').length - 1 !== 1) {
        return 'Ingresa solo un @ en el correo (e.g. ' + ejemplo + ').';
    }
    const parts = cuenta.split('@');
    const local = parts[0];
    const domain = parts.slice(1).join('@');
    if (!local) {
        return 'Ingresa el nombre del correo (e.g. ' + ejemplo + ').';
    }
    if (!domain) {
        return 'Ingresa el dominio del correo despues del @ (e.g. @' + dominioCfg + ').';
    }
    if (domain.indexOf('.') === -1) {
        return 'El dominio despues del @ debe tener nombre y extension (e.g. .edu).';
    }
    if (!dominioInstitucionalPermitido(domain, dominioCfg, permitirSub)) {
        return 'Utiliza solo cuentas institucionales (e.g. ' + ejemplo + ').';
    }
    return null;
}

function readFirebaseWebConfig() {
    const el = document.getElementById('chem-firebase-config-json');
    if (!el) {
        return null;
    }
    try {
        return JSON.parse((el.textContent || '').trim());
    } catch (e) {
        console.error('[ChemAuth:config]', 'Invalid JSON in #chem-firebase-config-json', e);
        return null;
    }
}

function userFacingMessage(mode, err) {
    const code = err && err.code ? String(err.code) : '';

    // Firebase errors have err.code like auth/...
    if (code) {
        const mapped = mapFirebaseAuthError(code);
        if (mapped) {
            return mapped;
        }
        return 'Firebase: ' + code + ' (see browser console F12 for [ChemAuth:firebase]).';
    }

    // fetch() / server errors are plain Error with message only
    if (err && err.message) {
        return err.message;
    }

    return 'Could not complete ' + (mode === 'create' ? 'registration' : 'sign-in') + '. See console (F12).';
}

function init() {
    const cfg = readFirebaseWebConfig();
    if (!cfg || typeof cfg !== 'object' || !cfg.apiKey) {
        console.warn('[ChemAuth:config]', 'Missing or invalid Firebase web config; buttons will not work.');
        return;
    }

    const app = initializeApp(cfg);
    const auth = getAuth(app);

    const form = document.getElementById('chem-login-form');
    const emailEl = document.getElementById('accountName');
    const passEl = document.getElementById('password');
    const btnSignIn = document.getElementById('chem-btn-signin');
    const btnCreate = document.getElementById('chem-btn-create');

    if (!form || !emailEl || !passEl || !btnSignIn || !btnCreate) {
        console.warn('[ChemAuth:dom]', 'Login form elements missing.');
        return;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
    });

    const emailRules = readLoginEmailRules();

    async function run(mode) {
        const email = (emailEl.value || '').trim();
        const password = passEl.value || '';
        if (!email || !password) {
            window.SistemasErrores?.mostrar('Please enter both email and password.');
            return;
        }
        const identError = validarIdentificadorCuentaCliente(email, emailRules);
        if (identError) {
            console.info('[ChemAuth:rules]', 'blocked before Firebase', email);
            window.SistemasErrores?.mostrar(identError);
            return;
        }
        try {
            let cred;
            if (mode === 'create') {
                console.info('[ChemAuth:firebase]', 'createUserWithEmailAndPassword', email);
                cred = await createUserWithEmailAndPassword(auth, email, password);
            } else {
                console.info('[ChemAuth:firebase]', 'signInWithEmailAndPassword', email);
                cred = await signInWithEmailAndPassword(auth, email, password);
            }
            const idToken = await cred.user.getIdToken();
            console.info('[ChemAuth:session]', 'POST idToken to Flask /login');
            await postIdTokenToFlask(idToken);
        } catch (err) {
            const code = err && err.code ? String(err.code) : '';
            if (code) {
                console.error('[ChemAuth:firebase]', mode, code, err.message || err);
            } else {
                console.error('[ChemAuth:session]', mode, err.message || err, err);
            }
            window.SistemasErrores?.mostrar(userFacingMessage(mode, err));
        }
    }

    btnSignIn.addEventListener('click', function () {
        run('signin');
    });
    btnCreate.addEventListener('click', function () {
        run('create');
    });
}

init();
