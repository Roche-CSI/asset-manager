import React from "react";
import {AssetClass} from "servers/asset_server";
import {FilePenLine, FilePlus2} from "lucide-react";

const MetaSchemaView: React.FC<{assetClass: AssetClass}> = ({assetClass}) => {
	const [editMode, setEditMode] = React.useState<boolean>(false);
	
	return (
		<div className="bg-base-100 w-full">
			<div className="flex justify-between mb-6">
				<div className="text-lg text-neutral font-semibold">Meta Schema</div>
				<div className="flex space-x-8 items-center">
					{
						!editMode && (
							<button
								className={`btn btn-sm btn-secondary rounded-md`}
								onClick={() => setEditMode(prevState => !prevState)}>
								Add Meta Schema
								<FilePlus2 className="size-4"/>
							</button>
						)
					}
				</div>
			</div>
			<div className="h-32 border border-base-300 rounded-md w-full">
				<div className="flex justify-center items-center h-full text-neutral-500">
					Meta Schema coming soon
				</div>
			</div>
		</div>
	);
}

export default MetaSchemaView;
