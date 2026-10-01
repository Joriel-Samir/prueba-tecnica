import 'leaflet/dist/leaflet.css';
import { MapContainer, Marker, Polyline, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { bearingBetween, browserLocationSource, distanceBetween, nominatimGeocoder, osrmRouter, type GeoPoint, type LocationSample, type Place, type Route } from './tracking';

const DEFAULT_CENTER: [number, number] = [4.711, -74.0721];

function markerIcon(label: string, color: string) {
  return L.divIcon({ className: 'tracking-marker-wrapper', html: `<span class="tracking-marker" style="background:${color}">${label}</span>`, iconSize: [32, 32], iconAnchor: [16, 16] });
}

function RouteBounds({ route }: { route: Route | null }) {
  const map = useMap();
  useEffect(() => {
    if (route?.geometry.length) {
      map.fitBounds(route.geometry.map((point) => [point.lat, point.lng] as [number, number]), { padding: [24, 24] });
    }
  }, [map, route]);
  return null;
}

function formatDistance(meters: number): string {
  return meters >= 1000 ? `${(meters / 1000).toFixed(1)} km` : `${Math.round(meters)} m`;
}

function formatEta(seconds: number): string {
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min`;
}

function routeDistanceFrom(route: Route, index: number): number {
  return route.geometry.slice(index).reduce((total, point, position, points) => {
    const next = points[position + 1];
    return total + (next ? distanceBetween(point, next) : 0);
  }, 0);
}

export function TrackingPage({ onClose }: { onClose: () => void }) {
  const [originQuery, setOriginQuery] = useState('Bogotá, Colombia');
  const [destinationQuery, setDestinationQuery] = useState('Chapinero, Bogotá, Colombia');
  const [origin, setOrigin] = useState<Place | null>(null);
  const [destination, setDestination] = useState<Place | null>(null);
  const [route, setRoute] = useState<Route | null>(null);
  const [demoIndex, setDemoIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [liveSample, setLiveSample] = useState<LocationSample | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [liveSpeed, setLiveSpeed] = useState(0);
  const [locationError, setLocationError] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);
  const previousLiveSampleRef = useRef<LocationSample | null>(null);

  const currentPoint = isLive ? liveSample?.point ?? null : route?.geometry[demoIndex] ?? null;
  const remainingDistance = route && currentPoint
    ? isLive && destination ? distanceBetween(currentPoint, destination.point) : routeDistanceFrom(route, demoIndex)
    : 0;
  const demoSpeed = route ? route.distanceMeters / Math.max(route.durationSeconds, 1) : 0;
  const speed = isLive ? liveSpeed : demoSpeed;
  const bearing = currentPoint && route && route.geometry[demoIndex + 1]
    ? bearingBetween(currentPoint, route.geometry[demoIndex + 1])
    : 0;

  useEffect(() => {
    if (!isPlaying || !route || isLive) return undefined;
    const timer = window.setInterval(() => {
      setDemoIndex((index) => {
        if (index >= route.geometry.length - 1) {
          setIsPlaying(false);
          return index;
        }
        return index + 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [isLive, isPlaying, route]);

  useEffect(() => {
    if (!isLive) {
      previousLiveSampleRef.current = null;
      setLiveSpeed(0);
      return undefined;
    }
    const stop = browserLocationSource.watch(
      (sample) => {
        const previous = previousLiveSampleRef.current;
        if (previous) {
          setLiveSpeed(distanceBetween(previous.point, sample.point) / Math.max((sample.timestamp - previous.timestamp) / 1000, 1));
        }
        previousLiveSampleRef.current = sample;
        setLiveSample(sample);
        setLocationError('');
      },
      (geoError) => { setLocationError(geoError.message); setIsLive(false); },
    );
    return stop;
  }, [isLive]);

  const handleRoute = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setIsLoading(true);
    setError('');
    setRoute(null);
    setDemoIndex(0);
    setIsPlaying(false);
    try {
      const [nextOrigin, nextDestination] = await Promise.all([
        nominatimGeocoder.search(originQuery, controller.signal),
        nominatimGeocoder.search(destinationQuery, controller.signal),
      ]);
      const nextRoute = await osrmRouter.route(nextOrigin.point, nextDestination.point, controller.signal);
      setOrigin(nextOrigin);
      setDestination(nextDestination);
      setRoute(nextRoute);
    } catch (routeError) {
      if ((routeError as Error).name !== 'AbortError') setError(routeError instanceof Error ? routeError.message : 'No se pudo preparar el seguimiento.');
    } finally {
      setIsLoading(false);
    }
  };

  const center = useMemo<[number, number]>(() => {
    const point: GeoPoint = currentPoint ?? origin?.point ?? { lat: DEFAULT_CENTER[0], lng: DEFAULT_CENTER[1] };
    return [point.lat, point.lng];
  }, [currentPoint, origin]);

  return (
    <section className="tracking-shell" aria-label="Seguimiento geoespacial">
      <header className="tracking-header"><div><p className="eyebrow">Frontend 2</p><h1>Seguimiento de entrega</h1></div><button type="button" className="secondary-button" onClick={onClose}>Volver</button></header>
      <form className="tracking-form" onSubmit={handleRoute}>
        <label htmlFor="tracking-origin">Origen</label>
        <input id="tracking-origin" value={originQuery} onChange={(event) => setOriginQuery(event.target.value)} required />
        <label htmlFor="tracking-destination">Destino</label>
        <input id="tracking-destination" value={destinationQuery} onChange={(event) => setDestinationQuery(event.target.value)} required />
        <button type="submit" disabled={isLoading}>{isLoading ? 'Calculando ruta…' : 'Calcular ruta real'}</button>
      </form>
      {error ? <p className="form-error">{error}</p> : null}
      {locationError ? <p className="form-error">Ubicación: {locationError}</p> : null}
      <div className="tracking-map-wrap">
        <MapContainer center={center} zoom={12} className="tracking-map" scrollWheelZoom>
          <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {route ? <Polyline positions={route.geometry.map((point) => [point.lat, point.lng] as [number, number])} pathOptions={{ color: '#2563eb', weight: 5 }} /> : null}
          {origin ? <Marker position={[origin.point.lat, origin.point.lng]} icon={markerIcon('A', '#16a34a')} /> : null}
          {destination ? <Marker position={[destination.point.lat, destination.point.lng]} icon={markerIcon('B', '#dc2626')} /> : null}
          {currentPoint ? <Marker position={[currentPoint.lat, currentPoint.lng]} icon={markerIcon(`<span style="display:block;transform:rotate(${bearing}deg)">➤</span>`, '#f59e0b')} /> : null}
          <RouteBounds route={route} />
        </MapContainer>
      </div>
      <div className="tracking-controls">
        <button type="button" onClick={() => { setIsLive(false); setDemoIndex(0); setIsPlaying(false); }} disabled={!route}>Reiniciar demo</button>
        <button type="button" onClick={() => { setIsLive(false); setIsPlaying((playing) => !playing); }} disabled={!route}>{isPlaying ? 'Pausar' : 'Reproducir demo'}</button>
        <button type="button" onClick={() => { setIsPlaying(false); setIsLive((live) => !live); }} disabled={!route}>{isLive ? 'Detener ubicación' : 'Usar ubicación real'}</button>
      </div>
      <div className="tracking-metrics" aria-live="polite">
        <div><span>Distancia restante</span><strong>{formatDistance(remainingDistance)}</strong></div>
        <div><span>Velocidad estimada</span><strong>{speed > 0 ? `${(speed * 3.6).toFixed(1)} km/h` : 'Calculando'}</strong></div>
        <div><span>ETA</span><strong>{route ? formatEta(remainingDistance / Math.max(speed || demoSpeed, 1)) : '—'}</strong></div>
        <div><span>Precisión / última señal</span><strong>{isLive && liveSample ? `${Math.round(liveSample.accuracyMeters ?? 0)} m / ${new Date(liveSample.timestamp).toLocaleTimeString('es-ES')}` : 'Ruta activa'}</strong></div>
        <div><span>Fuente</span><strong>{isLive ? 'GPS en vivo' : route ? 'Demo sobre ruta real' : 'Sin ruta'}</strong></div>
      </div>
    </section>
  );
}
