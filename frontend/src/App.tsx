import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FormEvent, useState } from 'react';
import { ActivityCalendar } from './features/activities/ActivityCalendar';
import { LoginForm } from './features/auth/LoginForm';
import { api, getStoredSession, persistSession } from './lib/api';
import type { AuthSession, RegisterRequest } from './types';

function AppContent() {
  const [session, setSession] = useState<AuthSession | null>(() => getStoredSession());
  const [loginError, setLoginError] = useState('');
  const [isSubmittingLogin, setIsSubmittingLogin] = useState(false);
  const [registerMessage, setRegisterMessage] = useState('');
  const [registerError, setRegisterError] = useState('');
  const [registerForm, setRegisterForm] = useState<RegisterRequest>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleLogin = async (email: string, password: string) => {
    setLoginError('');

    if (!email || !password) {
      setLoginError('Debes completar correo y contraseña.');
      return;
    }

    setIsSubmittingLogin(true);

    try {
      const nextSession = await api.login({ email, password });
      persistSession(nextSession);
      setSession(nextSession);
    } catch {
      setLoginError('No se pudo iniciar sesión. Intenta otra vez.');
    } finally {
      setIsSubmittingLogin(false);
    }
  };

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setRegisterError('');
    setRegisterMessage('');

    if (!registerForm.name.trim() || !registerForm.email.trim()) {
      setRegisterError('Nombre y correo son obligatorios.');
      return;
    }

    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email);
    if (!emailOk) {
      setRegisterError('Introduce un correo válido.');
      return;
    }

    if (registerForm.password.length < 8) {
      setRegisterError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      setRegisterError('Las contraseñas no coinciden.');
      return;
    }

    try {
      const result = await api.register(registerForm);
      setRegisterMessage(result.message);
      setRegisterForm({ name: '', email: '', password: '', confirmPassword: '' });
    } catch (error) {
      setRegisterError(error instanceof Error ? error.message : 'No se pudo enviar el registro.');
    }
  };

  const handleLogout = () => {
    persistSession(null);
    setSession(null);
    setLoginError('');
  };

  return (
    <main className="app-shell">
      {session ? (
        <ActivityCalendar user={session.user} onLogout={handleLogout} />
      ) : (
        <section className="auth-layout" aria-label="Formulario de acceso">
          <div className="auth-panel auth-panel--login">
            <LoginForm
              onLogin={handleLogin}
              isSubmitting={isSubmittingLogin}
              errorMessage={loginError}
            />
          </div>

          <aside className="auth-panel auth-panel--register" aria-label="Registro de usuario">
            <div className="register-copy">
              <span className="eyebrow">Registro</span>
              <h2>Crea tu cuenta</h2>
              <p>Gestiona la asignación de actividades y mantiene a tu equipo organizado.</p>
            </div>

            <form className="register-form" onSubmit={handleRegister}>
              <label htmlFor="name">Nombre</label>
              <input
                id="name"
                name="name"
                type="text"
                value={registerForm.name}
                onChange={(event) => setRegisterForm((current) => ({ ...current, name: event.target.value }))}
              />

              <label htmlFor="register-email">Correo</label>
              <input
                id="register-email"
                name="register-email"
                type="email"
                value={registerForm.email}
                onChange={(event) => setRegisterForm((current) => ({ ...current, email: event.target.value }))}
              />

              <label htmlFor="register-password">Contraseña</label>
              <input
                id="register-password"
                name="register-password"
                type="password"
                value={registerForm.password}
                onChange={(event) => setRegisterForm((current) => ({ ...current, password: event.target.value }))}
              />

              <label htmlFor="confirm-password">Repetir contraseña</label>
              <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                value={registerForm.confirmPassword}
                onChange={(event) => setRegisterForm((current) => ({ ...current, confirmPassword: event.target.value }))}
              />

              {registerError ? <p className="form-error">{registerError}</p> : null}
              {registerMessage ? <p className="form-success">{registerMessage}</p> : null}

              <button type="submit">Crear cuenta</button>
            </form>
          </aside>
        </section>
      )}
    </main>
  );
}

export default function App() {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
