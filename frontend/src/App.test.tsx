import { beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { api } from './lib/api';

vi.mock('./lib/api', async () => {
  const actual = await vi.importActual<typeof import('./lib/api')>('./lib/api');
  return {
    ...actual,
    getStoredSession: () => null,
    login: undefined,
    api: {
      ...actual.api,
      login: vi.fn().mockResolvedValue({
        access: 'access-token',
        refresh: 'refresh-token',
        user: { id: '1', name: 'Admin', email: 'admin@ihungo.test', role: 'admin' },
      }),
      register: vi.fn().mockResolvedValue({ message: 'Registro recibido.' }),
      getAssociates: vi.fn().mockResolvedValue([]),
    },
  };
});

describe('App', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
    vi.mocked(api.login).mockResolvedValue({
      access: 'access-token',
      refresh: 'refresh-token',
      user: { id: '1', name: 'Admin', email: 'admin@ihungo.test', role: 'admin' },
    });
    vi.mocked(api.register).mockResolvedValue({ message: 'Registro recibido.' });
  });

  it('renders the login form and allows sign in', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText(/correo electrónico de acceso/i), 'admin@ihungo.test');
    await user.type(screen.getByLabelText(/contraseña de acceso/i), 'Password123');
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(screen.getByRole('heading', { name: /actividades/i })).toBeInTheDocument();
  });

  it('shows an error when the API rejects the login', async () => {
    vi.mocked(api.login).mockRejectedValueOnce(new Error('Credenciales inválidas'));
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText(/correo electrónico de acceso/i), 'bad@example.com');
    await user.type(screen.getByLabelText(/contraseña de acceso/i), 'wrong-password');
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(await screen.findByText(/no se pudo iniciar sesión/i)).toBeInTheDocument();
  });

  it('validates registration passwords before calling the API', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText('Nombre'), 'Ana Pérez');
    await user.type(screen.getByLabelText('Correo'), 'ana@example.com');
    await user.type(screen.getByLabelText('Contraseña', { selector: '#register-password' }), 'Password123');
    await user.type(screen.getByLabelText('Repetir contraseña'), 'Different123');
    await user.click(screen.getByRole('button', { name: /crear cuenta/i }));

    expect(screen.getByText(/no coinciden/i)).toBeInTheDocument();
    expect(api.register).not.toHaveBeenCalled();
  });

  it('confirma un registro válido y limpia el formulario', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText('Nombre'), 'Ana Pérez');
    await user.type(screen.getByLabelText('Correo'), 'ana@example.com');
    await user.type(screen.getByLabelText('Contraseña', { selector: '#register-password' }), 'Password123');
    await user.type(screen.getByLabelText('Repetir contraseña'), 'Password123');
    await user.click(screen.getByRole('button', { name: /crear cuenta/i }));

    expect(await screen.findByText('Registro recibido.')).toBeInTheDocument();
    expect(api.register).toHaveBeenCalledWith({
      name: 'Ana Pérez',
      email: 'ana@example.com',
      password: 'Password123',
      confirmPassword: 'Password123',
    });
  });
});
