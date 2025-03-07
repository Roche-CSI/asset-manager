import React, { useState } from "react";
import { Link } from "react-router-dom";
import { FileText, UserCircle2, Tag, Edit, Trash2, Menu, Ban, Eye, Play } from "lucide-react";
import { TemplateData } from "../../../servers/asset_server/template.ts";

interface TemplateCardProps {
	item: TemplateData;
	onAction: (action: string, item: TemplateData) => void;
}

const ACTIONS = [
	{ name: "Edit", icon: Edit },
	{ name: "Delete", icon: Trash2 },
	{ name: "Apply", icon: Play },
	{ name: "Deprecate", icon: Ban }
];

const TemplateCard: React.FC<TemplateCardProps> = ({ item, onAction }) => {
	const [isDropdownOpen, setIsDropdownOpen] = useState(false);
	
	const handleAction = (action: string) => {
		setIsDropdownOpen(false);
		onAction(action.toLowerCase(), item);
	};
	
	return (
		<div
			className="bg-white border border-gray-200 rounded-lg transition duration-150 ease-in-out w-96 hover:shadow-md group">
			<div className="flex flex-col space-y-4 p-4">
				<div className="flex items-center justify-between">
					<div className="truncate flex-1">
						<div className="flex space-x-8 justify-between">
							<span>{item.title || item.name}</span>
							<button
								onClick={() => setIsDropdownOpen(!isDropdownOpen)}
								className="p-1 rounded transition-opacity duration-200 hover:bg-gray-100"
							>
								<Menu className="size-4"/>
							</button>
						</div>
						<div className="flex space-x-8">
							<div className="flex items-center mt-1">
								<UserCircle2 className="size-3.5 mr-1 text-neutral-400"/>
								<span className="text-xs text-neutral-400">{item.created_by || 'Unknown'}</span>
							</div>
						</div>
					</div>
					<div className="flex items-center space-x-2">
						<div className="relative">
							{isDropdownOpen && (
								<div
									className="absolute right-0 mt-1 w-36 bg-white rounded-md shadow-lg z-10 border border-gray-200">
									<div className="py-1">
										{ACTIONS.map((action) => (
											<button
												key={action.name}
												onClick={() => handleAction(action.name)}
												className="flex items-center w-full px-4 py-2 text-xs text-gray-700 hover:bg-gray-100"
											>
												<action.icon className="size-3.5 mr-2"/>
												{action.name}
											</button>
										))}
									</div>
								</div>
							)}
						</div>
					</div>
				</div>
				
				<p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
				
				<div className="flex items-center space-x-4 text-xs text-gray-500 justify-between">
					<div className="flex items-center">
					</div>
				</div>
				
				<div className="flex items-center justify-between text-xs text-gray-500 pt-2">
					<span
						className={`px-3 py-1 text-[10px] font-semibold rounded-md ${item.is_active ? 'bg-green-100 text-green-600' : 'bg-red-50 text-red-600'}`}>
                      {item.is_active ? 'Active' : 'Inactive'}
                   </span>
					<button
						onClick={() => handleAction("preview")}
						className="btn btn-xs btn-secondary rounded"
					>
						<Eye className="size-3 mr-1"/>
						Preview
					</button>
				</div>
			</div>
		</div>
	);
};

export default TemplateCard;
