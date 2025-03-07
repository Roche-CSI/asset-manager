import React from 'react';
import { CheckCircle, Lock, Trash, AlertTriangle, XCircle } from 'lucide-react';
import { AccessStatus } from "servers/base/accessStatus";

export const getStatusConfig = (status) => {
	switch (status) {
		case AccessStatus.PUBLIC.value:
			return { icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-100', label: 'Public' };
		case AccessStatus.PRIVATE.value:
			return { icon: Lock, color: 'text-blue-500', bgColor: 'bg-blue-100', label: 'Private' };
		case AccessStatus.DELETED.value:
			return { icon: Trash, color: 'text-red-500', bgColor: 'bg-red-100', label: 'Deleted' };
		case AccessStatus.DEPRECATED.value:
			return { icon: AlertTriangle, color: 'text-yellow-500', bgColor: 'bg-yellow-100', label: 'Deprecated' };
		case AccessStatus.OBSOLETE.value:
			return { icon: XCircle, color: 'text-red-500', bgColor: 'bg-gray-100', label: 'Obsolete' };
		default:
			return { icon: CheckCircle, color: 'text-gray-500', bgColor: 'bg-gray-100', label: 'Unknown' };
	}
};


const StatusBadge = ({ status }) => {
	const { icon: Icon, color, bgColor, label } = getStatusConfig(status);
	return (
		<div className={`w-32 inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${color}`}>
			<Icon className="size-4 mr-2" />
			{label}
		</div>
	);
};

export default StatusBadge;
