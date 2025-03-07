import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArtifactsIcon } from "../../components/icons/Icons";
import { CheckCircle, Lock, Trash, AlertTriangle, XCircle, Star } from 'lucide-react';
import CLASS_ICONS from "./ClassIcons";
import { CLASS_TYPE } from "../../components/assetClassBrowser";
import { AccessStatus } from "servers/base/accessStatus";
import { daysAgo } from "utils";
import { stringToDate } from "utils/dateUtils";

export interface AssetClassCardProps {
	item: any;
	routeGenerator: (item: any) => string;
	isFavorite?: boolean;
	onFavoriteClicked?: (item: any) => void;
}

const container = "bg-white p-4 border border-base-300 rounded-lg hover:shadow-md transition duration-150 ease-in-out cursor-pointer flex flex-col group";

const getStatusConfig = (status: number) => {
	switch (status) {
		case AccessStatus.PUBLIC.value:
			return { icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-100', label: 'Public' };
		case AccessStatus.PRIVATE.value:
			return { icon: Lock, color: 'text-blue-500', bgColor: 'bg-blue-100', label: 'Private' };
		case AccessStatus.DELETED.value:
			return { icon: Trash, color: 'text-red-500', bgColor: 'bg-red-100', label: 'Deleted' };
		case AccessStatus.DEPRECATED.value:
			return { icon: AlertTriangle, color: 'text-orange-500', bgColor: 'bg-yellow-100', label: 'Deprecated' };
		case AccessStatus.OBSOLETE.value:
			return { icon: XCircle, color: 'text-red-500', bgColor: 'bg-gray-100', label: 'Obsolete' };
		default:
			return { icon: CheckCircle, color: 'text-gray-500', bgColor: 'bg-gray-100', label: 'Unknown' };
	}
};

export const AssetClassCard: React.FC<AssetClassCardProps> = ({
	                                                              item,
	                                                              routeGenerator,
	                                                              isFavorite = false,
	                                                              onFavoriteClicked
                                                              }) => {
	const isObsolete = item.class_type === "obsolete" || item.description.includes("obsolete");
	const isDeprecated = item.class_type === "deprecated" || item.description.includes("deprecated");
	const badge = item.class_type === CLASS_TYPE.EXPERIMENTAL ? "experimental" : null;
	const Icon = CLASS_ICONS[item.class_type] || CLASS_ICONS["default"];
	const navigate = useNavigate();
	const onClick = () => navigate(routeGenerator(item));
	const badgeColor = isObsolete ? "bg-red-200 text-red-950" : isDeprecated ? "bg-yellow-200 text-yellow-950" : "bg-base-300 text-neutral-600";
	
	const status = item.status || AccessStatus.PUBLIC.value;
	const showStatusBadge = status !== AccessStatus.PUBLIC.value;
	const { icon: StatusIcon, color: statusColor, bgColor: statusBgColor, label: statusLabel } = getStatusConfig(status);
	
	const handleFavoriteClick = (e: React.MouseEvent) => {
		e.stopPropagation();
		onFavoriteClicked?.(item);
	};
	
	return (
		<div className={container}>
			<div className="flex items-start justify-between mb-2">
				<Link to={routeGenerator(item)} className="flex-grow min-w-0" onClick={onClick}>
					<div className="flex items-center">
						<Icon className="flex-shrink-0 size-3.5 mr-4"/>
						<h3 className="text-md font-semibold text-neutral-600 hover:text-primary hover:underline transition-colors duration-150 truncate">
							{/* {item.title.normalize(" ").toTitleCase() || item.title} */}
							{item.title}
						</h3>
					</div>
				</Link>
				<div className="flex items-center gap-2">
					<button
						onClick={handleFavoriteClick}
						className={`p-1 rounded-md hover:bg-neutral-100 transition-colors duration-150 opacity-0 group-hover:opacity-100 ${isFavorite ? 'opacity-100' : ''}`}
						title={isFavorite ? "Remove from favorites" : "Add to favorites"}
					>
						<Star
							className={`size-4 ${isFavorite ? 'text-orange-400 fill-orange-400' : 'text-neutral-400'}`}
						/>
					</button>
					{showStatusBadge && (
						<div className={`inline-flex items-center px-2.5 py-1 rounded-md text-[10px] font-medium ${statusColor} ${statusBgColor}`}>
							<StatusIcon className="size-3 mr-2" />
							{statusLabel}
						</div>
					)}
					{badge && (
						<span className={`px-2 py-0.5 text-[10px] flex-shrink-0 ${badgeColor} rounded-sm whitespace-nowrap`}>
                            {badge}
                        </span>
					)}
				</div>
			</div>
			<p className="text-neutral-600 text-xs mb-2 ml-8 flex-grow truncate overflow-hidden whitespace-nowrap">
				{item.description}
			</p>
			<div className="text-xs text-neutral-400 ml-8 flex gap-2 items-center mt-auto">
				<ArtifactsIcon className="size-3"/>
				<p className="mr-4">assets: {item.counter}</p>
				{/* {item.modified_at && (
					<p className="mr-4">last modified: {daysAgo(stringToDate(item.modified_at))} days ago</p>
				)} */}
			</div>
		</div>
	);
}
