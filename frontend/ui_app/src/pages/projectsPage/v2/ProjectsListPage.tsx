import React, {useCallback, useEffect, useState} from "react"
import styles from "../projects.module.scss"
import {SimpleToast} from "../../../components/toasts";
import {ToastType} from "../../../components/toasts/SimpleToast.tsx";
import {Project} from "../../../servers/asset_server";
import {fetchPost} from "../../../servers/base";
import AssetURLs from "../../../servers/asset_server/assetURLs.ts";
import {StoreNames, useStore} from "../../../stores";
import {ProjectIcons} from "../ProjectInfoPage.tsx";
import {useNavigate} from "react-router-dom";
import CreateProjectLauncher from "../ProjectLauncher.tsx"
import {ErrorBoundary} from "../../../components/errorBoundary";
import ProjectAlert from "../ProjectAlert.tsx";
import {AlertDismissible} from "../../../components/alerts";
import {SpinIndicator} from "../../../components/spinIndicator";
import {save_user} from "../../../components/layout/PrivateRoute";
import {BreadCrumbV2} from "../../../components/breadCrumb/BreadCrumbV2";
import {FilterBar} from "../../../components/filterbar";
import {AddNewIcon} from "../../../components/icons/Icons";
import {Link} from "react-router-dom";
import DigitalAssetIcons from "./DigitalAssetIcons";
import Spinner from "../../../components/spinner/Spinner";
import {ProjectForm} from "pages/projectsPage/v2/forms/ProjectForm";
import ProjectCard from "./cards/ProjectCard";

export default function ProjectsListPage() {
	//stores
	const userStore = useStore(StoreNames.userStore);
	const projectStore = useStore(StoreNames.projectStore);
	const classIdStore = useStore(StoreNames.classIdStore);
	const navigate = useNavigate();
	
	const isCreate = location.pathname.split("/").pop() === "create";
	const currentUser = userStore.get("user")
	
	//states
	const [projects, setProjects] = useState<Project[]>([]);
	const [toast, setToast] = useState<any>({type: null, title: null, description: null});
	const [showAlert, setShowAlert] = useState<boolean>(false);
	const [activeProject, setActiveProject] = useState<string>(userStore.get("active_project"));
	const [userProjects, setUserProjects] = useState<any>(userStore.get("projects"))
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string>("");
	const [searchTerm, setSearchTerm] = useState<string>("");

	const renderData = searchTerm 
    	? projects.filter((item: Project) => 
        	item.name.toLowerCase().includes(searchTerm.toLowerCase())
      	)
    	: projects;
	
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
		console.log("project clicked: ", id);
		if (id in userProjects) {
			userStore.set("active_project", id)
			setActiveProject(id)
			classIdStore.didFullUpdate = false; //force update class list
		}
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
		                    onClick={onProjectInfoClicked}/>
	})
	
	const toaster = () => {
		if (!toast.type) {
			return null;
		}
		return (
			<SimpleToast title={toast.title}
			             message={toast.description}
			             type={toast.type}
			             onClose={() => setToast({type: null, title: null, description: null})}
			             autoHide={true}
			             show={true}/>
		)
	}
	
	const onSearch = (value: string) => {
		setSearchTerm(value)
	}
	
	const onCreate = () => {
		navigate("/projects/create")
	}
	
	const Nav = [
		{name: "projects", url: "/projects", label: "Projects", index: 1},
	]
	if (isCreate) {
		Nav.push({name: "create", url: "", label: "Create", index: 2})
	}
	
	const onNewProject = () => {
		fetchProjects();
		navigate("/projects")
	}
	
	const onNewProjectCancel = () => {
		navigate("/projects")
	}
	
	return (
		<div className='mb-6'>
			<div className='bg-base-200 pt-6 px-16 mb-6'>
				<div className='flex flex-row text-xl font-normal'>
					<BreadCrumbV2 items={Nav}/>
				</div>
				<div className={"pt-4"}>
					<FilterBar
						label={
							<React.Fragment>
								<p className="text-lg font-normal flex items-center">
									{/*<ArtifactsIcon className="h-3.5 w-3.5 mr-2"/>*/}
									<span>Projects</span>
								</p>
								<p className="text-lg text-neutral-500 mr-4">{projects.length.toLocaleString()}</p>
							</React.Fragment>}
						onSearch={onSearch}
						placeholder={"Filter by project name"}
						rightButton={
							<button
								className="btn btn-sm btn-secondary rounded-md"
								onClick={() => onCreate()}>
								<AddNewIcon className="h-3.5 w-3.5 mr-2"/>
								<span>New Project</span>
							</button>
						}/>
				</div>
				<div className={"pb-2 flex text-xs"}>
					<p>{`To obtain access please contact admins on Slack ${userStore.get('dashboard_settings')?.slack_channel || ''}`}</p>
					<p className='ml-1.5 italic'></p>
				</div>
			</div>
			
			<div className='m-auto px-16'>
				<div className="text-lg text-neutral mb-6 font-semibold">{isCreate ? "Create Project" : "Project List"}</div>
				{error && renderError()}
				<ErrorBoundary>
					{
						isCreate ?
							<div className="border border-base-300 rounded-md p-6 mb-6">
								<ProjectForm
									onSave={onNewProject}
									onCancel={onNewProjectCancel}
									action={"create"}
								/>
							</div>
							:
							<React.Fragment>
								<ProjectGrid projects={renderData}
								             activeProject={activeProject}
								             onClick={handleProjectSelection}
								             userProjects={userProjects}/>
								<div className={"flex align-center justify-center mt-6"}>
									<button className="btn btn-sm border border-primary text-primary rounded-md"
									        onClick={() => handleRefresh()}>
										Refresh Access
									</button>
								</div>
							</React.Fragment>
						
					}
					
					{loading && <Spinner message={"loading"}/>}
					{/*{createProject &&*/}
					{/*    <CreateProjectLauncher*/}
					{/*        onLaunch={onLauncherComplete}*/}
					{/*        onCancel={onLauncherCancel}*/}
					{/*        type={"new"}/>*/}
					{/*}*/}
					{/*{toaster()}*/}
					{/*{showAlert && <ProjectAlert show={showAlert} setShow={setShowAlert} projects={projects}/>}*/}
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
		                    onClick={onProjectClicked}/>
	}
	
	function onLauncherComplete(message: string) {
		if (message === "success") {
			setToast({type: ToastType.Success, title: "Success", description: "Project Created Successfully"})
			setCreateProject(null);
		} else if (message === "error") {
			setToast({
				type: ToastType.Danger, title: "Error",
				description: "Error in Creating Project, please check the credentials"
			})
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

const ProjectGrid = ({projects, activeProject, onClick, userProjects}) => {
	return (
		<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
			{
				projects.map((project, index) =>
					<ProjectCard
						key={project.id}
						index={index}
						project={project}
						isActive={activeProject === project.id}
						hasAccess={userProjects?.[project.id]}
						onClick={onClick}/>)
				
			}
		</div>
	);
};

