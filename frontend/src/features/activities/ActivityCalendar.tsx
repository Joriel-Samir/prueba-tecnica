import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState, type DragEvent } from 'react';
import { api } from '../../lib/api';
import type { Activity, User } from '../../types';
import { BulkUploadPanel } from './BulkUploadPanel';
import { ActivityModal } from './ActivityModal';
import { TrackingPage } from '../tracking/TrackingPage';

type CalendarView = 'Mes' | 'Semana' | 'Día' | 'Agenda';

interface ActivityCalendarProps {
  user: User;
  onLogout: () => void;
}

const pad = (value: number) => String(value).padStart(2, '0');
const dateKey = (date: Date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
const parseDate = (value: string) => new Date(`${value}T00:00:00`);

function addDays(date: Date, amount: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + amount);
  return result;
}

function startOfWeek(date: Date): Date {
  const result = new Date(date);
  result.setDate(result.getDate() - ((result.getDay() + 6) % 7));
  result.setHours(0, 0, 0, 0);
  return result;
}

function addMonths(date: Date, amount: number): Date {
  const result = new Date(date);
  result.setMonth(result.getMonth() + amount, 1);
  return result;
}

function formatDateTime(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function moveActivityToDay(activity: Activity, target: Date): Partial<Activity> {
  const start = new Date(activity.start);
  const end = new Date(activity.end);
  const duration = Math.max(end.getTime() - start.getTime(), 60 * 60 * 1000);
  const nextStart = new Date(target);
  nextStart.setHours(start.getHours(), start.getMinutes(), 0, 0);
  return {
    start: formatDateTime(nextStart),
    end: formatDateTime(new Date(nextStart.getTime() + duration)),
    assigneeId: activity.assigneeId,
  };
}

function isPastActivity(activity: Activity): boolean {
  return new Date(activity.end).getTime() < Date.now();
}

function ActivityCard({ activity, selectedId, canDrag, onSelect }: {
  activity: Activity;
  selectedId: string | null;
  canDrag: boolean;
  onSelect: (id: string) => void;
}) {
  return (
    <article
      className={`activity-card ${selectedId === activity.id ? 'is-selected' : ''}`}
      draggable={canDrag}
      tabIndex={0}
      onDragStart={(event) => event.dataTransfer.setData('text/activity-id', activity.id)}
      onClick={() => onSelect(activity.id)}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') onSelect(activity.id);
      }}
    >
      <div className="activity-card__time">
        {new Date(activity.start).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
      </div>
      <div><h3>{activity.title}</h3><p>{activity.notes}</p></div>
      <span className="assignee">{activity.assignee}</span>
    </article>
  );
}

