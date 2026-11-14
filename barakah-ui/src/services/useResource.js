import { useEffect, useState } from 'react';

// A request changing filters cannot overwrite a newer request's result.
export function useResource(loader, ...args) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const key = JSON.stringify(args);
  useEffect(() => {
    let current = true;
    setState({ data: null, loading: true, error: null });
    loader(...JSON.parse(key)).then(
      data => current && setState({ data, loading: false, error: null }),
      error => current && setState({ data: null, loading: false, error: error.message }),
    );
    return () => { current = false; };
  }, [loader, key, attempt]);
  return { ...state, retry: () => setAttempt(value => value + 1) };
}
