import React, {useEffect, useState} from "react";
import {MarkdownEditor} from "components/markDownEditor";
import {FilePenLine, FilePlus} from "lucide-react";
import {ProjectReadMeForm} from "pages/projectsPage/v2/forms/ProjectReadMeForm";
import {Project} from "servers/asset_server";


const ReadMeView: React.FC<{ project: Project }> = ({project}) => {
	const [editMode, setEditMode] = React.useState<boolean>(false);
	const [readMeContent, setReadMeContent] = useState("")
	
	useEffect(() => {
		setReadMeContent(project.readme)
	}, [project.readme]);
	
	const onReadMeUpdate = (content) => {
		setReadMeContent(content)
		setEditMode(false);
	}
	
	const onUpdateCancel = () => {
		setEditMode(false);
	}
	
	return (
		<div className="bg-base-100 w-full">
			<div className="mb-6 flex justify-between w-full">
				<span
					className="text-lg text-neutral font-semibold">{editMode ? "Edit" : ""} ReadMe For {project.title || project.name}</span>
				<div className="flex space-x-8 items-center">
					{
						!editMode && (
							<button
								className={`btn btn-sm btn-secondary rounded-md`}
								onClick={() => setEditMode(prevState => !prevState)}>
								{readMeContent ? "Edit" : "Add"}
								<FilePenLine className="size-4"/>
							</button>
						)
					}
				</div>
			</div>
			<div className="border border-base-300 rounded-md mb-6">
				{
					editMode &&
                    <ProjectReadMeForm onSave={onReadMeUpdate}
                                onCancel={onUpdateCancel}
                                project={project}
                                initialContent={readMeContent}
                    />
				}
				{
					!editMode && readMeContent && <MarkdownEditor mode={editMode ? "edit" : "preview"}
                                                                  showTabs={false}
                                                                  mdContent={readMeContent}/>}
				{
					!editMode && !readMeContent &&
                    <div className="h-32">
                        <div className="flex justify-center items-center h-full text-neutral-500">
                            No ReadMe content available
                        </div>
                    </div>
				}
			</div>
		</div>
	);
}

export default ReadMeView;
