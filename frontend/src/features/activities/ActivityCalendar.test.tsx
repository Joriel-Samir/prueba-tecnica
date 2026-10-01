import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ActivityCalendar } from './ActivityCalendar';
import { api } from '../../lib/api';

vi.mock('../../lib/api', () => ({
  api: {
    getActivities: vi.fn(),
    getAssociates: vi.fn(),
    createActivity: vi.fn(),
    updateActivity: vi.fn(),
    deleteActivity: vi.fn(),
  },
}));

function renderCalendar(role: 'admin' | 'associate' = 'admin') {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <ActivityCalendar
        user={{ id: '1', name: 'Admin', email: 'admin@example.com', role }}
        onLogout={vi.fn()}
      />
    </QueryClientProvider>,
  );
}

describe('ActivityCalendar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getActivities).mockResolvedValue([
      {
        id: '1',
        title: 'Visita de cliente',
        notes: 'Seguimiento',
        start: '2026-10-03T09:00',
        end: '2026-10-03T10:00',
        assignee: 'Ana Pérez',
        assigneeId: 7,
      },
    ]);
    vi.mocked(api.getAssociates).mockResolvedValue([
      { id: 7, name: 'Ana', lastName: 'Pérez', email: 'ana@example.com' },
    ]);
  });

  it('loads activities and navigates between calendar views', async () => {
    renderCalendar();

    expect(await screen.findByText('Visita de cliente')).toBeInTheDocument();
    await fireEvent.click(screen.getByRole('button', { name: 'Agenda' }));
    expect(await screen.findByText('Visita de cliente')).toBeInTheDocument();
    await fireEvent.click(screen.getByRole('button', { name: 'Siguiente' }));
    expect(api.getActivities).toHaveBeenCalledTimes(3);
  });

  it('opens the activity modal with the real associate selector', async () => {
    renderCalendar();

    await screen.findByText('Visita de cliente');
    await fireEvent.click(screen.getByRole('button', { name: 'Crear actividad' }));

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Ana Pérez/ })).toBeInTheDocument();
  });

  it('restricts creation and deletion controls for associates', async () => {
    renderCalendar('associate');

    const createButton = screen.getByRole('button', { name: 'Crear actividad' });
    const deleteButton = screen.getByRole('button', { name: 'Eliminar actividad seleccionada' });
    expect(createButton).toBeDisabled();
    await screen.findByText('Visita de cliente');
    await fireEvent.click(screen.getByText('Visita de cliente'));
    expect(screen.getByRole('button', { name: 'Editar actividad' }).hasAttribute('disabled')).toBe(false);
    expect(deleteButton.hasAttribute('disabled')).toBe(false);
  });
});
