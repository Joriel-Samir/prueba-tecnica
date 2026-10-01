import { FormEvent, useEffect, useMemo, useState } from 'react';
import type { Activity, Associate } from '../../types';

interface ActivityModalProps {
  isOpen: boolean;
  onClose: () => void;
  activity?: Activity | null;
  associates: Associate[];
  onSave: (payload: Partial<Activity>) => Promise<void>;
}

export function ActivityModal({ isOpen, onClose, activity, associates, onSave }: ActivityModalProps) {
  const [form, setForm] = useState<Partial<Activity>>({
    title: activity?.title ?? '',
    notes: activity?.notes ?? '',
    start: activity?.start ?? '2026-10-03T09:00',
    end: activity?.end ?? '2026-10-03T10:30',
    assignee: activity?.assignee ?? 'Ana García',
    assigneeId: activity?.assigneeId,
  });

  useEffect(() => {
    setForm({
      title: activity?.title ?? '',
      notes: activity?.notes ?? '',
      start: activity?.start ?? '2026-10-03T09:00',
      end: activity?.end ?? '2026-10-03T10:30',
      assignee: activity?.assignee ?? 'Ana García',
      assigneeId: activity?.assigneeId,
    });
  }, [activity, isOpen]);

  const modalTitle = useMemo(() => (activity ? 'Editar evento' : 'Nuevo evento'), [activity]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSave(form);
    onClose();
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="event-dialog-title">
      <div className="modal-card">
        <div className="modal-header">
          <h2 id="event-dialog-title">{modalTitle}</h2>
          <button type="button" onClick={onClose} aria-label="Cerrar modal">
            ×
          </button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          <label htmlFor="start-date">Fecha y hora de inicio</label>
          <input
            id="start-date"
            type="datetime-local"
            value={form.start ?? ''}
            onChange={(event) => setForm((current) => ({ ...current, start: event.target.value }))}
          />

          <label htmlFor="end-date">Fecha y hora de fin</label>
          <input
            id="end-date"
            type="datetime-local"
            value={form.end ?? ''}
            onChange={(event) => setForm((current) => ({ ...current, end: event.target.value }))}
          />

          <label htmlFor="activity-title">Título</label>
          <input
            id="activity-title"
            type="text"
            value={form.title ?? ''}
            placeholder="Descripción corta"
            onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
          />

          <label htmlFor="assignee-id">Asociado</label>
          <select
            id="assignee-id"
            aria-label="Asociado"
            required={!activity}
            value={form.assigneeId ?? ''}
            onChange={(event) => setForm((current) => ({
              ...current,
              assigneeId: event.target.value ? Number(event.target.value) : undefined,
            }))}
          >
            <option value="">Selecciona un asociado</option>
            {associates.map((associate) => (
              <option key={associate.id} value={associate.id}>
                {associate.name} {associate.lastName} — {associate.email}
              </option>
            ))}
          </select>

          <label htmlFor="notes">Notas</label>
          <textarea
            id="notes"
            rows={4}
            placeholder="Información adicional"
            value={form.notes ?? ''}
            onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))}
          />

          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
}
