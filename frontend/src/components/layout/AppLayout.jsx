import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Outlet, useParams, useLocation } from 'react-router-dom';
import { FiSearch, FiPlus, FiMenu } from 'react-icons/fi';
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
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);

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
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <main className="lg:pl-[240px] min-h-screen flex flex-col transition-all">
                {/* Header */}
                <header className="border-b border-border bg-background sticky top-0 z-20 w-full">
                    {/* Main header bar */}
                    <div className="h-14 lg:h-16 flex items-center justify-between px-3 md:px-4 lg:px-8">
                        <div className="flex items-center gap-2 md:gap-3 min-w-0 flex-1">
                            {/* Mobile menu button */}
                            <button
                                onClick={() => setSidebarOpen(true)}
                                className="lg:hidden p-2 -ml-2 text-text-muted hover:text-text-main flex-shrink-0"
                                aria-label="Open menu"
                            >
                                <FiMenu className="w-5 h-5" />
                            </button>

                            <div className="flex items-baseline gap-2 min-w-0 flex-1">
                                <h1 className="text-base md:text-lg lg:text-xl font-bold truncate">{projectTitle}</h1>
                                <span className="text-text-muted hidden sm:inline">/</span>
                                <span className="text-sm font-medium text-text-main hidden sm:inline truncate">{getPageTitle()}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-1.5 md:gap-2 lg:gap-4 flex-shrink-0">
                            {/* Search Bar - Desktop only */}
                            <div className="relative hidden md:block w-48 lg:w-64 xl:w-80 group">
                                <input
                                    type="text"
                                    placeholder="Search..."
                                    className="w-full pl-9 pr-4 py-1.5 lg:py-2 bg-surfaceHover border-transparent focus:bg-white focus:border-primary/50 focus:ring-2 focus:ring-primary/10 rounded-full text-sm transition-all outline-none border"
                                />
                                <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted group-focus-within:text-primary transition-colors" />
                            </div>

                            {/* Mobile search button */}
                            <button
                                onClick={() => setSearchOpen(!searchOpen)}
                                className="md:hidden p-2 text-text-muted hover:text-text-main"
                                aria-label="Search"
                            >
                                <FiSearch className="w-5 h-5" />
                            </button>

                            {/* New Button */}
                            <Button size="sm" className="rounded-full shadow-none text-xs md:text-sm px-2.5 md:px-3 lg:px-4">
                                <FiPlus className="w-4 h-4 lg:mr-1.5" />
                                <span className="hidden lg:inline">New</span>
                            </Button>
                        </div>
                    </div>

                    {/* Mobile search bar (expandable) */}
                    {searchOpen && (
                        <div className="md:hidden px-3 pb-3 border-t border-border bg-background animate-fade-in">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search documents..."
                                    className="w-full pl-9 pr-4 py-2.5 bg-surfaceHover border border-border focus:bg-white focus:border-primary/50 focus:ring-2 focus:ring-primary/10 rounded-lg text-sm transition-all outline-none"
                                    autoFocus
                                />
                                <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                            </div>
                        </div>
                    )}
                </header>

                {/* Content Area */}
                <div className="flex-1 p-3 md:p-4 lg:p-8 max-w-7xl w-full mx-auto animate-fade-in">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};
