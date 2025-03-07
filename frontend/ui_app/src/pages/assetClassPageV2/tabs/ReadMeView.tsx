import React, {useEffect, useState} from "react";
import {MarkdownEditor} from "../../../components/markDownEditor";
import {AssetClass} from "../../../servers/asset_server";
import {FilePenLine, FilePlus} from "lucide-react";
import {ReadMeForm} from "pages/assetClassPageV2/forms/ReadmeForm.tsx";


const ReadMeView: React.FC<{ assetClass: AssetClass }> = ({assetClass}) => {
	const [editMode, setEditMode] = React.useState<boolean>(false);
	const [readMeContent, setReadMeContent] = useState("")
	
	useEffect(() => {
		setReadMeContent(assetClass.readme)
	}, [assetClass.readme]);
	
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
					className="text-lg text-neutral font-semibold">{editMode ? "Edit" : ""} ReadMe For {assetClass.title || assetClass.name}</span>
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
                    <ReadMeForm onSave={onReadMeUpdate}
                                onCancel={onUpdateCancel}
                                assetClass={assetClass}
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
