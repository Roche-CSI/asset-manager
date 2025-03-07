import React, { useState, useEffect } from 'react';
import {
	Tag,
	FileText,
	Type,
	Hash,
	User,
	Calendar,
	GitBranch,
	Edit,
	Info,
	CircleUser,
	Clock,
	Anchor,
	CalendarRange
} from 'lucide-react';
import { AssetInterface, Asset } from "../../../servers/asset_server";
import { AssetForm } from "../forms/AssetForm";
import {convertToCurrentTimeZone, isEmptyObject} from "../../../utils";
import {StoreNames, useStore} from "stores";
import {InfoLabel} from "../../../components/v2/InfoLabel.tsx";
import { AssetPhase } from "../../../servers/asset_server/assetPhase";

interface AssetInfoViewProps {
	asset: AssetInterface;
	assetClassName: string;
	setAsset: (asset: Asset) => void;
}

const AssetInfoView: React.FC<AssetInfoViewProps> = ({ asset, assetClassName, setAsset }) => {
	const assetStore = useStore(StoreNames.assetStore);
	const userStore = useStore(StoreNames.userStore);
	const [isEditing, setIsEditing] = useState(false);
	const [assetData, setAssetData] = useState<AssetInterface>(asset);
	
	const toggleEdit = () => {
		setIsEditing(prevState => !prevState);
	}
	
	const handleCancel = () => {
		setIsEditing(false);
	};
	
	const onAssetUpdate = (formData: Partial<AssetInterface>) => {
		const newAsset: Asset = new Asset(formData);
		setAssetData(new Asset(formData));
		let assetName = Asset.getName(assetClassName, asset.seq_id);
		assetStore.set(assetName, newAsset);
		setAsset(newAsset);
		setIsEditing(false);
		assetStore.didFullUpdate = false; //force update list
	}
	
	const renderEditForm = () => {
		return (
			<div className="bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md">
				<AssetForm asset={assetData} onSave={onAssetUpdate} onCancel={handleCancel} action={"edit"}/>
			</div>
		);
	}
	
	const infoItems = [
		{ label: "Asset title", value: assetData.title, icon: <FileText className="size-4" /> },
		{ label: "Asset handle", value: `${assetClassName}/${assetData.seq_id}`, icon: <FileText className="size-4" /> },
		{ label: "Asset ID", value: assetData.id, icon: <Info className="size-4" /> },
		{ label: "Alias", value: assetData.alias, icon: <Anchor className="size-4" /> },
		{ label: "Created By", value: assetData.created_by, icon: <CircleUser className="size-4" /> },
		{ label: "Created At", value: convertToCurrentTimeZone(assetData.created_at, "date"), icon: <Calendar className="size-4" /> },
		{ label: "Status", value: assetData.status, isStatus: true },
		{ label: "Last Updated", value: convertToCurrentTimeZone(assetData.modified_at, "date"), icon: <Clock className="size-4" /> },
		{ label: "Phase", value: AssetPhase.getLabelByValue(assetData.phase), icon: <CalendarRange className="size-4" /> },
		{ label: "Attributes", value: JSON.stringify(assetData?.attributes), icon: <FileText className="size-4" /> },
	];
	
	const renderViewMode = () => (
		<div className="bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md">
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
				{infoItems.map((item, index) => (
					<InfoLabel item={item} key={index}/>
				))}
			</div>
			<div className="p-4">
				<h3 className="font-semibold text-gray-700 mb-3 flex items-center text-sm">
					<FileText className="w-3 h-3 mr-2"/>
					Description
				</h3>
				<p className="text-neutral-600 whitespace-pre-wrap pl-4 text-sm">
					{assetData.description || "No description available."}
				</p>
			</div>
		</div>
	);
	
	return (
		<div className="w-full space-y-6 mb-6 mt-6">
			<div className="flex items-center justify-between">
				<div className="flex space-x-4">
                    <span className="text-lg text-neutral font-semibold">
                        Asset Information
                    </span>
				</div>
				<button
					className={`btn btn-sm btn-secondary rounded-md ${isEditing ? "hidden" : ""}`}
					onClick={toggleEdit}>
					Edit
					<Edit className="size-4"/>
				</button>
			</div>
			{isEditing ? renderEditForm() : renderViewMode()}
		</div>
	);
};

export default AssetInfoView;
