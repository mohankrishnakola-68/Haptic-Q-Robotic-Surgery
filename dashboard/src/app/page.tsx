"use client";

import React, { useEffect, useState, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { Shield, Activity, Lock, AlertTriangle, Zap, User } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<any[]>([]);
  const [currentStatus, setCurrentStatus] = useState({
    integrity: 100,
    force: 0,
    lockout: false,
    online: false
  });

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    connectWS();
    return () => ws.current?.close();
  }, []);

  const connectWS = () => {
    ws.current = new WebSocket('ws://127.0.0.1:5556');

    ws.current.onopen = () => {
      setCurrentStatus(prev => ({ ...prev, online: true }));
    };

    ws.current.onmessage = (event) => {
      try {
        const packet = JSON.parse(event.data);
        if (packet.type === 'telemetry') {
          const telemetry = packet.data;

          setCurrentStatus({
            integrity: telemetry.integrity,
            force: telemetry.force,
            lockout: telemetry.lockout,
            online: true
          });

          setData(prev => {
            const newData = [...prev, {
              time: new Date().toLocaleTimeString(),
              integrity: telemetry.integrity,
              force: telemetry.force
            }].slice(-20);
            return newData;
          });
        }
      } catch (err) {
        console.error("WS Parse Error", err);
      }
    };

    ws.current.onclose = () => {
      setCurrentStatus(prev => ({ ...prev, online: false }));
      setTimeout(connectWS, 3000);
    };
  };

  const isAlert = currentStatus.lockout || currentStatus.integrity < 50;

  return (
    <main className={`dashboard-container ${isAlert ? 'alert-mode' : ''}`}>
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div className={`status-indicator ${currentStatus.online ? 'status-online' : 'status-offline'}`} />
          <h1>HAPTIC-Q <span style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 300, opacity: 0.6 }}>| SURGICAL SYSTEMS ARCHITECT</span></h1>
        </div>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.7rem', color: '#8899a6' }}>SECURE SESSION ID</div>
            <div style={{ fontSize: '0.9rem', color: '#00f5ff' }}>QS-7742-XP-03</div>
          </div>
          <User size={32} color="#008b8b" style={{ border: '1px solid #004d4d', borderRadius: '50%', padding: '5px' }} />
        </div>
      </header>

      <div className="main-content">
        {/* Force Feedback Chart */}
        <section className="card" style={{ gridColumn: '1 / 2', gridRow: '1 / 3' }}>
          <div className="card-title">
            <Activity size={16} /> Force Feedback Telemetry (N)
          </div>
          <div style={{ width: '100%', height: '80%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorForce" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ced1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00ced1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" hide />
                <YAxis stroke="#475569" domain={[0, 1024]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#131922', border: '1px solid #1e293b' }}
                  itemStyle={{ color: '#00f5ff' }}
                />
                <Area type="monotone" dataKey="force" stroke="#00ced1" fillOpacity={1} fill="url(#colorForce)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div style={{ position: 'absolute', bottom: 20, right: 20, textAlign: 'right' }}>
            <div style={{ fontSize: '0.8rem', color: '#8899a6' }}>Real-time Delay</div>
            <div style={{ fontSize: '1.2rem', color: '#00ff88' }}>42ms</div>
          </div>
        </section>

        {/* Security / Integrity Display */}
        <section className="card">
          <div className="card-title">
            <Shield size={16} /> Quantum Link Integrity
          </div>
          <div className="value-display" style={{ color: currentStatus.integrity < 80 ? '#ffcc00' : '#00f5ff' }}>
            {currentStatus.integrity}%
          </div>
          <div style={{ width: '100%', height: '50px' }}>
            <div style={{ background: '#1e293b', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                background: currentStatus.integrity < 80 ? '#ffcc00' : '#00ced1',
                width: `${currentStatus.integrity}%`,
                height: '100%',
                transition: 'width 0.5s ease'
              }} />
            </div>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#8899a6', marginTop: '10px' }}>
            Algorithm: E91 Entanglement-based QSDC
          </div>
        </section>

        {/* System Status / Lockout */}
        <section className={`card ${currentStatus.lockout ? 'alert-mode' : ''}`}>
          <div className="card-title">
            <Lock size={16} /> Robot Control Status
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            {currentStatus.lockout ? (
              <>
                <AlertTriangle size={48} color="#ff3e3e" />
                <div>
                  <div style={{ fontSize: '1.2rem', color: '#ff3e3e', fontWeight: 600 }}>LOCKOUT ACTIVE</div>
                  <div style={{ fontSize: '0.8rem', color: '#8899a6' }}>Interception Detected. Robot motors disabled.</div>
                </div>
              </>
            ) : (
              <>
                <Zap size={48} color="#00ff88" />
                <div>
                  <div style={{ fontSize: '1.2rem', color: '#00ff88', fontWeight: 600 }}>ARM ACTIVE</div>
                  <div style={{ fontSize: '0.8rem', color: '#8899a6' }}>Secure link established. Control active.</div>
                </div>
              </>
            )}
          </div>
          {currentStatus.lockout && (
            <button style={{
              marginTop: '15px',
              padding: '8px 16px',
              background: 'transparent',
              border: '1px solid #ff3e3e',
              color: '#ff3e3e',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }}>
              OVERRIDE SECURITY (REQUIRES MD KEY)
            </button>
          )}
        </section>
      </div>

      <footer style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', opacity: 0.4, fontSize: '0.7rem' }}>
        <div>HAPTIC-Q v1.0.4 - RUNNING IN SIMULATION MODE</div>
        <div>C-ENC: RSA-4096 | Q-ENC: BB84/E91 HYBRID</div>
      </footer>
    </main>
  );
}
