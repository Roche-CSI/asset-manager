import React, { useState } from 'react';
import { convertToCurrentTimeZone } from "../../utils";
import { MarkdownEditor } from "../../components/markDownEditor";

interface ProjectInfoCardProps {
	project: any;
}

const ProjectInfoCard: React.FC<ProjectInfoCardProps> = ({ project }) => {
	const [isReadmeExpanded, setIsReadmeExpanded] = useState(false);
	
	const infoItems = [
		{ label: "Project Name", value: project.name },
		{ label: "Project ID", value: project.id },
		{ label: "Created By", value: project.created_by },
		{ label: "Created At", value: convertToCurrentTimeZone(project.created_at, "date") },
		{ label: "Last Modified", value: convertToCurrentTimeZone(project.last_modified, "date") },
		{ label: "Description", value: project.description },
		{ label: "Remote URL", value: project.remote_url },
	];
	
	return (
		<div className="bg-white rounded-md border border-base-200 overflow-hidden">
			<div className="px-6 py-4 bg-gray-50 border-b border-base-200">
				<h3 className="text-lg font-semibold text-gray-800">Project Information</h3>
			</div>
			<div className="px-6 py-4">
				<dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
					{infoItems.map((item, index) => (
						<div key={index} className="sm:col-span-1">
							<dt className="text-sm font-medium text-gray-500">{item.label}</dt>
							<dd className="mt-1 text-sm text-gray-900">
								{item.label === "Remote URL" ? (
									<a href={item.value} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
										{item.value}
									</a>
								) : (
									item.value
								)}
							</dd>
						</div>
					))}
				</dl>
			</div>
			<div className="px-6 py-4 border-t border-base-200">
				<button
					onClick={() => setIsReadmeExpanded(!isReadmeExpanded)}
					className="btn-ghost font-bold flex items-center text-sm rounded-md p-1 hover:text-blue-800">
					<span className="mr-2">README.md</span>
					<svg
						className={`w-5 h-5 transform transition-transform duration-200 ${isReadmeExpanded ? 'rotate-180' : ''}`}
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
					</svg>
				</button>
				{isReadmeExpanded && (
					<div className="mt-4 bg-gray-50 p-4 rounded">
						<MarkdownEditor
							mode="preview"
							showTabs={false}
							mdContent={project.readme || "No README content available."}
						/>
					</div>
				)}
			</div>
		</div>
	);
};

export default ProjectInfoCard;
