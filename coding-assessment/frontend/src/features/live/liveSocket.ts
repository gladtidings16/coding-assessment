import { io, type Socket } from "socket.io-client";

let socket: Socket | null = null;

/** Basic client. Task 2: reconnect and keep Mongo-backed events in sync. */
export function getLiveSocket() {
  if (!socket) {
    socket = io({
      path: "/socket.io",
      transports: ["websocket"],
      reconnection: false,
      timeout: 2500,
    });
  }
  return socket;
}
