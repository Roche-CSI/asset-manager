import React, {useState} from 'react';
import Project, {ProjectData, UserRole} from "../../../../servers/asset_server/project.ts";
import InputField from "./fields/InputField.tsx";
import {SwitchField} from "../../../assetClassPageV2/forms/fields/Fields.tsx";
import {Upload} from "lucide-react";

interface FormProps {
	onSave: (formData: UserRole) => void;
	onCancel: () => void;
	adminUser: any;
	data: UserRole;
	project: ProjectData;
	action: "edit" | "create";
}

const EmptyUser: UserRole = {
	username: "",
	email: "",
	role_id: null,
	id: null,
	access_level: ""
}

export const ProjectUserForm: React.FC<FormProps> = ({
	                                                     onSave,
	                                                     onCancel,
	                                                     adminUser,
	                                                     data,
	                                                     project,
	                                                     action = "create"
                                                     }) => {
	const [formData, setFormData] = useState<UserRole>(data ? JSON.parse(JSON.stringify(data)) : EmptyUser);
	const [formErrors, setFormErrors] = useState<Partial<UserRole>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const {name, value} = e.target;
		const updated = name === "access_level" ? (value === "on" ? "admin" : "member") : value;
		setFormData(prev => ({...prev, [name]: updated}));
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const errors = await validateForm(formData);
		if (Object.keys(errors).length > 0) {
			setFormErrors(errors);
			return;
		}
		
		setIsUpdating(true);
		setStatusMessage(null);
		
		try {
			if (action === "create" && !formData.id) {
				Project.addUserRole({
					...formData,
					project_name: project.name,
					created_by: adminUser.username
				}).then((res) => {
					console.log("User created successfully:", res);
					setIsUpdating(false);
					setStatusMessage({type: 'success', message: 'User added successfully'});
					setShowPostSaveOptions(true);
					// onSave(res);
				}).catch((error: any) => {
					console.error("Error adding user:", error);
					setIsUpdating(false);
					setStatusMessage({
						type: 'error',
						message: 'Error adding user: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
					});
				});
			} else {
				const updatedFields = Object.keys(formData).filter((key) => formData[key as keyof UserRole] !== data[key as keyof UserRole]);
				if (updatedFields.length === 0) {
					setIsUpdating(false);
					setStatusMessage({type: 'info', message: 'No changes detected'});
					return;
				}
				const updates = updatedFields.reduce((acc, key) => ({
					...acc,
					[key]: formData[key as keyof UserRole]
				}), {});
				
				Project.updateUserRole(formData.id!, {
					...updates,
					project_name: project.name,
					modified_by: adminUser.username
				}).then((res) => {
					setFormData(res);
					setIsUpdating(false);
					setStatusMessage({type: 'success', message: 'User updated successfully'});
					setShowPostSaveOptions(true);
					// onSave(res);
				}).catch((error: any) => {
					console.error("Error updating user:", error);
					setIsUpdating(false);
					setStatusMessage({
						type: 'error',
						message: 'Error updating user: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
					});
				});
			}
		} catch (error: any) {
			console.error("Error updating user:", error);
			setIsUpdating(false);
			setStatusMessage({type: 'error', message: 'Error updating user: ' + JSON.stringify(error)});
		}
	};
	
	const validateForm = async (data: UserRole): Promise<Partial<UserRole>> => {
		const errors: Partial<UserRole> = {};
		if (!data.username || data.username === "n/a") errors.username = "UnixId is required";
		if (!data.email) {
			errors.email = "Email is required";
		}
		return errors;
	};
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	const PostSaveOptions: React.FC<{message: string, onClose: () => void}> = ({message, onClose}) => {
		return (
			<div className="space-y-4">
				<div className="p-4 rounded-md bg-green-50 text-green-700">
					<p className="text-sm font-medium">{message}</p>
				</div>
				<button
					onClick={onClose}
					className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
					Close
				</button>
			</div>
		)
	}
	
	const FormStatusMessage: React.FC<{message: string, type: 'success' | 'error' | 'info'}> = ({message, type}) => {
		return (
			<div className={`p-4 rounded-md ${type === 'error' ? 'bg-red-50 text-red-700' : type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
				<p className="text-sm font-medium">{message}</p>
			</div>
		)
	}
	
	const ButtonSpinner: React.FC<{action: "create" | "edit" | "delete"}> = ({action}) => {
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
				{action === "create" ? "Creating..." : "edit" ? "Updating..." : "Deleting..."}
			</span>
		)
	}
	
	return (
		<div className="space-y-6">
			{!showPostSaveOptions ? (
				<form onSubmit={handleSubmit} className="space-y-8">
					<div className="max-w-2xl space-y-6">
						<InputField
							label="Unix Id"
							name="username"
							value={formData.username}
							onChange={handleInputChange}
							placeholder={`Enter your Unix Id`}
							error={formErrors.username}
							readOnly={isUpdating || action === "edit"}
						/>
						
						<InputField
							label="Email"
							name="email"
							value={formData.email}
							onChange={handleInputChange}
							placeholder={`Enter your email`}
							error={formErrors.email}
							readOnly={isUpdating || action === "edit"}
						/>
						
						<SwitchField
							label={"Admin"}
							name={"access_level"}
							checked={formData.access_level === "admin"}
							onChange={handleInputChange}
							readOnly={isUpdating}
						/>
					</div>
					<div className="flex justify-start space-x-4">
						<button
							type="button"
							onClick={onCancel}
							className="btn btn-sm rounded-md border border-base-300"
							disabled={isUpdating}
						>
							Cancel
						</button>
						<button
							type="submit"
							className="btn btn-secondary btn-sm rounded-md flex"
							disabled={isUpdating}
						>
							{
								isUpdating ? (<ButtonSpinner action={action}/>) :
								(
									<span>
										Save
									</span>
								)
							}
							
						</button>
					</div>
				</form>
			) : (
				<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose}/>
			)}
			{
				statusMessage && !showPostSaveOptions && (
				<FormStatusMessage message={statusMessage.message} type={statusMessage.type}/>)
			}
		</div>
	);
};
