import React, { useState } from "react";
import { Link } from "react-router-dom";
import { UserCircle2, Mail } from "lucide-react";
import DigitalAssetIcons from "pages/projectsPage/v2/DigitalAssetIcons.tsx";
import { StoreNames, useStore } from '../../../../stores';

interface CardProps {
	project: {
		id: string;
		name: string;
		title?: string;
		description: string;
		admin: {
			name: string;
			email: string;
		};
	};
	isActive: boolean;
	hasAccess: boolean;
	onClick: (id: string) => void;
	index: number;
}

const handleProjectLinkClick = (event: React.MouseEvent) => {
	event.stopPropagation();
};

const ProjectCard: React.FC<CardProps> = ({project, isActive, hasAccess, onClick, index}) => {
	const [isHovered, setIsHovered] = useState(false);
	const userStore = useStore(StoreNames.userStore);
	
	project.admin = {
		email: userStore.get('dashboard_settings')?.admin_email || "joe@gmail.com", 
		name: userStore.get('dashboard_settings')?.admin_name || "Joe"
	};
	
	return (
		<div
			key={project.id}
			className={`border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-gray-300 transition-colors ${
				isActive ? 'bg-base-200' : ''
			}`}
			onClick={() => onClick(project.id)}>
			<div className="flex space-x-4">
				<div className="size-8 border border-white rounded-md">
					<DigitalAssetIcons name={project.name} index={index}/>
				</div>
				<div className="w-full">
					<div className="flex justify-between items-start">
						<div className="flex flex-col">
							<Link to={`/project/${project.id}`} onClick={handleProjectLinkClick}>
								<h3 className="text-lg font-semibold hover:text-primary hover:underline">
									{project.title || project.name}
								</h3>
							</Link>
							<div className="flex items-center mt-1 space-x-2">
								{isActive && (
									<span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                               Active
                            </span>
								)}
								<span
									className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
										hasAccess ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'
									}`}
								>
                            {hasAccess ? 'Access' : 'Restricted'}
                         </span>
							</div>
						</div>
						<div>
							{isActive && (
								<Link
									to={`/assets?project_id=${project.id}`}
									className="btn btn-xs btn-primary rounded-md transition-colors"
									onClick={handleProjectLinkClick}
								>
									View Assets
								</Link>
							)}
						</div>
					</div>
					<p className="text-sm text-gray-600 mt-2">{project.description}</p>
					<div className="flex items-center mt-3 space-x-4 text-xs text-gray-400">
						<div className="flex items-center space-x-1">
							<UserCircle2 size={14} className="text-gray-400"/>
							<span>{project.admin.name}</span>
						</div>
						<div className="flex items-center space-x-1">
							<Mail size={14} className="text-gray-400"/>
							<span>{project.admin.email}</span>
						</div>
						<div
							className="px-2 py-0.5 bg-blue-100 text-primary text-[10px] rounded-full cursor-pointer transition-colors hover:bg-blue-200"
							onMouseEnter={() => setIsHovered(true)}
							onMouseLeave={() => setIsHovered(false)}
						>
							{isHovered ? 'copy' : 'admin'}
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default ProjectCard;
