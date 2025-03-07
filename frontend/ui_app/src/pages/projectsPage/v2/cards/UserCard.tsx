import React, {useState} from 'react';
import {Trash2, AlertCircle, Calendar, Edit, EllipsisVertical} from 'lucide-react';
import Project from "../../../../servers/asset_server/project.ts";
import {StringExt} from "utils/strUtils.ts";

interface CircularAvatarProps {
	username: string;
	size?: 'sm' | 'md' | 'lg' | 'xl';
	bgColor?: string;
	textColor?: string;
}

export const CircularAvatar: React.FC<CircularAvatarProps> = ({
	                                                       username,
	                                                       size = 'md',
	                                                       bgColor = "",
	                                                       textColor = 'text-white'
                                                       }) => {
	const sizeClasses = {
		sm: 'w-8 h-8 text-sm',
		md: 'w-12 h-12 text-lg',
		lg: 'w-16 h-16 text-xl',
		xl: 'w-20 h-20 text-2xl',
	};
	
	// Function to generate a random color based on the username
	const generateColor = (name: string) => {
		let hash = 0;
		for (let i = 0; i < name.length; i++) {
			hash = name.charCodeAt(i) + ((hash << 5) - hash);
		}
		const hue = hash % 360;
		return `hsl(${hue}, 70%, 50%)`;
	};
	const background = bgColor || generateColor(username);
	
	return (
		<div
			className={`flex items-center justify-center ${background} ${textColor} ${sizeClasses[size]}
			rounded-full shadow-md transition-transform duration-300 hover:scale-110`}>
			<span className="font-semibold">
				{username[0].toUpperCase()}
			</span>
		</div>
	);
};


