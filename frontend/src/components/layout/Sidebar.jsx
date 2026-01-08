import React from 'react';
import { NavLink, useParams, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import {
    FiFolder,
    FiFileText,
    FiMapPin,
    FiUser,
    FiBookOpen,
    FiGlobe,
    FiAnchor,
    FiArrowLeft
} from 'react-icons/fi';

const NAV_BASE = [
    { label: "Overview", path: "dashboard", icon: FiFolder },
];

const WIKI_CATEGORIES = [
    { label: "CHARACTERS", path: "wiki/characters", icon: FiUser },
    { label: "EPISODES", path: "wiki/episodes", icon: FiFileText },
    { label: "LOCATIONS", path: "wiki/locations", icon: FiMapPin },
    { label: "LORE", path: "wiki/lore", icon: FiBookOpen },
    { label: "NATIONS", path: "wiki/nations", icon: FiGlobe },
    { label: "RACES", path: "wiki/races", icon: FiUser },
    { label: "RELIGIONS", path: "wiki/religions", icon: FiAnchor },
];

export const Sidebar = () => {
    const { projectId } = useParams();
    const location = useLocation();

    // Helper to check active state relative to current project root
    const isActiveLink = (path) => {
        // Construct absolute path for comparison
        const targetPath = `/project/${projectId}/${path}`;
        return location.pathname.startsWith(targetPath);
    };

    return (
        <aside className="w-[240px] h-screen fixed left-0 top-0 bg-sidebar border-r border-border flex flex-col text-sm z-20 transition-all">
            {/* Back to Gateway */}
            <div className="p-3 border-b border-border">
                <NavLink
                    to="/"
                    className="flex items-center gap-2 px-2 py-1.5 text-text-muted hover:text-text-main hover:bg-surfaceHover rounded-md transition-colors"
                >
                    <FiArrowLeft className="w-4 h-4" />
                    <span className="font-medium">All Projects</span>
                </NavLink>
            </div>

            {/* Sidebar Content */}
            <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">

                {/* General Section */}
                <div>
                    {NAV_BASE.map((item) => (
                        <NavLink
                            key={item.label}
                            to={`/project/${projectId}/${item.path}`}
                            className={({ isActive }) => cn(
                                "flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors mb-0.5",
                                isActive
                                    ? "bg-primary/10 text-primary font-medium"
                                    : "text-text-main hover:bg-surfaceHover"
                            )}
                        >
                            <item.icon className="w-4 h-4 opacity-70" />
                            <span className="truncate">{item.label}</span>
                        </NavLink>
                    ))}
                </div>

                {/* Wiki Categories */}
                <div>
                    <h3 className="px-3 mb-2 text-xs font-bold text-text-muted select-none">
                        DOCUMENTS
                    </h3>
                    <div className="space-y-0.5">
                        {WIKI_CATEGORIES.map((item) => (
                            <NavLink
                                key={item.label}
                                to={`/project/${projectId}/${item.path}`}
                                className={({ isActive }) => cn(
                                    "flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors",
                                    isActive
                                        ? "bg-primary/10 text-primary font-medium"
                                        : "text-text-main hover:bg-surfaceHover"
                                )}
                            >
                                <item.icon className="w-4 h-4 opacity-70" />
                                <span className="truncate">{item.label}</span>
                            </NavLink>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-border">
                <div className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-surfaceHover cursor-pointer">
                    <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                        D
                    </div>
                    <span className="font-medium text-text-main">DM Account</span>
                </div>
            </div>
        </aside>
    );
};
