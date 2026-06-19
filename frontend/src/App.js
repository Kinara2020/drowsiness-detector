import { useState, useEffect } from "react";

function App() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch("http://localhost:5000/alerts");
      const data = await res.json();
      setAlerts(data);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center p-6 gap-6">
      <h1 className="text-3xl font-bold text-yellow-400">🚗 Driver Drowsiness Monitor</h1>

      <img
        src="http://localhost:5000/video_feed"
        alt="Live Feed"
        className="rounded-xl border-4 border-yellow-400 w-[640px] shadow-xl"
      />

      <div className="w-full max-w-2xl">
        <h2 className="text-xl font-semibold mb-3 text-gray-300">Alert Log</h2>
        <div className="flex flex-col gap-2 max-h-72 overflow-y-auto">
          {alerts.length === 0 && (
            <p className="text-gray-500">No alerts yet — drive safe!</p>
          )}
          {alerts.map((a, i) => (
            <div
              key={i}
              className={`flex justify-between rounded-lg px-4 py-2 text-sm font-medium
                ${a.type === "DROWSY" ? "bg-red-800" : "bg-orange-700"}`}
            >
              <span>{a.type === "DROWSY" ? "😴 Drowsiness" : "🥱 Yawn"}</span>
              <span>EAR: {a.ear} | MAR: {a.mar}</span>
              <span className="text-gray-300">{new Date(a.timestamp).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;