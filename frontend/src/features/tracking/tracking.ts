export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface Place {
  label: string;
  point: GeoPoint;
}

export interface Route {
  geometry: GeoPoint[];
  distanceMeters: number;
  durationSeconds: number;
}

export interface Geocoder {
  search(query: string, signal?: AbortSignal): Promise<Place>;
}

export interface Router {
  route(origin: GeoPoint, destination: GeoPoint, signal?: AbortSignal): Promise<Route>;
}

export interface LocationSource {
  watch(onLocation: (sample: LocationSample) => void, onError: (error: GeolocationPositionError) => void): () => void;
}

export interface LocationSample {
  point: GeoPoint;
  accuracyMeters?: number;
  timestamp: number;
}

const GEOCODER_URL = import.meta.env.VITE_GEOCODER_URL ?? 'https://nominatim.openstreetmap.org/search';
const ROUTER_URL = import.meta.env.VITE_ROUTER_URL ?? 'https://router.project-osrm.org/route/v1/driving';

export const nominatimGeocoder: Geocoder = {
  async search(query, signal) {
    const params = new URLSearchParams({ format: 'jsonv2', limit: '1', q: query });
    const response = await fetch(`${GEOCODER_URL}?${params}`, { signal });
    if (!response.ok) throw new Error('No se pudo consultar el buscador de lugares.');
    const results = await response.json() as Array<{ display_name: string; lat: string; lon: string }>;
    const first = results[0];
    if (!first) throw new Error(`No se encontró el lugar «${query}».`);
    return { label: first.display_name, point: { lat: Number(first.lat), lng: Number(first.lon) } };
  },
};

export const osrmRouter: Router = {
  async route(origin, destination, signal) {
    const coordinates = `${origin.lng},${origin.lat};${destination.lng},${destination.lat}`;
    const response = await fetch(`${ROUTER_URL}/${coordinates}?overview=full&geometries=geojson`, { signal });
    if (!response.ok) throw new Error('No se pudo calcular la ruta.');
    const body = await response.json() as { code: string; routes?: Array<{ distance: number; duration: number; geometry: { coordinates: Array<[number, number]> } }> };
    const first = body.routes?.[0];
    if (body.code !== 'Ok' || !first) throw new Error('No se encontró una ruta entre esos lugares.');
    return {
      geometry: first.geometry.coordinates.map(([lng, lat]) => ({ lat, lng })),
      distanceMeters: first.distance,
      durationSeconds: first.duration,
    };
  },
};

export const browserLocationSource: LocationSource = {
  watch(onLocation, onError) {
    if (!navigator.geolocation) {
      onError({ code: 0, message: 'Este navegador no admite geolocalización.' } as GeolocationPositionError);
      return () => undefined;
    }
    const id = navigator.geolocation.watchPosition(
      (position) => onLocation({
        point: { lat: position.coords.latitude, lng: position.coords.longitude },
        accuracyMeters: position.coords.accuracy,
        timestamp: position.timestamp,
      }),
      onError,
      { enableHighAccuracy: true, maximumAge: 10_000, timeout: 15_000 },
    );
    return () => navigator.geolocation.clearWatch(id);
  },
};

export function distanceBetween(a: GeoPoint, b: GeoPoint): number {
  const earthRadius = 6_371_000;
  const lat1 = a.lat * Math.PI / 180;
  const lat2 = b.lat * Math.PI / 180;
  const deltaLat = (b.lat - a.lat) * Math.PI / 180;
  const deltaLng = (b.lng - a.lng) * Math.PI / 180;
  const value = Math.sin(deltaLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLng / 2) ** 2;
  return earthRadius * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
}

export function bearingBetween(a: GeoPoint, b: GeoPoint): number {
  const lat1 = a.lat * Math.PI / 180;
  const lat2 = b.lat * Math.PI / 180;
  const deltaLng = (b.lng - a.lng) * Math.PI / 180;
  return (Math.atan2(Math.sin(deltaLng) * Math.cos(lat2), Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(deltaLng)) * 180 / Math.PI + 360) % 360;
}
