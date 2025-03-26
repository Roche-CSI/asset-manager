import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaBars } from 'react-icons/fa6';
import { BadgeAlert, Layers, Box, Github, BookOpen, Search } from "lucide-react";
import { StoreNames, useStore } from '../../stores';
import { BadgedDropDown } from '../dropDown';
import { UserMenu } from './userMenu';
import ProjectsDropdown from './ProjectsDropdown';
import { Logo } from '../logo';
import { MenuItem } from "../common";
import { CircularAvatar } from "../../pages/projectsPage/v2/cards/UserCard"

interface NavItem {
    name: string;
    route: string;
    icon: any;
    label: string;
    pattern?: string;
    isJwtProtected?: boolean; // If the route is protected by JWT
}

export const TopNavV2 = () => {
    const userStore = useStore(StoreNames.userStore, true);
    const activeProjectId = userStore.get("active_project");
    const activeProject = userStore.get("projects")?.[activeProjectId];
    const [currentUser, setCurrentUser] = useState({ username: null, picture: null });
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const active: string = location.pathname.split("/")[1];

    const LEFT_MENU: Record<string, NavItem> = {
        asset: {
            name: "assets",
            route: `/assets?project_id=${activeProject?.id}`,
            icon: <Layers className="size-3.5 text-neutral-400" />,
            label: "Assets",
            pattern: "asset"
        },
        pipelines: {
            name: "pipelines",
            route: userStore.get('dashboard_settings')?.pipeline_url || '',
            isJwtProtected: true,
            icon: <Box className="size-3" />,
            label: "Pipelines",
            pattern: "pipeline"
        },
        issue: {
            name: "issue",
            route: "/issue",
            label: "Issues",
            icon: <BadgeAlert className="size-4 text-neutral-400" />,
            pattern: "issue"
        }
    }
    
    const RIGHT_MENU: Record<string, any> = {
        search: {
            name: "search",
            route: "/search",
            icon: <Search className="size-4 text-neutral-400" />,
            label: "Search"
        },
        github: {
            name: "github",
            route: import.meta.env.VITE_REPO_URL || '',
            label: "Github",
            icon: <Github className="size-4 text-neutral-400" />,
            pattern: "github"
        },
        documentation: {
            name: "documentation",
            route: import.meta.env.VITE_DOCS_URL || '',
            label: "Docs",
            icon: <BookOpen className="size-4 text-neutral-400" />,
            pattern: "documentation"
        },
    };


    useEffect(() => {
        const user = userStore.get("user") || {};
        setCurrentUser({ username: user.username, picture: user.picture });

        const subscription = userStore.subscribe("updates", (data: Record<string, any>) => {
            const updatedUser = data.user || {};
            setCurrentUser({ username: updatedUser.username, picture: updatedUser.picture });
        });

        return () => subscription.unsubscribe();
    }, []);

    const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

    const onUserMenuClick = (item: Record<string, any>) => {
        if (item.name === "logout" || item.name === "switch") {
            userStore.clear();
        }
        navigate(item.route);
    };

    const renderNavLink = (item: NavItem) => {
        const isExternal = item.route.startsWith('http');
        const baseClasses = `flex items-center px-3 py-2 text-sm font-medium
            ${active.includes(item?.pattern || '') ? "border border-base-300 rounded-md" : ""}`;

        // Add subtle styling for external links
        const externalClasses = isExternal ? "after:content-['↗'] after:ml-1 after:text-neutral-400 hover:after:text-primary" : "";

        if (isExternal) {
            const route: string = item.isJwtProtected? `${item.route}?token=${userStore.get("user").token}` : item.route;
            return (
                <a
                    key={item.name}
                    href={route}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`${baseClasses} ${externalClasses} hover:text-primary transition-colors`}
                >
                    <span className="mr-2">{item.icon}</span>
                    <span className={active.includes(item?.pattern || '') ? "font-bold" : ""}>
                        {item.label}
                    </span>
                </a>
            );
        }

        return (
            <Link
                key={item.name}
                to={item.route}
                className={baseClasses}
            >
                <span className="mr-2">{item.icon}</span>
                <span className={active.includes(item?.pattern || '') ? "font-bold" : ""}>
                    {item.label}
                </span>
            </Link>
        );
    };

    return (
        <nav className="bg-white w-full px-8 border-b border-base-300 z-10">
            <div className="px-2 sm:px-6 lg:px-8">
                <div className="relative flex h-16 items-center justify-between">
                    <div className="flex items-center">
                        <div className="flex items-center sm:hidden">
                            <button
                                type="button"
                                className="relative inline-flex items-center justify-center rounded-md p-2 text-primary hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                                onClick={toggleMobileMenu}
                            >
                                <span className="sr-only">Open main menu</span>
                                {isMobileMenuOpen ? (
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5"
                                        stroke="currentColor" aria-hidden="true">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                ) : (
                                    <FaBars className="h-6 w-6" />
                                )}
                            </button>
                        </div>

                        <Link to="/" className="flex-shrink-0 items-center">
                            <Logo className="size-10" />
                        </Link>

                        <div className="hidden sm:ml-6 sm:block">
                            <div className="flex space-x-4">
                                {Object.values(LEFT_MENU).map(renderNavLink)}
                            </div>
                        </div>
                    </div>

                    <div className="flex">
                        <div className="hidden sm:ml-6 sm:block mr-16">
                            <div className="flex space-x-4">
                                {Object.values(RIGHT_MENU).map(renderNavLink)}
                            </div>
                        </div>

                        <div className="flex items-center">
                            <ProjectsDropdown />
                            <div className="relative ml-6 flex justify-end">
                                {currentUser.username &&
                                    <BadgedDropDown
                                        customToggle={() => renderUserToggle(currentUser)}
                                        contentData={UserMenu}
                                        renderItems={(item: MenuItem, index: number) => renderUserMenu(item, index, onUserMenuClick)}
                                    />
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {isMobileMenuOpen && (
                <div className="sm:hidden">
                    <div className="space-y-1 px-2 pb-3 pt-2">
                        {Object.values(LEFT_MENU).map((item: Record<string, any>) => {
                            const isExternal = item.route.startsWith('http');
                            const baseClasses = `flex items-center px-3 py-2 rounded-md text-base font-medium ${active.includes(item.pattern)
                                ? 'bg-gray-900 text-white'
                                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                                }`;

                            if (isExternal) {
                                return (
                                    <a
                                        key={item.name}
                                        href={item.route}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={`${baseClasses} after:content-['↗'] after:ml-1`}
                                    >
                                        {item.icon}
                                        <span className="ml-2">{item.label}</span>
                                    </a>
                                );
                            }

                            return (
                                <Link
                                    key={item.name}
                                    to={item.route}
                                    className={baseClasses}
                                >
                                    {item.icon}
                                    <span className="ml-2">{item.label}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}
        </nav>
    );
};

const renderUserToggle = (user: Record<string, any>) => (
    <div>
        <div className="flex items-center justify-center">
            <CircularAvatar username={user.username} size="sm"
                bgColor="bg-gradient-to-r from-blue-500 to-blue-700" />
        </div>
    </div>
);

const renderUserMenu = (item: MenuItem, index: number, onClick: Function) => (
    <div key={index} onClick={() => onClick(item)}>
        <div className="flex items-center px-4 py-2 text-sm text-gray-700 cursor-pointer hover:text-primary">
            <item.icon className="h-3 w-3 mr-2" />
            <span>{item.label}</span>
        </div>
    </div>
);

export default TopNavV2;
