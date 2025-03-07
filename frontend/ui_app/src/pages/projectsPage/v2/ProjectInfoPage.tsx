import React, { useEffect, useState } from "react";
import styles from "../project_info.module.scss";
import { useStore } from "../../../stores";
import {Link, useLocation, useParams} from "react-router-dom";
import { StoreNames } from "../../../stores";
import { RiFlowChart } from "react-icons/ri";
import Project from "../../../servers/asset_server/project";
import { AiOutlineProject } from "react-icons/ai";
import { BsCloudUpload } from "react-icons/bs";
import { GrAdd } from "react-icons/gr";
import { ErrorBoundary } from "../../../components/errorBoundary";
import {BreadCrumbV2} from "../../../components/breadCrumb/BreadCrumbV2";
import ProjectView from "./tabs/ProjectView";
import {TabBar} from "../../../components/tabbar";
import {BookLock, BookText, FileChartColumn, Layers, Package, PackagePlus, UserCircle} from "lucide-react";
import {ThreeBarsIcon} from "../../../components/icons/Icons";
import ReadMeView from "./tabs/ReadMeView";
import UserListView from "./tabs/UserListView";
import BucketListView from "./tabs/BucketListView";
import MetricsListView from "pages/projectsPage/v2/tabs/MetricsListView";
import SecretsListView from "pages/projectsPage/v2/tabs/SecretsListView";

export const ProjectIcons: any = {
    "asset_playground": BsCloudUpload,
    "default": AiOutlineProject,
    "add": GrAdd,
}

const ProjectInfoPage = () => {
    //stores
    const userStore = useStore(StoreNames.userStore);
    const projectStore = useStore(StoreNames.projectStore);
    const { project_id } = useParams();
    const storedProject: any = projectStore.get(project_id);
    const [project, setProject] = useState<Project | null>(storedProject);
    const [error, setError] = useState<string>('');
    const location = useLocation();
    console.log("location:", location);
    const params = new URLSearchParams(location.search);
    const activeTab = params.get("tab") || "info";

    useEffect(() => {
        /***
         * user could directly copy & paste the project-url in browser
         */
        if (!storedProject) {
            Project.getFromServer(userStore.get("user").username, project_id)
                .then((data: Project) => {
                    setProject(data);
                }).catch((error: any) => {
                    setError(error)
                    console.error(error)
                })
        }
    }, [])

    if (!project) {
        return null;
    }
    const Nav = [
        {name: "projects", url: "/projects", label: "Projects", index: 0},
        {name: "project", url: `${location.pathname}?tab=info`, index: 1, label: project.title || project.name},
        {name: "tab", url: "", index: 2, label: activeTab},
    ]
    
    const TABS  = [
        {name: "info", label: "About", icon: <ThreeBarsIcon className="size-3 mr-2"/>, link: `${location.pathname}?tab=info`},
        {name: "card", label: "ReadMe", icon: <BookText className="size-3 mr-2"/>, link: `${location.pathname}?tab=card`},
        {name: "users", label: "Users", icon: <UserCircle className="size-3 mr-2"/>, link: `${location.pathname}?tab=users`},
        {name: "buckets", label: "Buckets", icon: <Package className="size-3 mr-2"/>, link: `${location.pathname}?tab=buckets`},
        {name: "stats", label: "Metrics", icon: <FileChartColumn className="size-3 mr-2"/>, link: `${location.pathname}?tab=stats`},
        {name: "secrets", label: "Secrets", icon: <BookLock className="size-3 mr-2"/>, link: `${location.pathname}?tab=secrets`},
        {name: "assets", label: "Assets", icon: <Layers className="size-3 mr-2"/>, link: `/assets/?project_id=${project_id}`},
    ]
    
    const TabView = (tab) => {
        switch (tab) {
            case "info":
                return <ProjectView project={project} iconMap={ProjectIcons}/>
            case "card":
                return <ReadMeView project={project}/>
            case "users":
                return <UserListView project={project}/>
            case "stats":
                return <MetricsListView project={project}/>
            case "buckets":
                return <BucketListView project={project}/>
            case "secrets":
                return <SecretsListView project={project}/>
            default:
                return <div>Default</div>
        }
    }

    return (
        <div className="">
            <ErrorBoundary>
                <div className='bg-base-200 pt-6 px-16'>
                    <div className="flex items-center">
                        <div className="flex">
                            <BreadCrumbV2 items={Nav}/>
                        </div>
                    </div>
                    <div className={"pt-6"}>
                        <p className="text-md text-neutral-500 mb-4">{project.title || project.name}</p>
                        <TabBar tabs={TABS} activeTab={activeTab}/>
                    </div>
                </div>
                <div className="mt-6 px-16">
                    {TabView(activeTab)}
                </div>
            </ErrorBoundary>
        </div>
    )
}

export default ProjectInfoPage;
