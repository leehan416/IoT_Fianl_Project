import { useEffect, useMemo, useState } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';

type RunnerLocation = {
  runner_id: string;
  latitude: number;
  longitude: number;
  pace: number | null;
  battery: number | null;
  status: string;
  received_at: string;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const defaultCenter: [number, number] = [36.10321, 129.38712];

const runnerIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function RecenterMap({
  runners,
  selectedRunner,
}: {
  runners: RunnerLocation[];
  selectedRunner: RunnerLocation | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (selectedRunner) {
      map.flyTo([selectedRunner.latitude, selectedRunner.longitude], 17, {
        duration: 0.6,
      });
      return;
    }

    if (runners.length === 0) return;

    const bounds = L.latLngBounds(
      runners.map((runner) => [runner.latitude, runner.longitude]),
    );
    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 16 });
  }, [map, runners, selectedRunner]);

  return null;
}

export function App() {
  const [runners, setRunners] = useState<RunnerLocation[]>([]);
  const [selectedRunnerId, setSelectedRunnerId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadRunners() {
    try {
      const response = await fetch(`${apiBaseUrl}/runners`);
      if (!response.ok) {
        throw new Error(`GET /runners failed: ${response.status}`);
      }
      const data = (await response.json()) as RunnerLocation[];
      setRunners(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRunners();
    const timer = window.setInterval(loadRunners, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const center = useMemo<[number, number]>(() => {
    if (runners.length === 0) return defaultCenter;
    return [runners[0].latitude, runners[0].longitude];
  }, [runners]);

  const selectedRunner = useMemo(() => {
    if (!selectedRunnerId) return null;
    return runners.find((runner) => runner.runner_id === selectedRunnerId) ?? null;
  }, [runners, selectedRunnerId]);

  return (
    <main className="app-shell">
      <section className="map-area" aria-label="Runner location map">
        <MapContainer center={center} zoom={15} className="runner-map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <RecenterMap runners={runners} selectedRunner={selectedRunner} />
          {runners.map((runner) => (
            <Marker
              key={runner.runner_id}
              position={[runner.latitude, runner.longitude]}
              icon={runnerIcon}
            >
              <Popup>
                <strong>Runner {runner.runner_id}</strong>
                <dl className="runner-popup">
                  <dt>Pace</dt>
                  <dd>{runner.pace ?? '-'} </dd>
                  <dt>Battery</dt>
                  <dd>{runner.battery ?? '-'}%</dd>
                  <dt>Status</dt>
                  <dd>{runner.status}</dd>
                  <dt>Received</dt>
                  <dd>{runner.received_at || '-'}</dd>
                </dl>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </section>

      <aside className="status-panel">
        <div>
          <p className="eyebrow">Live tracking</p>
          <h1>Runner Map</h1>
        </div>
        <button type="button" onClick={loadRunners}>
          Refresh
        </button>
        <p className="summary">
          {loading ? 'Loading runners...' : `${runners.length} runners tracked`}
        </p>
        {error && <p className="error">{error}</p>}
        <ul className="runner-list">
          {runners.map((runner) => (
            <li key={runner.runner_id}>
              <button
                type="button"
                className={
                  runner.runner_id === selectedRunnerId
                    ? 'runner-row is-selected'
                    : 'runner-row'
                }
                onClick={() => setSelectedRunnerId(runner.runner_id)}
              >
              <span>#{runner.runner_id}</span>
              <span>{runner.battery ?? '-'}%</span>
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </main>
  );
}
