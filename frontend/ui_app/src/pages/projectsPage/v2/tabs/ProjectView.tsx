import React, { useEffect, useState } from "react";
import { StoreNames, useStore } from "../../../../stores";
import Project, { UserRole } from "../../../../servers/asset_server/project.ts";
import {CircleUser, Calendar, Clock, FileText, Link, Edit, Info} from "lucide-react";
import { convertToCurrentTimeZone } from "../../../../utils";
import {ProjectForm} from "pages/projectsPage/v2/forms/ProjectForm.tsx";
import {InfoLabel} from "components/v2/InfoLabel.tsx";

interface BrowserProps {
	project: any;
}

export default function ProjectView(props: BrowserProps) {
	const [project, setProject] = useState<Project>(props.project);
	const [isEditMode, setIsEditMode] = useState<boolean>(false);
	
	const userStore = useStore(StoreNames.userStore);
	const isAdmin: boolean = userStore.get("projects")?.[props.project?.id]?.can_admin_project || true;
	
	
	if (!project) {
		return null;
	}
	
	const infoItems = [
		{ label: "Project Name", value: project.name, icon: <FileText className="size-4" /> },
		{ label: "Project title", value: project.title, icon: <FileText className="size-4" /> },
		{ label: "Project ID", value: project.id, icon: <Info className="size-4" /> },
		{ label: "Created By", value: project.created_by, icon: <CircleUser className="size-4" /> },
		{ label: "Created At", value: convertToCurrentTimeZone(project.created_at, "date"), icon: <Calendar className="size-4" /> },
		{ label: "Last Updated", value: convertToCurrentTimeZone(project.modified_at, "date"), icon: <Clock className="size-4" /> },
	];
	
	const handleProjectUpdate = (data) => {
		setProject(new Project(data));
		setIsEditMode(false)
	}
	
	return (
		<div className="bg-base-100">
			<div className="flex justify-between mb-4">
				<div className="text-lg text-neutral mb-6 font-semibold">Project Information</div>
				{isAdmin && !isEditMode &&(
					<button
						onClick={() => setIsEditMode(prevState => !prevState)}
						className={'btn btn-secondary btn-sm rounded-md'}>
						Edit Project
						<Edit className="size-4"/>
					</button>
				)}
			</div>
			<div className="border border-base-300 rounded-md overflow-hidden mb-6">
				{
					!isEditMode && (
						<div className="p-6 space-y-8">
							<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
								{infoItems.map((item, index) => (
									<InfoLabel item={item} key={index}/>
								))}
							</div>
							<InfoLabel item={{label: "Status", value: project.status, isStatus: true}}/>
							<InfoLabel item={{label: "Storage Url", value: project.remote_url, isLink: true, icon: <Link className="size-3.5"/>}}/>
							<InfoLabel item={{label: "Description", value: project.description, icon: <FileText className="size-3.5"/>}}/>
						</div>
					)
				}
				{
					isEditMode && (
						<div className="p-6">
							<ProjectForm onSave={handleProjectUpdate}
							             onCancel={() => setIsEditMode(false)}
							             data={project}/>
						</div>
					)
				}
			</div>
		</div>
	);
}
