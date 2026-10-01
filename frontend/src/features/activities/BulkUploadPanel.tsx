import { FormEvent, useState } from 'react';
import * as XLSX from 'xlsx';
import { api } from '../../lib/api';
import type { BulkUploadResult } from '../../types';

export function BulkUploadPanel() {
  const [resource, setResource] = useState<'associates' | 'activities'>('associates');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BulkUploadResult | null>(null);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [preview, setPreview] = useState<string[][]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const handleFileChange = async (selectedFile: File | null) => {
    setFile(selectedFile);
    setResult(null);
    setError('');
    setPreview([]);
    if (!selectedFile) return;
    setIsPreviewLoading(true);
    try {
      const workbook = XLSX.read(await selectedFile.arrayBuffer(), { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<unknown[]>(firstSheet, { header: 1, defval: '' });
      setPreview(rows.slice(0, 6).map((row) => row.map((cell) => String(cell))));
    } catch {
      setError('No se pudo leer la vista previa del archivo.');
    } finally {
      setIsPreviewLoading(false);
    }
  };

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
        <input id="associates-file" type="file" accept=".csv,.xlsx" onChange={(event) => { void handleFileChange(event.target.files?.[0] ?? null); }} />
        {isPreviewLoading ? <p>Cargando vista previa…</p> : null}
        {preview.length ? (
          <div className="bulk-preview" aria-label="Vista previa del archivo">
            <strong>Vista previa</strong>
            <table><tbody>{preview.map((row, rowIndex) => <tr key={`preview-${rowIndex}`}>{row.map((cell, cellIndex) => rowIndex === 0 ? <th key={`cell-${cellIndex}`}>{cell}</th> : <td key={`cell-${cellIndex}`}>{cell}</td>)}</tr>)}</tbody></table>
          </div>
        ) : null}
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
