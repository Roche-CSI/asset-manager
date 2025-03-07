import React, { useState } from 'react';
import {
	Database,
	FileKey,
	Settings,
	ChevronDown,
	ChevronUp,
	Trash2,
	Edit,
	Text,
	EllipsisVertical,
	AlertCircle, Calendar, UserCircle
} from 'lucide-react';
import { BucketData } from "../../../../servers/asset_server/bucket.ts";
import {stringToDate} from "utils/dateUtils.ts";

interface BucketCardProps {
	bucket: BucketData;
	onDelete: (bucket: BucketData) => void;
	onEdit: (bucket: BucketData) => void;
	adminUser: any;
	project_name: string;
}

const ACTIONS = [
	{ name: "Edit", icon: Edit },
	{ name: "Delete", icon: Trash2 },
];

const ButtonSpinner: React.FC<{ action: "create" | "edit" | "delete" }> = ({ action }) => {
	return (
		<span className="flex items-center">
      <svg className="w-5 h-5 mr-2 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
			{action === "create" ? "Creating..." : action === "edit" ? "Updating..." : "Deleting..."}
    </span>
	)
}

const CardStatusMessage: React.FC<{ message: string, type: 'success' | 'error' | 'info' }> = ({ message, type }) => {
	return (
		<div className={`p-4 rounded-md ${type === 'error' ? 'bg-red-50 text-red-700' : type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
			<p className="text-sm font-medium">{message}</p>
		</div>
	)
}

const PostSaveOptions: React.FC<{ message: string, onClose: () => void }> = ({ message, onClose }) => {
	return (
		<div className="space-y-4">
			<div className="p-4 rounded-md bg-green-50 text-green-700">
				<p className="text-sm font-medium">{message}</p>
			</div>
			<button
				onClick={onClose}
				className="btn btn-sm btn-secondary rounded">
				Close
			</button>
		</div>
	)
}

const MockBucketService = {
	deleteBucket: (bucketId: number, adminUsername: string, projectName: string) => {
		return new Promise((resolve, reject) => {
			setTimeout(() => {
				if (Math.random() < 0.8) {
					resolve({ success: true, message: "Bucket deleted successfully" });
				} else {
					reject(new Error("Failed to delete bucket"));
				}
			}, 2000);
		});
	}
};

const BucketCard: React.FC<BucketCardProps> = ({ bucket, onDelete, onEdit, adminUser, project_name }) => {
	const [isExpanded, setIsExpanded] = useState(false);
	const [isDropdownOpen, setIsDropdownOpen] = useState(false);
	const [isConfirming, setIsConfirming] = useState(false);
	const [isDeleting, setIsDeleting] = useState(false);
	const [deleteStatus, setDeleteStatus] = useState<'idle' | 'success' | 'error'>('idle');
	const [statusMessage, setStatusMessage] = useState('');
	
	const toggleExpand = () => {
		setIsExpanded(!isExpanded);
	};
	
	const handleDeleteClick = () => {
		setIsConfirming(true);
	};
	
	const handleClose = () => {
		onDelete(bucket);
	};
	
	const handleConfirmDelete = () => {
		setIsDeleting(true);
		MockBucketService.deleteBucket(bucket.id, adminUser.username, project_name)
			.then((data: any) => {
				console.log("Bucket deleted:", data);
				setTimeout(() => {
					setIsConfirming(false);
					setIsDeleting(false);
					setDeleteStatus('success');
					setStatusMessage('Bucket successfully deleted from the project.');
				}, 2000);
			}).catch((error: any) => {
			console.error("Error deleting bucket:", error);
			setDeleteStatus('error');
			setStatusMessage('Failed to delete bucket. Please try again.');
			setIsDeleting(false);
		});
	};
	
	const handleCancelDelete = () => {
		setIsConfirming(false);
		setDeleteStatus('idle');
	};
	
	const handleAction = (action: string) => {
		setIsDropdownOpen(false);
		if (action.toLowerCase() === 'delete') {
			handleDeleteClick();
		} else if (action.toLowerCase() === 'edit') {
			onEdit(bucket);
		}
	};
	
	return (
		<div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-300 group">
			<div className="p-4">
				<div className="flex items-center justify-between mb-4">
					<div className="flex items-center justify-start space-x-3">
						<div className="bg-blue-100 p-1 rounded-lg">
							<Database className="size-5 text-blue-600" />
						</div>
						<h2 className="text-md font-semibold text-gray-800 truncate">{bucket.title}</h2>
					</div>
					{!isConfirming && (
						<div className="relative">
							<button
								onClick={() => setIsDropdownOpen(!isDropdownOpen)}
								className="p-2 rounded-full transition-colors duration-200 hover:bg-gray-100"
							>
								<EllipsisVertical className="size-5 text-gray-600" />
							</button>
							{isDropdownOpen && (
								<div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
									<div className="py-1">
										{ACTIONS.map((action) => (
											<button
												key={action.name}
												onClick={() => handleAction(action.name)}
												className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
											>
												<action.icon className="size-4 mr-3" />
												{action.name}
											</button>
										))}
									</div>
								</div>
							)}
						</div>
					)}
				</div>
				
				{isConfirming ? (
					<React.Fragment>
						<div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-4 mt-2">
							<div className="flex items-center mb-2">
								<AlertCircle className="w-4 h-4 text-yellow-400 mr-2"/>
								<p className="font-medium text-xs text-yellow-700">Confirm Removal</p>
							</div>
							<p className="text-yellow-700 text-xs mb-6">Are you sure you want to remove this bucket from
								the project?
							</p>
							<div className="flex justify-start space-x-2">
								<button
									onClick={handleCancelDelete}
									disabled={isDeleting}
									className="btn btn-xs bg-base-300 border border-neutral-300 text-neutral-800 rounded">
									Cancel
								</button>
								<button
									onClick={handleConfirmDelete}
									disabled={isDeleting}
									className="btn btn-xs bg-red-500 border border-red-500 hover:bg-red-600 text-white rounded">
									{isDeleting ? <ButtonSpinner action="delete"/> : "Delete"}
								</button>
							</div>
						</div>
						{
							!isDeleting && ["error", "info"].includes(deleteStatus) &&
                            <CardStatusMessage message={statusMessage}
                                               type={deleteStatus === 'error' ? 'error' : 'info'}/>
						}
					</React.Fragment>
				) : deleteStatus === 'success' ? (
					<PostSaveOptions message={statusMessage} onClose={handleClose} />
				) : (
					<React.Fragment>
						<div className="space-y-3 text-sm text-gray-600 mb-6">
							<p className="line-clamp-3 h-16">
								{bucket.description}
							</p>
							<div className="flex items-center space-x-4 text-xs">
								<div className="flex items-center">
									<Calendar className="size-4 mr-2 text-gray-400" />
									<span>{stringToDate(bucket.created_at, bucket.created_at).toLocaleDateString()}</span>
								</div>
								<div className="flex items-center">
									<UserCircle className="size-4 mr-2 text-gray-400" />
									<span>{bucket.created_by}</span>
								</div>
							</div>
						</div>
						
						<div className="flex items-center space-x-2 w-full border-t border-base-300 pt-4">
							<span className={`px-2 py-1 text-xs font-medium rounded-md ${bucket.is_primary ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}`}>
								{bucket.is_primary ? 'Primary' : 'Proxy'}
							</span>
							<span className={`px-2 py-1 text-xs font-medium rounded-md ${
								bucket.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
							}`}>
								{bucket.is_active ? 'Active' : 'Inactive'}
							</span>
						</div>
					</React.Fragment>
				)}
			</div>
		</div>
	);
};

export default BucketCard;
