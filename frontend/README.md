# Marathon Runner Map

React + Leaflet client for displaying runner locations from the FastAPI server with OpenStreetMap tiles.

## Run

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:3000`.

The app polls:

```text
GET http://localhost:8000/runners
```
