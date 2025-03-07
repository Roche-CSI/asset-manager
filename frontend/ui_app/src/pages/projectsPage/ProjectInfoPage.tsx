import React, { useEffect, useState } from "react";
import styles from "./project_info.module.scss";
import { useStore } from "../../stores";
import { Link, useParams } from "react-router-dom";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import { StoreNames } from "../../stores";
import ProjectBrowser from "../../components/projectBrowser/ProjectBrowser";
import { RiFlowChart } from "react-icons/ri";
import Project from "../../servers/asset_server/project";
import { AiOutlineProject } from "react-icons/ai";
import { BsCloudUpload } from "react-icons/bs";
import { GrAdd } from "react-icons/gr";
import { ErrorBoundary } from "../../components/errorBoundary";

export const ProjectIcons: any = {
    "asset_playground": BsCloudUpload,
    "default": AiOutlineProject,
    "add": GrAdd,
}

export default function ProjectInfoPage() {
    //stores
    const userStore = useStore(StoreNames.userStore);
    const projectStore = useStore(StoreNames.projectStore);
    const { project_id } = useParams();
    const storedProject: any = projectStore.get(project_id);
    const [project, setProject] = useState<Project | null>(storedProject);
    const [error, setError] = useState<string>('');

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

    return (
        <div className={styles.page}>
            <ErrorBoundary>
                {pageTitle(project.name)}
                {project && <ProjectBrowser project={project} iconMap={ProjectIcons} />}
                {error && <h2>Project Not Found</h2>}
            </ErrorBoundary>
        </div>
    )

    function pageTitle(name: string) {
        return (
            <div style={{ border: "none", display: "flex" }}>
                <div className={styles.pageHeader}>
                    <h5>
                        <Link to="/projects">projects</Link>
                        <ArrowRightIcon />
                        <span>{name}</span>
                    </h5>
                </div>
            </div>
        )
    }
}