import React from "react";
import { BadgeAlert, Layers, Box, Github, BookOpen, Search } from "lucide-react";

import { StoreNames, useStore } from '../../stores';


interface NavItem {
    name: string;
    route: string;
    icon: any;
    label: string;
    pattern?: string;
}

let activeProject;

const GetActiveProject = () => {
    const userStore = useStore(StoreNames.userStore, true);
    const activeProjectId = userStore.get("active_project");
    return userStore.get("projects")?.[activeProjectId];
};

activeProject = GetActiveProject();


export const LEFT_MENU: Record<string, NavItem> = {
    asset: {
        name: "assets",
        route: `/assets?project_id=${activeProject?.id}`,
        icon: <Layers className="size-3.5 text-neutral-400" />,
        label: "Assets",
        pattern: "asset"
    },
    issue: {
        name: "issue",
        route: "/issue",
        label: "Issues",
        icon: <BadgeAlert className="size-4 text-neutral-400" />,
        pattern: "issue"
    }
}

export const RIGHT_MENU: Record<string, any> = {
    search: {
        name: "search",
        route: "/search",
        icon: <Search className="size-4 text-neutral-400" />,
        label: "Search"
    },
    github: {
        name: "github",
        route: "https://github.com",
        label: "Github",
        icon: <Github className="size-4 text-neutral-400" />,
        pattern: "github"
    },
    documentation: {
        name: "documentation",
        route: "",
        label: "Docs",
        icon: <BookOpen className="size-4 text-neutral-400" />,
        pattern: "documentation"
    },
};