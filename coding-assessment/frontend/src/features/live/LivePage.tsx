import { FormEvent, useEffect, useState } from "react";
import { eventsApi } from "../../api/events";
import { ErrorBanner, EmptyState, PageHeader } from "../../components/common/Ui";
import type { LiveEvent } from "../../types";
import { getLiveSocket } from "./liveSocket";

export function LivePage() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [body, setBody] = useState("");
  const [mongo, setMongo] = useState("unknown");

  useEffect(() => {
    eventsApi
      .list()
      .then((res) => setEvents(res.data ?? []))
      .catch((err: Error) => setError(err.message));

    const socket = getLiveSocket();
    socket.emit("events:subscribe");
    socket.on("mongo:status", (payload: { driver?: boolean; tcp?: string }) => {
      setMongo(payload.driver ? "driver up" : `driver down (${payload.tcp ?? ""})`);
    });
    socket.on("event:created", (doc: LiveEvent) => {
      setEvents((prev) => [doc, ...prev]);
    });
    return () => {
      socket.off("mongo:status");
      socket.off("event:created");
    };
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await eventsApi.create(body);
      setBody("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    }
  }

  return (
    <div className="stack">
      <PageHeader title="Live events" />
      <p className="muted">Mongo: {mongo}. REST + sockets are stubbed until the connection layer is finished.</p>
      <ErrorBanner message={error} />
      <form className="toolbar" onSubmit={onSubmit}>
        <input className="input" placeholder="Event text" value={body} onChange={(e) => setBody(e.target.value)} />
        <button className="btn primary" type="submit">
          Post
        </button>
      </form>
      <div className="card table-wrap">
        {events.length === 0 ? (
          <EmptyState title="No events" hint="Mongo must be connected for this list to load." />
        ) : (
          <table className="data">
            <thead>
              <tr>
                <th>When</th>
                <th>Body</th>
              </tr>
            </thead>
            <tbody>
              {events.map((row) => (
                <tr key={row._id}>
                  <td>{row.createdAt}</td>
                  <td>{row.body}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
