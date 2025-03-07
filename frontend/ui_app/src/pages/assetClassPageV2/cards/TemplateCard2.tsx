import React, {useState} from 'react';
import {
	Ban,
	Edit,
	Eye, FileBox,
	MoreVertical,
	Play,
	Trash2,
	UserCircle2
} from 'lucide-react';
import {TemplateData} from "../../../servers/asset_server/template";
import {useNavigate} from "react-router-dom";

interface TemplateCardProps {
	item: TemplateData;
	projectId: string;
	assetClassName: string;
	onAction: (action: string, item: TemplateData) => void;
}

const ACTIONS = [
	{name: "Edit", icon: Edit},
	{name: "Delete", icon: Trash2},
	{name: "Apply", icon: Play},
	{name: "Deprecate", icon: Ban}
];

const TemplateCard2: React.FC<TemplateCardProps> = ({item, onAction, projectId, assetClassName}) => {
	const [isActionMenuOpen, setIsActionMenuOpen] = useState(false);
	const navigate = useNavigate();
	
	const handleAction = (action: string) => {
		switch (action.toLowerCase()) {
			case "edit":
				onAction("edit", item);
				break;
			case "delete":
				onAction("delete", item);
				break;
			case "preview":
				navigate(`/templates/${item.id}?project_id=${projectId}&asset_class=${assetClassName}&tab=templates`);
				break;
			case "apply":
				onAction("apply", item);
				break;
			case "deprecate":
				onAction("deprecate", item);
				break;
			default:
				break;
		}
	}
	
	return (
		<div className="w-96 min-h-48 bg-white rounded-lg border border-base-300 overflow-hidden hover:shadow-md">
			{/* Header */}
			<div className="h-32 bg-base-200 p-6">
				<div className="relative">
					<div className="flex justify-between items-start">
						<h2 className="text-gray-800 text-lg font-semibold">
							<span>{item.title || item.name}</span>
						</h2>
						<button
							className="w-6 h-6 rounded-full border border-neutral-400 flex items-center justify-center"
							onClick={() => setIsActionMenuOpen(prevState => !prevState)}>
							<MoreVertical size={16} className="text-neutral-400"/>
						</button>
					</div>
					{isActionMenuOpen && (
						<div
							className="absolute right-0 mt-1 w-[120px] bg-white rounded-md shadow-lg z-10 border border-gray-200">
							<div className="py-1">
								{ACTIONS.map((action) => (
									<button
										key={action.name}
										onClick={() => handleAction(action.name)}
										className="btn btn-xs btn-ghost font-normal w-full flex justify-start text-gray-700 hover:bg-gray-100"
									>
										<action.icon className="size-3 mr-2"/>
										{action.name}
									</button>
								))}
							</div>
						</div>
					)}
				</div>
				<div className="mt-1 flex items-center text-neutral-800">
					<div className="flex space-x-8">
						<div className="flex items-center mt-1">
							<UserCircle2 className="w-3.5 h-3.5 mr-1"/>
							<span className="text-xs">{item.created_by || 'Unknown'}</span>
						</div>
						<div className="flex items-center mt-1">
							<FileBox className="w-3.5 h-3.5 mr-1"/>
							<span className="text-xs">{item.category || "asset"}</span>
						</div>
					</div>
				</div>
				<div className="flex items-center justify-start space-x-2 text-xs text-gray-500 pt-4">
					<button
						onClick={() => handleAction("preview")}
						className="btn btn-xs btn-secondary rounded"
					>
						<Eye className="w-3 h-3 mr-1"/>
						Preview
					</button>
				</div>
			</div>
			<div className="p-4 flex justify-between items-center">
				<p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
			</div>
		</div>
	);
};

export default TemplateCard2;
