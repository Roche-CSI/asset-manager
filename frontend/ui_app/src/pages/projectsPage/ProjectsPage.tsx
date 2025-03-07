import React, { useCallback, useEffect, useState } from "react"
import styles from "./projects.module.scss"
import ProjectCard from "./ProjectCard";
import { SimpleToast } from "../../components/toasts";
import { ToastType } from "../../components/toasts/SimpleToast";
import { Project } from "../../servers/asset_server";
import {fetchPost} from "../../servers/base";
import AssetURLs from "../../servers/asset_server/assetURLs";
import { StoreNames, useStore } from "../../stores";
import { ProjectIcons } from "./ProjectInfoPage";
import { useNavigate } from "react-router-dom";
import CreateProjectLauncher from "./ProjectLauncher"
import { ErrorBoundary } from "../../components/errorBoundary";
import ProjectAlert from "./ProjectAlert";
import { ProjectsTable } from "../../components/tables/projectsTable";
import Paper from '@mui/material/Paper';
import { AlertDismissible } from "../../components/alerts";
import { SpinIndicator } from "../../components/spinIndicator";
import { save_user } from "../../components/layout/PrivateRoute";
import Tooltip from '@mui/material/Tooltip';
import {Button} from "react-bootstrap";

export default function ProjectsPage() {
    //stores
    const userStore = useStore(StoreNames.userStore);
    const projectStore = useStore(StoreNames.projectStore);
    const classIdStore = useStore(StoreNames.classIdStore);
    const navigate = useNavigate();

    //states
    const [createProject, setCreateProject] = useState<any>(null);
    const [projects, setProjects] = useState<any[]>([]);
    const [toast, setToast] = useState<any>({ type: null, title: null, description: null });
    const [showAlert, setShowAlert] = useState<boolean>(false);
    const [activeProject, setActiveProject] = useState<string>(userStore.get("active_project"));
    const [userProjects, setUserProjects] = useState<any>(userStore.get("projects"))
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");

    const onProjectInfoClicked = (id: string) => {
        navigate(`/project/${id}`)
    }

    useEffect(() => {
        fetchProjects();
    }, [])

    useEffect(() => {
        if (userStore.get("first_time_user")) {
            userStore.remove("first_time_user")
            setShowAlert(true)
        }
    }, [])

    const fetchProjects = () => {
        if (!projectStore.last_update) {
            Project.getFromServer(userStore.get("user").username).then((data: any[]) => {
                data.forEach((proj: any) => projectStore.set(proj.id, proj));
                setProjects(data);
                setError("");
            }).catch((error) => {
                setError(error.message)
                setProjects([]);
            })
        } else {
            setProjects(Object.values(projectStore.get()));
        }
    }

    const handleProjectSelection = (id: string) => {
        userStore.set("active_project", id)
        setActiveProject(id)
        classIdStore.didFullUpdate = false; //force update class list
    }

    const handleRefresh = useCallback(() => {
        setLoading(true)
        fetchPost(new AssetURLs().token_login_route(), {token: userStore.get("user").token})
        .then((data: any) => {
            // console.log("res: ", data);
            let token = save_user(userStore, data);
            setUserProjects(userStore.get("projects"))
        }).catch((error) => setError(error.message));
        setLoading(false)
    }, [userStore])

    const launchers = projects.map((p: any, idx: number) => {
        const icon: any = ProjectIcons?.[p.name] ?? ProjectIcons.default;
        return <ProjectCard key={idx}
            icon={icon}
            id={p.id}
            name={p.name}
            label={p.description}
            onClick={onProjectInfoClicked} />
    })

    const toaster = () => {
        if (!toast.type) {
            return null;
        }
        return (
            <SimpleToast title={toast.title}
                message={toast.description}
                type={toast.type}
                onClose={() => setToast({ type: null, title: null, description: null })}
                autoHide={true}
                show={true} />
        )
    }

    return (
        <div className='p-4'>
            <div className='w-2/3 m-auto'>
            {error && renderError()}
            <ErrorBoundary>
                <h5 className={styles.pageHeader}>Projects</h5>
                <div className={styles.launchIcons}>
                    {/* {launchers} */}
                    {addProjectIcon()}
                </div>
                <Paper className={styles.projectsTableContainer}>
                    <ProjectsTable projects={projects} onProjectInfoClicked={onProjectInfoClicked}
                        activeProject={activeProject}
                        handleSelection={handleProjectSelection}
                        userProjects={userProjects} />
                </Paper>
                <div className='has-bootstrap'>
                <AlertDismissible variant={"primary"} className={styles.alert}>
                    <p>To Obtain Access, Please Contact Admin.</p>
                    <p>Admin Slack: </p>
                    <div className='mt-3 flex flex-row items-center justify-center'>
                        <div><p><b>Or</b></p></div>
                        <div className='inline-flex items-center justify-center rounded-md border border-primary  
                            bg-white text-center font-medium text-base hover:text-primary lg:px-8 xl:px-10 ml-2 p-1 cursor-pointer' 
                        onClick={() => handleRefresh()}>
                            Refresh
                        </div>
                    </div>
                </AlertDismissible>
                </div>
                {loading && <SpinIndicator message={"loading"} />}
                {createProject &&
                    <CreateProjectLauncher
                        onLaunch={onLauncherComplete}
                        onCancel={onLauncherCancel}
                        type={"new"} />
                }
                {toaster()}
                {showAlert && <ProjectAlert show={showAlert} setShow={setShowAlert} projects={projects} />}
            </ErrorBoundary>
            </div>
        </div>
    )

    function addProjectIcon() {
        const rss_data_science_project: any = Object.values(userStore.get("projects")).find((proj: any) => proj.name === "rss_data_science")
        if (!rss_data_science_project || !rss_data_science_project.can_admin_project) {
            return null
        }
        return <ProjectCard key={projects.length + 1}
            icon={ProjectIcons["add"]}
            label={"Add Project"}
            onClick={onProjectClicked} />
    }

    function onLauncherComplete(message: string) {
        if (message === "success") {
            setToast({ type: ToastType.Success, title: "Success", description: "Project Created Successfully" })
            setCreateProject(null);
        } else if (message === "error") {
            setToast({ type: ToastType.Danger, title: "Error", 
                description: "Error in Creating Project, please check the credentials" })
        }
        fetchProjects();
    }

    function onProjectClicked(project_id: string) {
        setCreateProject((createProject: any) => {
            return {
                project_id: project_id,
                launch_type: "new"
            }
        });
    }

    function onLauncherCancel() {
        setCreateProject(null);
    }

    function renderError() {
        return (
            <AlertDismissible title={"Oh Snap! You got an error!"}>
                {error}
                <p>Make sure you are connected to VPN</p>
            </AlertDismissible>
        )
    }

}