export function ActivityCalendar({ user, onLogout }: ActivityCalendarProps) {
  const queryClient = useQueryClient();
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [view, setView] = useState<CalendarView>('Mes');
  const [actionError, setActionError] = useState('');
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [showTracking, setShowTracking] = useState(false);

  const visibleRange = useMemo(() => {
    if (view === 'Mes') {
      const first = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const gridStart = addDays(first, -((first.getDay() + 6) % 7));
      return { from: dateKey(gridStart), to: dateKey(addDays(gridStart, 41)) };
    }
    if (view === 'Día') return { from: dateKey(currentDate), to: dateKey(currentDate) };
    const weekStart = startOfWeek(currentDate);
    return { from: dateKey(weekStart), to: dateKey(addDays(weekStart, 6)) };
  }, [currentDate, view]);

  const { data: activities = [], isLoading, error: queryError } = useQuery({
    queryKey: ['activities', visibleRange.from, visibleRange.to],
    queryFn: () => api.getActivities(visibleRange.from, visibleRange.to),
  });
  const { data: associates = [], error: associatesError } = useQuery({
    queryKey: ['associates'],
    queryFn: api.getAssociates,
    enabled: user.role === 'admin',
  });

  const days = useMemo(() => {
    if (view === 'Día') return [new Date(currentDate)];
    if (view === 'Semana') return Array.from({ length: 7 }, (_, index) => addDays(startOfWeek(currentDate), index));
    const first = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const gridStart = addDays(first, -((first.getDay() + 6) % 7));
    return Array.from({ length: 42 }, (_, index) => addDays(gridStart, index));
  }, [currentDate, view]);

  const selectedActivity = activities.find((activity) => activity.id === selectedId) ?? null;
  const title = view === 'Día'
    ? currentDate.toLocaleDateString('es-ES', { dateStyle: 'full' })
    : currentDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });

  const updateActivity = useMutation<Activity, Error, { id: string; payload: Partial<Activity> }>({
    mutationFn: ({ id, payload }) => api.updateActivity(id, payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['activities'] }),
  });
  const createActivity = useMutation<Activity, Error, Partial<Activity>>({
    mutationFn: (payload) => api.createActivity(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['activities'] });
      setIsModalOpen(false);
    },
  });
  const deleteActivity = useMutation<void, Error, string>({
    mutationFn: (id) => api.deleteActivity(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['activities'] });
      setSelectedId(null);
    },
  });

  const changePeriod = (amount: number) => {
    if (view === 'Mes') setCurrentDate((date) => addMonths(date, amount));
    else setCurrentDate((date) => addDays(date, amount * (view === 'Día' ? 1 : 7)));
  };

  const handleDrop = async (event: DragEvent<HTMLDivElement>, target: Date) => {
    event.preventDefault();
    const activity = activities.find((item) => item.id === event.dataTransfer.getData('text/activity-id'));
    if (!activity || isPastActivity(activity)) return;
    setActionError('');
    const queryKey = ['activities', visibleRange.from, visibleRange.to] as const;
    const previousActivities = queryClient.getQueryData<Activity[]>(queryKey);
    const payload = moveActivityToDay(activity, target);
    queryClient.setQueryData<Activity[]>(queryKey, (current = []) => current.map((item) => (
      item.id === activity.id ? { ...item, ...payload } : item
    )));

    try {
      await updateActivity.mutateAsync({ id: activity.id, payload });
    } catch (error) {
      queryClient.setQueryData(queryKey, previousActivities);
      setActionError(error instanceof Error ? error.message : 'No se pudo reprogramar la actividad.');
    }
  };

  const handleSave = async (payload: Partial<Activity>) => {
    setActionError('');
    try {
      if (selectedActivity) await updateActivity.mutateAsync({ id: selectedActivity.id, payload });
      else await createActivity.mutateAsync(payload);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'No se pudo guardar la actividad.');
      throw error;
    }
  };

  const handleDelete = async () => {
    if (!selectedId || !selectedActivity || isPastActivity(selectedActivity)) return;
    setActionError('');
    try {
      await deleteActivity.mutateAsync(selectedId);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'No se pudo eliminar la actividad.');
    }
  };

  if (showTracking) {
    return <TrackingPage onClose={() => setShowTracking(false)} />;
  }

  return (
    <div className="calendar-shell">
      <header className="topbar">
        <div><p className="eyebrow">Panel principal</p><h1>Actividades</h1></div>
        <div className="topbar-actions"><span className="user-pill">{user.name}</span><button type="button" className="secondary-button" onClick={onLogout}>Salir</button></div>
      </header>
      <div className="calendar-toolbar" aria-label="Acciones del calendario">
        <button type="button" onClick={() => setCurrentDate(new Date())}>Hoy</button>
        <button type="button" onClick={() => changePeriod(-1)}>Anterior</button>
        <button type="button" onClick={() => changePeriod(1)}>Siguiente</button>
        <strong className="calendar-period-title">{title}</strong>
        <div className="calendar-views" aria-label="Vistas del calendario">
          {(['Mes', 'Semana', 'Día', 'Agenda'] as const).map((option) => <button key={option} type="button" className={view === option ? 'active-view' : ''} onClick={() => setView(option)}>{option}</button>)}
        </div>
        {selectedActivity && !isPastActivity(selectedActivity) ? <button type="button" className="secondary-button" onClick={() => setIsModalOpen(true)}>Editar actividad</button> : null}
        <button type="button" className="secondary-button" onClick={() => setShowTracking(true)}>Seguimiento</button>
        {user.role === 'admin' ? <button type="button" className="secondary-button" onClick={() => setShowBulkUpload((current) => !current)}>{showBulkUpload ? 'Ocultar carga' : 'Carga masiva'}</button> : null}
      </div>
      {showBulkUpload && user.role === 'admin' ? <BulkUploadPanel /> : null}
      <section className="calendar-panel">
        <div className="calendar-header-row"><h2>Calendario</h2><span>{activities.length} actividades en el periodo</span></div>
        {isLoading ? <p>Cargando actividades…</p> : null}
        {queryError ? <p className="form-error">{queryError.message}</p> : null}
        {associatesError ? <p className="form-error">No se pudieron cargar los asociados.</p> : null}
        {actionError ? <p className="form-error">{actionError}</p> : null}
        {view === 'Agenda' ? (
          <div className="agenda-list">
            {activities.map((activity) => <ActivityCard key={activity.id} activity={activity} selectedId={selectedId} canDrag={!isPastActivity(activity)} onSelect={setSelectedId} />)}
          </div>
        ) : (
          <div className={`calendar-grid calendar-grid--${view.toLowerCase()}`} aria-label={`Calendario ${view.toLowerCase()}`}>
            {days.map((day) => (
              <div key={dateKey(day)} className={`calendar-day ${view === 'Mes' && day.getMonth() !== currentDate.getMonth() ? 'calendar-day--muted' : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={(event) => void handleDrop(event, day)}>
                <div className="calendar-day__header"><span>{day.toLocaleDateString('es-ES', { weekday: 'short' })}</span><strong>{day.getDate()}</strong></div>
                {activities.filter((activity) => dateKey(parseDate(activity.start.slice(0, 10))) === dateKey(day)).map((activity) => <ActivityCard key={activity.id} activity={activity} selectedId={selectedId} canDrag={!isPastActivity(activity)} onSelect={setSelectedId} />)}
              </div>
            ))}
          </div>
        )}
      </section>
      <button type="button" className="fab fab--add" onClick={() => { setSelectedId(null); setIsModalOpen(true); }} disabled={user.role !== 'admin'} aria-label="Crear actividad">+</button>
      <button type="button" className="fab fab--delete" aria-label="Eliminar actividad seleccionada" onClick={() => void handleDelete()} disabled={!selectedId || !selectedActivity || isPastActivity(selectedActivity)}>🗑️</button>
      <ActivityModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} activity={selectedActivity ?? undefined} associates={associates} onSave={handleSave} />
    </div>
  );
}
