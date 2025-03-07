import React, {useState} from 'react';
import {
	Tag,
	FileText,
	Hash,
	Type,
	Edit,
	UserCircle, Calendar, Info, CircleUser, Clock
} from 'lucide-react';
import {AssetClass} from "../../../servers/asset_server";
import {AssetClassForm} from "../forms/AssetClassForm";
import {InfoLabel} from "components/v2/InfoLabel";
import {convertToCurrentTimeZone} from "utils";
import {StoreNames, useStore} from "stores";

interface AssetClassViewProps {
	assetClass: AssetClass;
	setAssetClass: (assetClass: AssetClass) => void;
}

const AssetClassView: React.FC<AssetClassViewProps> = ({assetClass, setAssetClass}) => {
	const classIdStore = useStore(StoreNames.classIdStore);
	const classNameStore = useStore(StoreNames.classNameStore);
	const [isEditing, setIsEditing] = useState(false);
	const [classData, setClassData] = useState<AssetClass | null>(assetClass);
	
	const handleCancel = () => {
		setIsEditing(false);
	};
	
	const onAssetClassUpdate = (formData: any) => {
		const newClass: AssetClass = new AssetClass(formData);
		setClassData(newClass);
		classNameStore.set(assetClass.name, newClass);
		setAssetClass(newClass);
		setIsEditing(false);
		classIdStore.didFullUpdate = false; //force update class list
	}
	
	const renderEditForm = () => {
		const darkStyle = "dark:border-slate-800 dark:bg-slate-800 dark:text-white";
		return (
			<div className="bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md">
				<AssetClassForm assetClass={classData}
				                onSave={onAssetClassUpdate}
				                onCancel={handleCancel}
				                action={"edit"}/>
			</div>
		);
	}
	
	const infoItems = [
		{ label: "Collection Name", value: classData?.name, icon: <FileText className="size-4" /> },
		{ label: "Title", value: classData?.title, icon: <FileText className="size-4" /> },
		{ label: "ID", value: classData?.id, icon: <Info className="size-4" /> },
		{ label: "Created By", value: classData?.created_by, icon: <CircleUser className="size-4" /> },
		{ label: "Created At", value: convertToCurrentTimeZone(classData?.created_at, "date"), icon: <Calendar className="size-4" /> },
		{ label: "Last Updated", value: convertToCurrentTimeZone(classData?.modified_at, "date"), icon: <Clock className="size-4" /> },
		{ label: "Type", value: classData?.class_type || "general", icon: <Type className="size-4"/> },
	];
	
	const renderViewMode = () => {
		return (
			<div className="bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md flex flex-col">
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-6">
					{infoItems.map((item, index) => (
						<InfoLabel item={item} key={index}/>
					))}
				</div>
				<div className="">
					<InfoLabel item={{label: "Status", value: classData?.status, isStatus: true}}/>
				</div>
				<div className="mt-8">
					<h3 className="font-semibold text-gray-700 mb-3 flex items-center text-sm">
						<FileText className="size-4 text-neutral-400 mr-2"/>
						About
					</h3>
					<p className="text-neutral-600 whitespace-pre-wrap pl-6 text-sm">
						{classData?.description || "No description available."}
					</p>
				</div>
			</div>
		);
	}
	
	const title = classData?.title.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
	return (
		<div className="w-full space-y-6 mb-6">
			<div className="flex items-center justify-between">
				<div className="flex space-x-4">
					<span className="text-lg text-neutral font-semibold">
						{isEditing ? "Edit" : ""} {title}
					</span>
				</div>
				{
					!isEditing && (
						<button
							className="btn btn-sm btn-secondary rounded-md"
							onClick={() => setIsEditing(prevState => !prevState)}>
							Edit
							<Edit className="size-4"/>
						</button>
					)
				}
			</div>
			{isEditing ? renderEditForm() : renderViewMode()}
		</div>
	);
};

export default AssetClassView;
