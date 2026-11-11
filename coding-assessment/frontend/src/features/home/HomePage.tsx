import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="stack">
      <div className="card card-pad">
        <h2 style={{ marginTop: 0 }}>Starter workspace</h2>
        <p className="muted">Choose one task from task.md. This app only provides the base structure.</p>
      </div>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <Link to="/login" className="card card-pad">
          <div className="label">Task 1</div>
          <p style={{ margin: "8px 0 0" }}>Authentication workflow — start in features/auth. Current login is a conventional form.</p>
        </Link>
        <Link to="/live" className="card card-pad">
          <div className="label">Task 2</div>
          <p style={{ margin: "8px 0 0" }}>MongoDB, REST, and sockets — start in features/live and server/app/db/mongo.py.</p>
        </Link>
      </div>
    </div>
  );
}
