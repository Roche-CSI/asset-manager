import React, { useState } from 'react';
import InputField from "./fields/InputField.tsx";
import TextAreaField from "./fields/TextAreaField.tsx";
import { ProjectData } from "../../../../servers/asset_server/project";

interface FormProps {
	data?: ProjectData;
	onSave: (formData: ProjectData) => void;
	onCancel: () => void;
	action?: "edit" | "create";
}

const emptyProject: ProjectData = {
	id: "",
	name: "",
	title: "",
	description: "",
	created_by: "",
	created_at: "",
	remote_url: "",
};

export const ProjectForm: React.FC<FormProps> = ({ onSave, onCancel, data, action= "edit" }) => {
	const [formData, setFormData] = useState<ProjectData>(JSON.parse(JSON.stringify(data || emptyProject)));
	const [formErrors, setFormErrors] = useState<Partial<ProjectData>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const { name, value } = e.target;
		setFormData(prev => ({ ...prev, [name]: value }));
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
			const updatedFields = Object.keys(formData).filter((key) => formData[key as keyof ProjectData] !== data[key as keyof ProjectData]);
			
			// remove credentials from updated fields
			["credentials_server", "credentials_user"].forEach((crede) => {
				updatedFields.splice(updatedFields.indexOf(crede), 1);
			});
			
			if (updatedFields.length === 0) {
				setIsUpdating(false);
				setStatusMessage({ type: 'info', message: 'No changes detected' });
				return;
			}
			console.log("Updated fields:", updatedFields);
			console.log("formData:", formData, " projectData:", data);
			const updates = updatedFields.reduce((acc, key) => ({
				...acc,
				[key]: formData[key as keyof ProjectData]
			}), {});
			
			// Assuming there's a Project.updateProject method
			// Project.updateProject(formData.id!, {
			//     ...updates,
			//     modified_by: adminUser.username
			// }).then((res) => {
			//     setFormData(res);
			//     setIsUpdating(false);
			//     setStatusMessage({ type: 'success', message: 'Project updated successfully' });
			//     setShowPostSaveOptions(true);
			// }).catch((error: any) => {
			//     console.error("Error updating project:", error);
			//     setIsUpdating(false);
			//     setStatusMessage({
			//         type: 'error',
			//         message: 'Error updating project: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
			//     });
			// });
			
		} catch (error: any) {
			console.error("Error updating project:", error);
			setIsUpdating(false);
			setStatusMessage({ type: 'error', message: 'Error updating project: ' + JSON.stringify(error) });
		}
	};
	
	const validateForm = async (data: ProjectData): Promise<Partial<ProjectData>> => {
		const errors: Partial<ProjectData> = {};
		if (!data.name || data.name === "n/a") errors.name = "Name is required";
		if (!data.title) errors.title = "Title is required";
		if (!data.description) errors.description = "Description is required";
		return errors;
	};
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	const PostSaveOptions: React.FC<{ message: string, onClose: () => void }> = ({ message, onClose }) => {
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
	
	const FormStatusMessage: React.FC<{ message: string, type: 'success' | 'error' | 'info' }> = ({ message, type }) => {
		return (
			<div className={`p-4 rounded-md ${type === 'error' ? 'bg-red-50 text-red-700' : type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
				<p className="text-sm font-medium">{message}</p>
			</div>
		)
	}
	
	const ButtonSpinner: React.FC = () => {
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
                Updating...
            </span>
		)
	}
	
	return (
		<div className="space-y-6">
			{!showPostSaveOptions ? (
				<form onSubmit={handleSubmit} className="space-y-8">
					<div className="grid grid-cols-1 space-y-8 max-w-2xl">
						<InputField
							label="Project Title"
							name="title"
							placeholder="Enter project title"
							value={formData.title}
							onChange={handleInputChange}
							error={formErrors.title}
						/>
						{
							action === "create" && (
								<InputField
									label="Project Name"
									name="name"
									placeholder="Enter project name"
									value={formData.name}
									onChange={handleInputChange}
									error={formErrors.name}
								/>
							)
						}
						
						<TextAreaField
							label="Project Description"
							name="description"
							value={formData.description}
							placeholder="Enter project description"
							onChange={handleInputChange}
							error={formErrors.description}
						/>
						{/*<InputField*/}
						{/*	label="Created By"*/}
						{/*	name="created_by"*/}
						{/*	value={formData.created_by}*/}
						{/*	onChange={handleInputChange}*/}
						{/*	readOnly={true}*/}
						{/*	error={formErrors.created_by}*/}
						{/*/>*/}
						
						{/*<InputField*/}
						{/*	label="Created At"*/}
						{/*	name="created_at"*/}
						{/*	value={formData.created_at}*/}
						{/*	onChange={handleInputChange}*/}
						{/*	readOnly={true}*/}
						{/*	error={formErrors.created_at}*/}
						{/*/>*/}
						
						{
							action === "create" && (
								<InputField
									label="Remote URL"
									name="remote_url"
									value={formData.remote_url}
									onChange={handleInputChange}
									error={formErrors.remote_url}
								/>
							)
						}
					</div>
					<div className="mt-12 flex justify-start space-x-4">
						<button
							type="button"
							onClick={onCancel}
							className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
							disabled={isUpdating}
						>
							Cancel
						</button>
						<button
							type="submit"
							className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
							disabled={isUpdating}
						>
							{isUpdating ? <ButtonSpinner /> : 'Save'}
						</button>
					</div>
				</form>
			) : (
				<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose} />
			)}
			{
				statusMessage && !showPostSaveOptions && (
					<FormStatusMessage message={statusMessage.message} type={statusMessage.type} />
				)
			}
		</div>
	);
}
