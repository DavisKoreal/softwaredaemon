import { useState, useEffect, useRef, useCallback } from 'react';

// Define the type of message data the UI receives
export interface ReceivedData {
    // These are the properties causing the error (added back)
    timestamp?: string; 
    message?: string;
    
    // Original properties
    level?: 'info' | 'error' | 'warning' | 'success';
    response?: string;
    task?: string;
    error?: string;
}

// The Hook
export const useWebSocket = (url: string) => {
    const wsRef = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    // State to hold the most recent logs/messages received
    const [latestMessage, setLatestMessage] = useState<ReceivedData | null>(null);

    useEffect(() => {
        let ws: WebSocket;
        
        try {
            ws = new WebSocket(url);

            ws.onopen = () => {
                console.log('WebSocket: Connection opened.');
                wsRef.current = ws; 
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as ReceivedData;
                    setLatestMessage(data);
                } catch (error) {
                    console.error('WebSocket Error: Failed to parse message.', error, event.data);
                    // Sending a structured error message to the UI via the state
                    setLatestMessage({ 
                        level: 'error', 
                        message: 'Failed to parse incoming data.', 
                        timestamp: new Date().toISOString() 
                    });
                }
            };

            ws.onerror = (e) => {
                console.error('WebSocket Error:', e);
            };
            
            ws.onclose = () => {
                console.log('WebSocket: Connection closed.');
                if (wsRef.current === ws) {
                    wsRef.current = null;
                    setIsConnected(false);
                }
            };

        } catch (e) {
            console.error("Failed to create WebSocket instance:", e);
            return; 
        }

        return () => {
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                ws.close(1000, "Component unmounted/Strict Mode Cleanup");
            }
        };
    }, [url]);

    const sendMessage = useCallback((message: any) => {
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
            return true;
        } else {
            console.error("WebSocket is not connected. Cannot send message.");
            return false;
        }
    }, []);

    return { isConnected, latestMessage, sendMessage };
};