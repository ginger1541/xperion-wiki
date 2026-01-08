import React from 'react';
import { Sidebar } from './Sidebar';
import { Outlet, useParams, useLocation } from 'react-router-dom';
import { FiSearch, FiPlus } from 'react-icons/fi';
import { Button } from '../ui/Button';

// Mock Project Data (In real app, fetch from API based on ID)
const PROJECT_MAP = {
    dagosian: "다고시안 듀얼단",
    estua: "패스파인더: 이스투아",
    citron: "시트론 성의 개척자들"
};

export const AppLayout = () => {
    const { projectId } = useParams();
    const location = useLocation();

    const projectTitle = PROJECT_MAP[projectId] || "Unknown Project";

    // Get Breadcrumb Title
    const getPageTitle = () => {
        const path = location.pathname;
        if (path.includes('/dashboard')) return 'Dashboard';

        // Simple extraction for prototype
        const segments = path.split('/');
        const lastSegment = segments[segments.length - 1];
        return lastSegment.charAt(0).toUpperCase() + lastSegment.slice(1);
    };

    return (
        <div className="min-h-screen bg-background text-text-main font-sans">
            <Sidebar />
            <main className="pl-[240px] min-h-screen flex flex-col transition-all">
                {/* Header */}
                <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-background sticky top-0 z-10 w-full">
                    <div>
                        <div className="flex items-baseline gap-2">
                            <h1 className="text-xl font-bold">{projectTitle}</h1>
                            <span className="text-text-muted">/</span>
                            <span className="text-sm font-medium text-text-main">{getPageTitle()}</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Search Bar */}
                        <div className="relative w-64 md:w-80 group">
                            <input
                                type="text"
                                placeholder="검색어를 입력하세요..."
                                className="w-full pl-10 pr-4 py-2 bg-surfaceHover border-transparent focus:bg-white focus:border-primary/50 focus:ring-2 focus:ring-primary/10 rounded-full text-sm transition-all outline-none border"
                            />
                            <FiSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted group-focus-within:text-primary transition-colors" />
                        </div>

                        {/* New Button */}
                        <Button size="sm" className="rounded-full shadow-none">
                            <FiPlus className="mr-1.5" /> New
                        </Button>
                    </div>
                </header>

                {/* Content Area */}
                <div className="flex-1 p-8 max-w-7xl w-full mx-auto animate-fade-in">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};
