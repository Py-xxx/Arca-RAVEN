import { useEffect } from "react";
import { useRoverStore } from "../store/roverStore";

/**
 * Auto-connects to the bridge server on mount.
 * Cleans up on unmount.
 */
export function useAutoConnect() {
  const connect = useRoverStore((s) => s.connect);
  const disconnect = useRoverStore((s) => s.disconnect);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, []);
}
