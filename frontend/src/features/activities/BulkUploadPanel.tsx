import { FormEvent, useState } from 'react';
import { api } from '../../lib/api';
import type { BulkUploadResult } from '../../types';

export function BulkUploadPanel() {
  const [resource, setResource] = useState<'associates' | 'activities'>('associates');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BulkUploadResult | null>(null);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError('Selecciona un archivo CSV o XLSX.');
      return;
    }
    setError('');
    setResult(null);
    setIsSubmitting(true);
    try {
      setResult(resource === 'associates' ? await api.uploadAssociates(file) : await api.uploadActivities(file));
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'No se pudo procesar el archivo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="bulk-panel" aria-label="Carga masiva de asociados">
      <div>
        <p className="eyebrow">Administración</p>
        <h2>Carga masiva</h2>
        <p>Importa asociados o actividades y revisa los errores por fila.</p>
      </div>
      <form className="bulk-form" onSubmit={handleSubmit}>
        <label htmlFor="bulk-resource">Tipo de carga</label>
        <select id="bulk-resource" value={resource} onChange={(event) => { setResource(event.target.value as 'associates' | 'activities'); setFile(null); setResult(null); }}>
          <option value="associates">Asociados</option>
          <option value="activities">Actividades</option>
        </select>
        <label htmlFor="associates-file">Archivo CSV o XLSX</label>
        <input id="associates-file" type="file" accept=".csv,.xlsx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Procesando…' : 'Importar archivo'}</button>
      </form>
      {result ? (
        <div className="bulk-result" aria-live="polite">
          <strong>{result.created} de {result.total} filas creadas</strong>
          {result.errors.length ? (
            <ul>
              {result.errors.map((item, index) => <li key={`${item.row ?? 'row'}-${index}`}>Fila {item.row ?? 'desconocida'}: {item.error ?? 'Error de validación'}</li>)}
            </ul>
          ) : <p>El archivo se procesó sin errores.</p>}
        </div>
      ) : null}
    </section>
  );
}
