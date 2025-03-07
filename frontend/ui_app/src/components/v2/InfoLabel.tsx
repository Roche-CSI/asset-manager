import React from "react";
import {getStatusConfig} from "components/statusBadge/StatusBadge.tsx";

interface InfoLabelItem {
	label: string;
	value: string;
	icon?: React.ReactNode;
	isLink?: boolean;
	isStatus?: boolean;
}

interface InfoLabelProps {
	item: InfoLabelItem;
}

export const InfoLabel: React.FC<InfoLabelProps> = ({ item }) => {
	if (item.isStatus) {
		return <StatusInfoLabel item={item} />;
	}
	
	return (
		<div className="flex items-start space-x-3">
			<div className="flex-shrink-0 mt-1">
				{item.icon}
			</div>
			<div>
				<div className="font-semibold text-sm text-neutral">{item.label}</div>
				<div className="mt-1 text-sm text-neutral-600">
					{item.isLink ? (
						<a href={item.value} target="_blank" rel="noopener noreferrer"
						   className="text-blue-600 hover:underline flex items-center">
							{item.value}
							<svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" viewBox="0 0 20 20"
							     fill="currentColor">
								<path
									d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"/>
								<path
									d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
							</svg>
						</a>
					) : (
						item.value
					)}
				</div>
			</div>
		</div>
	);
};

const StatusInfoLabel: React.FC<InfoLabelProps> = ({ item }) => {
	const statusConfig = getStatusConfig(item.value);
	return (
		<div className="">
			<div className="flex items-start">
							<span className="p-0.5">
								<statusConfig.icon className={`size-4 ${statusConfig.color}`}/>
							</span>
				<div className="text-neutral-500 rounded-sm px-2 text-xs block">
					<div className={`text-sm font-medium ${statusConfig.color}`}>{statusConfig.label}</div>
				</div>
			</div>
		</div>
	)
}
