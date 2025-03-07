import React from 'react';
import {
	Tag,
	Link,
	FileText,
	Type,
	AlertTriangle,
	Box,
	Trash2,
	CheckCircle,
	Clock,
	AlertCircle,
	Anchor
} from 'lucide-react';

const getStatusConfig = (status) => {
	const configs = {
		available: {
			color: 'bg-emerald-100 text-emerald-700 border-emerald-200',
			icon: <CheckCircle className="w-4 h-4 text-emerald-500 mr-2" />
		},
		scheduled: {
			color: 'bg-blue-100 text-blue-700 border-blue-200',
			icon: <Clock className="w-4 h-4 text-blue-500 mr-2" />
		},
		deprecated: {
			color: 'bg-rose-100 text-rose-700 border-rose-200',
			icon: <AlertCircle className="w-4 h-4 text-rose-500 mr-2" />
		}
	};
	return configs[status.toLowerCase()] || {
		color: 'bg-gray-100 text-gray-700 border-gray-200',
		icon: <AlertCircle className="w-4 h-4 text-gray-400 mr-2" />
	};
};

const getImportanceConfig = (importance) => {
	const configs = {
		critical: {
			color: 'text-rose-500',
			label: 'Critical Priority'
		},
		high: {
			color: 'text-amber-500',
			label: 'High Priority'
		},
		medium: {
			color: 'text-yellow-500',
			label: 'Medium Priority'
		},
		low: {
			color: 'text-blue-500',
			label: 'Low Priority'
		}
	};
	return configs[importance.toLowerCase()] || {
		color: 'text-gray-500',
		label: 'Priority Level'
	};
};

const getEventTypeIcon = (type) => {
	const icons = {
		delete: <Trash2 className="w-4 h-4 text-rose-400" />,
		create: <Box className="w-4 h-4 text-emerald-400" />,
		update: <FileText className="w-4 h-4 text-blue-400" />
	};
	return icons[type.toLowerCase()] || <Type className="w-4 h-4 text-gray-400" />;
};

const getEventColor = (type: string) => {
	const colors = {
		delete: "text-rose-400",
		create: "text-emerald-400",
		update: "text-blue-400"
	};
	const color = colors[type.toLowerCase()] || 'text-gray-500'
	return colors;
};

export const WebhookCard = ({ event }) => {
	const statusConfig = getStatusConfig(event.attributes.status);
	const importanceConfig = getImportanceConfig(event.attributes.importance);
	
	return (
		<div className="w-full max-w-md rounded-lg border border-base-300 bg-white/50 backdrop-blur-sm overflow-hidden hover:shadow-lg transition-all duration-300">
			{/* Header */}
			<div className="p-6">
				<div className="flex items-center justify-between mb-4">
					<h3 className="text-md font-semibold text-gray-800 truncate">
						{event.title || event.name}
					</h3>
				</div>
				
				{/* Description */}
				<p className="text-sm text-gray-600 mb-2 line-clamp-2 h-12">{event.description}</p>
				
				{/* Details */}
				<div className="space-y-2">
					<div className="flex items-center text-xs text-gray-600">
						<Tag className="w-4 h-4 mr-2 text-gray-400"/>
						<span className="font-medium">{event.entity_type}:</span>
						<span className="ml-1 text-gray-700">{event.entity_id}</span>
					</div>
					
					<div className="flex items-center text-xs text-gray-600">
						<Link className="w-4 h-4 mr-2 text-gray-400"/>
						<span className="truncate">{event.webhook_url}</span>
					</div>
				</div>
			</div>
			
			{/* Footer */}
			<div className="px-6 py-2 border-t border-gray-100 bg-gray-50">
				<div className="flex items-center justify-between">
					<div className="flex items-center text-xs text-gray-600 py-1 rounded-full font-semibold">
						<span
							className="w-6 h-6 rounded-full bg-gray-200/80 p-1 flex items-center justify-center backdrop-blur-sm">
							<Anchor className="size-3.5 text-gray-400"/>
							{/*{getEventTypeIcon(event.event_type)}*/}
						</span>
						<span
							className={`ml-2 ${getEventColor(event.event_type)}}`}>{event.event_type.toUpperCase()}</span>
					</div>
					<div className={`px-3 py-1 rounded-full flex text-[10px] font-medium ${statusConfig.color}`}>
						<span className="mr-1">{statusConfig.icon}</span>
						{event.attributes.status}
					</div>
				</div>
			</div>
		</div>
	);
};

export default WebhookCard;
