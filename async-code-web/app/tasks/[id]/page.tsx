"use client";

"use client";

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Github, Clock, CheckCircle, XCircle, AlertCircle, GitCommit, FileText, ExternalLink, MessageSquare, Plus, Copy, Loader2, Terminal } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ProtectedRoute } from "@/components/protected-route";
import { useAuth } from "@/contexts/auth-context";
import { ApiService } from "@/lib/api-service";
import { websocketService, TaskLogMessage } from "@/lib/websocket-service";
import { Task, Project, ChatMessage } from "@/types";
import { formatDiff, parseDiffStats } from "@/lib/utils";
import { DiffViewer } from "@/components/diff-viewer";
    const [newMessage, setNewMessage] = useState("");
    const [githubToken, setGithubToken] = useState("");
    const [creatingPR, setCreatingPR] = useState(false);
    const [taskLogs, setTaskLogs] = useState<string[]>([]);
    const [showLogs, setShowLogs] = useState(false);
    const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (typeof window !== 'undefined') {
        }
    }, []);

    // WebSocket connection and log streaming
    useEffect(() => {
        if (!task || task.status !== 'running') {
            return;
        }

        let mounted = true;

        const connectAndSubscribe = async () => {
            try {
                const wsUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
                await websocketService.connect(wsUrl);

                if (!mounted) return;

                setIsWebSocketConnected(true);

                // Subscribe to task logs
                websocketService.subscribeToTask(taskId, (logMessage: TaskLogMessage) => {
                    if (!mounted) return;

                    setTaskLogs(prev => [...prev, logMessage.log]);
                });

                toast.success('Connected to real-time log stream');

            } catch (error) {
                console.error('Failed to connect to WebSocket:', error);
                toast.error('Failed to connect to real-time updates');
            }
        };

        connectAndSubscribe();

        return () => {
            mounted = false;
            websocketService.unsubscribeFromTask(taskId);
            setIsWebSocketConnected(false);
        };
    }, [task, taskId]);

    // Auto-scroll logs to bottom
    useEffect(() => {
        if (showLogs && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [taskLogs, showLogs]);

    // Clear logs when task completes
    useEffect(() => {
        if (task && task.status !== 'running' && taskLogs.length > 0) {
            // Optionally keep logs or clear them
            // setTaskLogs([]);
        }
    }, [task?.status, taskLogs.length]);

    useEffect(() => {
        if (user?.id && taskId) {
            loadTask();
                                    <CardTitle>Task Information</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {/* Show logs button for completed tasks */}
                                    {task.status !== 'running' && taskLogs.length > 0 && (
                                        <div className="mb-4">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setShowLogs(!showLogs)}
                                                className="gap-2"
                                            >
                                                <Terminal className="w-4 h-4" />
                                                {showLogs ? 'Hide' : 'Show'} Execution Logs
                                            </Button>
                                        </div>
                                    )}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label className="text-sm font-medium text-slate-500">Repository</Label>
                                    )}

                                    {task.status === "running" && (
                                        <>
                                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="animate-spin">
                                                        <AlertCircle className="w-5 h-5 text-blue-600" />
                                                    </div>
                                                    <div>
                                                        <div className="font-medium text-blue-900">AI is working on your code...</div>
                                                        <div className="text-sm text-blue-700 mt-1">
                                                            This may take a few minutes. You can safely close this page.
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="mt-3 bg-blue-100 rounded-full h-2">
                                                    <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
                                                </div>
                                            </div>

                                            {/* Real-time logs section */}
                                            <div className="mt-4">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <Terminal className="w-4 h-4" />
                                                        <h3 className="font-medium text-sm">Execution Logs</h3>
                                                        {isWebSocketConnected && (
                                                            <Badge variant="outline" className="text-xs">
                                                                <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
                                                                Live
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => setShowLogs(!showLogs)}
                                                    >
                                                        {showLogs ? 'Hide' : 'Show'} Logs
                                                    </Button>
                                                </div>

                                                {showLogs && (
                                                    <div className="bg-slate-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                                                        <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                                                            {taskLogs.length > 0 ? (
                                                                taskLogs.map((log, index) => (
                                                                    <div key={index} className="hover:bg-slate-800 px-1 py-0.5">
                                                                        {log}
                                                                    </div>
                                                                ))
                                                            ) : (
                                                                <div className="text-slate-500">
                                                                    {isWebSocketConnected
                                                                        ? 'Waiting for logs...'
                                                                        : 'Connecting to log stream...'}
                                                                </div>
                                                            )}
                                                            <div ref={logsEndRef} />
                                                        </pre>
                                                    </div>
                                                )}
                                            </div>
                                        </>
                                    )}

                                    {/* Show logs for completed/failed tasks */}
                                    {task.status !== "running" && taskLogs.length > 0 && showLogs && (
                                        <div className="mt-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center gap-2">
                                                    <Terminal className="w-4 h-4" />
                                                    <h3 className="font-medium text-sm">Execution Logs</h3>
                                                    <Badge variant={task.status === "completed" ? "default" : "destructive"} className="text-xs">
                                                        {task.status}
                                                    </Badge>
                                                </div>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => setShowLogs(false)}
                                                >
                                                    Hide Logs
                                                </Button>
                                            </div>
                                            <div className="bg-slate-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                                                <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                                                    {taskLogs.map((log, index) => (
                                                        <div key={index} className="hover:bg-slate-800 px-1 py-0.5">
                                                            {log}
                                                        </div>
                                                    ))}
                                                </pre>
                                            </div>
                                        </div>
                                    )}