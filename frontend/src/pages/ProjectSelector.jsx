import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { FiPlus, FiBox, FiLoader } from 'react-icons/fi';
import { getProjects } from '../services/api';

export default function ProjectSelector() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            setLoading(true);
            const data = await getProjects();
            setProjects(data.projects || []);
        } catch (err) {
            console.error('Failed to fetch projects:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-sidebar flex items-center justify-center">
                <div className="text-center">
                    <FiLoader className="w-12 h-12 text-primary mx-auto mb-4 animate-spin" />
                    <p className="text-text-muted">Loading projects...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-sidebar flex items-center justify-center">
                <Card className="p-8 text-center max-w-md">
                    <p className="text-red-500 mb-4">Failed to load projects: {error}</p>
                    <button
                        onClick={fetchProjects}
                        className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primaryHover"
                    >
                        Retry
                    </button>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-sidebar flex flex-col items-center justify-center p-8">
            <div className="max-w-4xl w-full space-y-8">
                {/* Header */}
                <div className="text-center space-y-2 mb-8">
                    <h1 className="text-3xl font-bold text-text-main tracking-tight">Xperion Wiki</h1>
                </div>
                {/* Project Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projects.map((project) => (
                        <Card
                            key={project.id}
                            onClick={() => navigate(`/project/${project.id}`)}
                            className="cursor-pointer group hover:shadow-lg transition-all duration-300 border-transparent hover:border-primary/20 relative overflow-hidden"
                        >
                            <div className={`h-2 ${project.color}`} />
                            <div className="p-6 space-y-4">
                                <div className="w-12 h-12 rounded-lg bg-surfaceHover flex items-center justify-center group-hover:bg-primary/5 transition-colors">
                                    <FiBox className="w-6 h-6 text-text-muted group-hover:text-primary transition-colors" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-text-main mb-1 group-hover:text-primary transition-colors">
                                        {project.title}
                                    </h3>
                                    <p className="text-sm text-text-muted line-clamp-2 h-10">
                                        {project.description}
                                    </p>
                                </div>
                                <div className="pt-4 border-t border-border flex items-center justify-between text-xs text-text-muted">
                                    <span>{project.doc_count} Documents</span>
                                    <span className="group-hover:translate-x-1 transition-transform">Enter &rarr;</span>
                                </div>
                            </div>
                        </Card>
                    ))}

                    {/* New Project Button */}
                    <button className="flex flex-col items-center justify-center p-6 rounded-lg border-2 border-dashed border-border text-text-muted hover:text-primary hover:border-primary/50 hover:bg-primary/5 transition-all gap-3 h-full min-h-[240px]">
                        <div className="w-12 h-12 rounded-full bg-surface flex items-center justify-center shadow-sm">
                            <FiPlus className="w-6 h-6" />
                        </div>
                        <span className="font-medium">새 세계관 생성</span>
                    </button>
                </div>
            </div>

            <footer className="mt-16 text-xs text-text-light">
                Xperion Wiki System v0.2.1 • Local Mode
            </footer>
        </div>
    );
}