const PostSaveOptions: React.FC<{ message: string, onClose: () => void }> = ({message, onClose}) => {
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

const CardStatusMessage: React.FC<{ message: string, type: 'success' | 'error' | 'info' }> = ({message, type}) => {
	return (
		<div
			className={`p-4 rounded-md ${type === 'error' ? 'bg-red-50 text-red-700' : type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
			<p className="text-sm font-medium">{message}</p>
		</div>
	)
}

const ButtonSpinner: React.FC<{ action: "create" | "edit" | "delete" }> = ({action}) => {
	return (
		<span className="flex items-center">
          <svg className="w-5 h-5 mr-2 animate-spin"
               xmlns="http://www.w3.org/2000/svg"
               fill="none"
               viewBox="0 0 24 24">
             <circle className="opacity-25"
                     cx="12"
                     cy="12"
                     r="10"
                     stroke="currentColor"
                     strokeWidth="4">
             </circle>
             <path className="opacity-75"
                   fill="currentColor"
                   d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
             </path>
          </svg>
			{action === "create" ? "Creating..." : action === "edit" ? "Updating..." : "Deleting..."}
       </span>
	)
}


export interface UserRole {
	access_level: string
	created_at: string
	email: string
	id: number
	role_id: number
	username: string
}

interface UserCardProps {
	user: UserRole;
	onDelete: (username: string) => void;
	onEdit: (user: UserRole) => void;
	canEdit?: boolean;
	adminUser: any;
	project_name: string;
}

const MockProject = {
	deleteUserRole: (userId: number, adminUsername: string, projectName: string) => {
		return new Promise((resolve, reject) => {
			// Simulate network delay
			setTimeout(() => {
				// Randomly decide whether to succeed or fail (80% success rate)
				if (Math.random() < 0.8) {
					resolve({success: true, message: "User role deleted successfully"});
				} else {
					reject(new Error("Failed to delete user role"));
				}
			}, 2000); // 2 second delay to simulate network request
		});
	}
};

const UserCard: React.FC<UserCardProps> = ({user, adminUser, project_name, onDelete, onEdit, canEdit = false,}) => {
	const [isDropdownOpen, setIsDropdownOpen] = useState(false);
	const [isConfirming, setIsConfirming] = useState(false);
	const [isDeleting, setIsDeleting] = useState(false);
	const [deleteStatus, setDeleteStatus] = useState<'idle' | 'success' | 'error'>('idle');
	const [statusMessage, setStatusMessage] = useState('');
	const isAdmin = user.access_level?.toLowerCase() === 'admin';
	
	const handleDeleteClick = () => {
		setIsConfirming(true);
	};
	
	const handleClose = () => {
		onDelete(user.username);
	};
	
	const handleConfirmDelete = () => {
		setIsDeleting(true);
		MockProject.deleteUserRole(user.id, adminUser.username, project_name)
			.then((data: any) => {
				console.log("User deleted:", data);
				setTimeout(() => {
					setIsConfirming(false);
					setIsDeleting(false);
					setDeleteStatus('success');
					setStatusMessage('User successfully removed from the project.');
				}, 2000);
			}).catch((error: any) => {
			console.error("Error deleting user:", error);
			setDeleteStatus('error');
			setStatusMessage('Failed to remove user. Please try again.');
			setIsDeleting(false);
		});
	};
	
	const handleCancelDelete = () => {
		setIsConfirming(false);
		setDeleteStatus('idle');
	};
	
	const ACTIONS = [
		{name: "Edit", icon: Edit},
		{name: "Delete", icon: Trash2},
	];
	
	const handleAction = (action: string) => {
		setIsDropdownOpen(false);
		if (action.toLowerCase() === 'delete') {
			handleDeleteClick();
		} else if (action.toLowerCase() === 'edit') {
			onEdit(user);
		}
		// onAction(action.toLowerCase(), item);
	};
	const fullName = new StringExt(user.email.split("@")[0].split(".").slice(0, 2).join(" ")).toTitleCase();
	
	return (
		<div className="bg-base-100 flex overflow-hidden min-h-32 group">
			<div className="ml-4 mr-2 mt-8">
				<CircularAvatar username={user.username} size="md"
				                bgColor="bg-gradient-to-r from-blue-500 to-blue-700"/>
			</div>
			<div className="pl-2 py-2 pr-1 w-full">
				{
					!isConfirming && (
						<div className="">
							<div className="flex space-x-8 justify-end">
								<button
									onClick={() => setIsDropdownOpen(!isDropdownOpen)}
									className="p-1 rounded transition-opacity duration-200 hover:bg-gray-100"
								>
									<EllipsisVertical className="size-4"/>
								</button>
							</div>
							<div className="relative">
								{isDropdownOpen && (
									<div
										className="absolute right-0 mt-1 w-24 bg-white rounded-md shadow-lg z-10 border border-gray-200">
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
					)
				}
				<div>
					<div className="flex items-center justify-between">
						<span className="font-semibold text-neutral-700">{fullName || user.username}</span>
					</div>
				</div>
				{isConfirming ? (
					<React.Fragment>
						<div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-4 mt-2">
							<div className="flex items-center mb-2">
								<AlertCircle className="w-4 h-4 text-yellow-400 mr-2"/>
								<p className="font-medium text-xs text-yellow-700">Confirm Removal</p>
							</div>
							<p className="text-yellow-700 text-xs mb-6">Are you sure you want to remove this user from
								the
								project?</p>
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
					<PostSaveOptions message={statusMessage} onClose={handleClose}/>
				) : (
					<div className="space-y-3">
						<div className="flex items-center max-w-full">
							{/*<Mail className="size-4 text-gray-500 flex-shrink-0 mr-2" />*/}
							<p className="text-sm text-neutral-500 overflow-hidden whitespace-nowrap text-ellipsis w-full">
								{user.email}
							</p>
						</div>
						<div className="flex items-center space-x-4">
							{/*<Briefcase className="size-3.5 text-neutral-500 mr-1"/>*/}
							<span className={`px-2 py-0.5 text-xs font-semibold rounded-sm ${
								isAdmin ? 'bg-blue-100 text-primary' : 'bg-base-200 text-neutral-700'
							}`}>{user.access_level}
								</span>
							<div className="flex items-center">
								<Calendar className="size-3.5 text-neutral-500 mr-1"/>
								<p className="text-gray-700 text-xs">
									{new Date(user.created_at).toLocaleDateString()}
								</p>
							</div>
						</div>
					</div>
				)}
			</div>
		
		</div>
	);
};

export default UserCard;
