import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { Calendar, UserCircle2, Folder, Box, Hash, Tag, Copy, Check, BarChart3,
	CheckCircle, Lock, Trash, AlertTriangle, XCircle } from "lucide-react";
import { convertToCurrentTimeZone } from "utils";
import { Asset } from "servers/asset_server";
import { formatBytes } from "utils/fileUtils.ts";
import { AccessStatus } from "servers/base/accessStatus";

interface AssetCardProps {
	item: Asset;
	className?: string;
}

const formatNumber = (num: number): string => {
	return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

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

const AssetCard: React.FC<AssetCardProps> = ({ item, className }) => {
	const size = item.getSize(true);
	const numFiles = item.getNumObjects(true);
	const [copied, setCopied] = React.useState(false);
	
	const handlePath = `${className}/${item.seq_id}`;
	
	const handleCopy = async () => {
		try {
			await navigator.clipboard.writeText(handlePath);
			setCopied(true);
			setTimeout(() => setCopied(false), 2000);
		} catch (err) {
			console.error('Failed to copy text:', err);
		}
	};
	
	const hasTemplate = item.attributes && item.attributes.template;
	const link = hasTemplate ? `${item.link}&template=${item.attributes.template}` : item.link;
	
	const status = item.status || AccessStatus.PUBLIC.value;
	const showStatusBadge = status !== AccessStatus.PUBLIC.value;
	const { icon: StatusIcon, color: statusColor, bgColor: statusBgColor, label: statusLabel } = getStatusConfig(status);
	
	return (
		<div className="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-all duration-300 overflow-hidden group">
			<div className="p-5">
				<div className="flex items-start justify-between mb-4">
					<div className="flex-grow mr-4">
						<div className="flex items-center flex-wrap gap-2">
							<RouterLink
								to={link}
								className="text-md font-semibold text-gray-800 hover:text-blue-600 hover:underline truncate block group-hover:text-blue-600 transition-colors duration-300"
							>
								{item.identifier}
							</RouterLink>
							{/* Dashboard Badge */}
							{hasTemplate && (
								<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 shadow-sm">
                                    <BarChart3 className="w-3.5 h-3.5 mr-1 stroke-blue-500" />
                                    Dashboard
                                </span>
							)}
							{/* Status Badge */}
							{showStatusBadge && (
								<span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${statusColor} ${statusBgColor}`}>
                                    <StatusIcon className="w-3.5 h-3.5 mr-1" />
									{statusLabel}
                                </span>
							)}
						</div>
						<p className="text-sm text-gray-600 line-clamp-2 mt-2 leading-relaxed h-12">
							{item.description}
						</p>
					</div>
				</div>
				
				{/* Handle & Alias Section */}
				<div className="space-y-3 mb-6 pb-6 border-b border-gray-100">
					<div className="flex items-center text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
						<Hash className="w-4 h-4 mr-2.5 text-gray-400 flex-shrink-0"/>
						<span className="font-medium text-gray-700 mr-2">Handle:</span>
						<span className="font-mono text-sm truncate">{handlePath}</span>
						<button
							onClick={handleCopy}
							className="ml-2 p-1.5 hover:bg-white rounded-md transition-colors group/copy"
							title="Copy handle"
						>
							{copied ? (
								<Check className="w-4 h-4 text-green-500" />
							) : (
								<Copy className="w-4 h-4 text-gray-400 group-hover/copy:text-gray-600" />
							)}
						</button>
					</div>
					<div className="flex items-center text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
						<Tag className="w-4 h-4 mr-2.5 text-gray-400 flex-shrink-0"/>
						<span className="font-medium text-gray-700 mr-2">Alias:</span>
						<span className="truncate">{item.alias}</span>
					</div>
				</div>
				
				<div className="flex items-center text-xs text-gray-500 flex-wrap gap-4">
					<div className="flex items-center bg-gray-50 px-3 py-1.5 rounded-full">
						<Box className="w-3.5 h-3.5 mr-1.5 text-gray-400"/>
						<span className="font-medium">
                            {size ? formatBytes(size) : 'size missing'}
                        </span>
					</div>
					<div className="flex items-center bg-gray-50 px-3 py-1.5 rounded-full">
						<Folder className="w-3.5 h-3.5 mr-1.5 text-gray-400"/>
						<span className="font-medium">
                            {numFiles
	                            ? `${formatNumber(numFiles)} file${numFiles !== 1 ? 's' : ''}`
	                            : 'count missing'}
                        </span>
					</div>
					<div className="flex items-center bg-gray-50 px-3 py-2 rounded-lg">
						<UserCircle2 className="w-4 h-4 mr-2 text-gray-400"/>
						<span className="text-sm font-medium text-gray-700 truncate">
                     {item.modified_by}
                   </span>
					</div>
					<div className="flex items-center bg-gray-50 px-3 py-1.5 rounded-full">
						<Calendar className="w-3.5 h-3.5 mr-1.5 text-gray-400"/>
						<span className="font-medium">
                            {convertToCurrentTimeZone(item.created_at, "date")}
                        </span>
					</div>
				</div>
			</div>
		</div>
	);
}

export default AssetCard;
