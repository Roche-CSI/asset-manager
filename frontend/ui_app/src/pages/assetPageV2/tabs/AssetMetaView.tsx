import React from "react";
import {Asset} from "../../../servers/asset_server";
import { Edit, FileJson2, FilePlus, Tag } from "lucide-react";
import MetaForm from "pages/assetPageV2/forms/MetaForm";
import TagForm from "pages/assetPageV2/forms/TagForm";
import { atomOneLight, CodeBlock } from "react-code-blocks";

interface AssetTagsSectionProps {
	asset: Asset;
	initialTags: string[];
	onChange: (tags: string[]) => void;
}

const AssetTagsSection: React.FC<AssetTagsSectionProps> = ({ asset, initialTags, onChange }) => {
	const [editMode, setEditMode] = React.useState<boolean>(false);
	const [tags, setTags] = React.useState<string[]>(initialTags);
	
	const handleSave = (data: { tags: string[] }) => {
		setTags(data.tags);
		onChange(data.tags);
		setEditMode(false);
	};
	
	const handleCancel = () => {
		setEditMode(false);
	};
	
	return (
		<div className="h-full w-1/4 pl-16">
			<div className="flex items-center gap-2 mb-4">
				<Tag className="size-4" />
				<div className="text-lg text-neutral font-semibold">Tags</div>
				{!editMode && (
					<button
						className="btn btn-sm btn-ghost text-secondary"
						onClick={() => setEditMode(true)}
					>
						{tags.length > 0 ? (
							<Edit className="size-4" />
						) : (
							<FilePlus className="size-4" />
						)}
					</button>
				)}
			</div>
			
			{!editMode && tags && tags.length > 0 ? (
				<div className="flex flex-wrap gap-2">
					{tags.map((tag: string, index: number) => (
						<div
							key={index}
							className="px-3 py-1 bg-base-200 text-neutral rounded-full text-xs"
						>
							{String(tag)}
						</div>
					))}
				</div>
			) : !editMode ? (
				<div className="h-full border border-base-300 rounded-md w-full">
					<div className="flex justify-center items-center h-full text-neutral-500">
						No Tags available
					</div>
				</div>
			) : (
				<div className="p-6 border border-base-300 rounded-md">
					<TagForm
						asset={asset}
						tags={tags}
						onSave={handleSave}
						onCancel={handleCancel}
					/>
				</div>
			)}
		</div>
	);
};

interface AssetMetaSectionProps {
	asset: Asset;
	initialMetaData: any;
	onChange: (metadata: any) => void;
}

const AssetMetaSection: React.FC<AssetMetaSectionProps> = ({
	                                                           asset,
	                                                           initialMetaData,
	                                                           onChange,
                                                           }) => {
	const [editMode, setEditMode] = React.useState<boolean>(false);
	const [metaData, setMetaData] = React.useState<any>(initialMetaData);
	
	const handleSave = (data: { metadata: any }) => {
		setMetaData(data.metadata);
		onChange(data.metadata);
		setEditMode(false);
	};
	
	const handleCancel = () => {
		setEditMode(false);
	};
	
	return (
		<div className="h-full w-3/4 pr-6">
			<div className="flex items-center gap-2 mb-4">
				<div className="flex items-center gap-2">
					<FileJson2 className="size-4" />
					<div className="text-lg text-neutral font-semibold">Metadata</div>
				</div>
				{!editMode && (
					<button
						className="btn btn-sm btn-ghost text-secondary"
						onClick={() => setEditMode(true)}
					>
						{Object.keys(metaData).length > 0 ? (
							<Edit className="size-4" />
						) : (
							<FilePlus className="size-4" />
						)}
					</button>
				)}
			</div>
			
			{!editMode && Object.keys(metaData).length > 0 ? (
				<div className="border border-base-300 rounded-md">
					<CodeBlock
						text={JSON.stringify(metaData, null, 8)}
						language={"json"}
						showLineNumbers={true}
						theme={atomOneLight}
						customStyle={{
							fontSize: "0.75rem",
							padding: "0.5rem",
						}}
					/>
				</div>
			) : !editMode ? (
				<div className="h-full border border-base-300 rounded-md w-full">
					<div className="flex justify-center items-center h-full text-neutral-500">
						No Metadata available
					</div>
				</div>
			) : (
				<div className="p-6 border border-base-300 rounded-md">
					<MetaForm
						asset={asset}
						metaData={metaData}
						onSave={handleSave}
						onCancel={handleCancel}
					/>
				</div>
			)}
		</div>
	);
};

const AssetMetaView: React.FC<{ asset: Asset }> = ({ asset }) => {
	const [metaData, setMetaData] = React.useState<any>(asset.metadata || {});
	const [tags, setTags] = React.useState<string[]>(
		Array.isArray(asset.tags) ? asset.tags : []
	);
	
	return (
		<div className="bg-base-100 w-full space-y-6">
			<div className="flex flex-col md:flex-row w-full mt-6">
				<AssetMetaSection
					asset={asset}
					initialMetaData={metaData}
					onChange={setMetaData}
				/>
				<AssetTagsSection
					asset={asset}
					initialTags={tags}
					onChange={setTags}
				/>
			</div>
		</div>
	);
};

export default AssetMetaView;
