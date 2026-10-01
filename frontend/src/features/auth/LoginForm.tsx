import { FormEvent, useState } from 'react';

interface LoginFormProps {
  onLogin: (email: string, password: string) => void | Promise<void>;
  isSubmitting?: boolean;
  errorMessage?: string;
}

export function LoginForm({ onLogin, isSubmitting = false, errorMessage = '' }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void onLogin(email, password);
  };

  return (
    <div className="auth-card">
      <div className="auth-header">
        <span className="eyebrow">Ingreso</span>
        <h2>Inicia sesión</h2>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="email">Correo electrónico de acceso</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="password">Contraseña de acceso</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {errorMessage ? <p className="form-error">{errorMessage}</p> : null}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Ingresando...' : 'Iniciar sesión'}
        </button>
      </form>
    </div>
  );
}
