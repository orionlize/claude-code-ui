"use client";

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Activity, ExternalLink, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ProtectedRoute } from "@/components/protected-route";
import { useAuth } from "@/contexts/auth-context";
import { ApiService } from "@/lib/api-service";
import { Project } from "@/types";

export default function ProjectDetailPage() {
    const { user } = useAuth();
    const params = useParams();
    const projectId = parseInt(params.id as string);
    
    const [project, setProject] = useState<Project | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user?.id && projectId) {
            loadProject();
        }
    }, [user?.id, projectId]);

    const loadProject = async () => {
        if (!user?.id) return;
        
        try {
            setLoading(true);
            const projectData = await ApiService.getProject(user.id, projectId);
            setProject(projectData);
        } catch (error) {
            console.error("Error loading project:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900 mx-auto"></div>
                        <p className="text-slate-600 mt-2">Loading project...</p>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (!project) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
                    <div className="text-center">
                        <p className="text-slate-600">Project not found</p>
                        <Link to="/projects">
                            <Button className="mt-4">Back to Projects</Button>
                        </Link>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
                <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
                    <div className="container mx-auto px-6 py-4">
                        <div className="flex items-center gap-4">
                            <Link to="/projects" className="text-slate-600 hover:text-slate-900 flex items-center gap-2">
                                <ArrowLeft className="w-4 h-4" />
                                Back to Projects
                            </Link>
                            <div>
                                <h1 className="text-2xl font-semibold text-slate-900">{project.name}</h1>
                                <p className="text-sm text-slate-500 flex items-center gap-1">
                                    <Github className="w-3 h-3" />
                                    {project.repo_owner}/{project.repo_name}
                                </p>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="container mx-auto px-6 py-8">
                    <Card>
                        <CardHeader>
                            <CardTitle>Project Details</CardTitle>
                            <CardDescription>Information and statistics for this project</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <p className="text-sm font-medium text-slate-500">Repository URL</p>
                                <a href={project.repo_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                    {project.repo_url}
                                </a>
                            </div>
                            {project.description && (
                                <div>
                                    <p className="text-sm font-medium text-slate-500">Description</p>
                                    <p className="text-sm">{project.description}</p>
                                </div>
                            )}
                            <div className="flex gap-2 pt-4">
                                <Button asChild>
                                    <Link to={`/projects/${project.id}/tasks`}>
                                        <Activity className="w-4 h-4 mr-2" />
                                        View Tasks
                                    </Link>
                                </Button>
                                <Button variant="outline" asChild>
                                    <a href={project.repo_url} target="_blank" rel="noopener noreferrer">
                                        <ExternalLink className="w-4 h-4 mr-2" />
                                        Open in GitHub
                                    </a>
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </main>
            </div>
        </ProtectedRoute>
    );
}