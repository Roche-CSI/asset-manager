import React, { useState } from 'react';
import { InputField, TextAreaField, SelectField } from "./fields/Fields";
import {ButtonSpinner, FormStatusMessage, PostSaveOptions} from "./FormHelpers";

interface WebhookData {
	id: string;
	entity_type: string;
	entity_id: string;
	name: string;
	title: string;
	description: string;
	webhook_url: string;
	event_type: string;
	event_source: string;
	attributes: {
		status: string;
		importance: string;
	};
}

interface FormProps {
	data?: WebhookData;
	onSave: (formData: WebhookData) => void;
	onCancel: () => void;
	action: "edit" | "create";
}

const EmptyWebhookData: WebhookData = {
	id: "",
	entity_type: "",
	entity_id: "",
	name: "",
	title: "",
	description: "",
	webhook_url: "",
	event_type: "",
	event_source: "",
	attributes: {
		status: "",
		importance: ""
	}
};

const entityTypeOptions = [
	{ value: "", label: "" },
	{ value: "asset_collection", label: "Asset Collection" },
	// { value: "project", label: "Project" },
	{ value: "asset", label: "Asset" },
];

const eventSourceOptions = [
	{ value: "", label: "" },
	// { value: "asset_class", label: "Asset Collection" },
	// { value: "project", label: "Project" },
	{ value: "asset", label: "Asset" },
];

const eventTypeOptions = [
	{ value: "", label: "" },
	{ value: "create", label: "Create" },
	{ value: "update", label: "Update" },
	{ value: "delete", label: "Delete" },
	{ value: "deprecate", label: "Deprecate" },
	{ value: "obsolete", label: "Obsolete" }
];

const statusOptions = [
	{ value: "", label: "" },
	{ value: "available", label: "Available" },
	{ value: "scheduled", label: "Scheduled" },
	{ value: "deprecated", label: "Deprecated" }
];

const importanceOptions = [
	{ value: "", label: "" },
	{ value: "low", label: "Low" },
	{ value: "medium", label: "Medium" },
	{ value: "high", label: "High" },
	{ value: "critical", label: "Critical" }
];

export const WebhookForm: React.FC<FormProps> = ({
	                                                 onSave,
	                                                 onCancel,
	                                                 action = "create",
	                                                 data
                                                 }) => {
	const [formData, setFormData] = useState<WebhookData>(data || EmptyWebhookData);
	const [formErrors, setFormErrors] = useState<Partial<WebhookData>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string
	} | null>(null);
	
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const { name, value } = e.target;
		if (name === "status" || name === "importance") {
			setFormData(prev => ({
				...prev,
				attributes: {
					...prev.attributes,
					[name]: value
				}
			}));
		} else {
			setFormData(prev => ({ ...prev, [name]: value }));
		}
		// setFormErrors(prev => ({ ...prev, [name]: '' }));
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const errors = validateForm(formData);
		if (Object.keys(errors).length > 0) {
			setFormErrors(errors);
			setStatusMessage({ type: 'error', message: 'Please fix the errors in the form' });
			return;
		}
		setIsUpdating(true);
		setStatusMessage(null);
		
		try {
			// Here you would typically call an API to save the webhook
			// For now, we'll just simulate a successful save
			await new Promise(resolve => setTimeout(resolve, 1000));
			console.log(`Webhook ${action === "edit" ? "updated" : "created"} successfully:`);
			setIsUpdating(false);
			setStatusMessage({ type: 'success', message: `Webhook ${action === "edit" ? "updated" : "created"} successfully` });
			setShowPostSaveOptions(true);
		} catch (error: any) {
			console.error("Error saving webhook:", error);
			setIsUpdating(false);
			setStatusMessage({
				type: 'error',
				message: 'Error saving webhook: ' + (error.message || JSON.stringify(error))
			});
			setShowPostSaveOptions(false);
		}
	};
	
	const validateForm = (data: WebhookData): Partial<WebhookData> => {
		const errors: Partial<WebhookData> = {};
		if (!data.title) errors.title = "Title is required";
		if (!data.name) errors.name = "Name is required";
		if (!data.entity_type) errors.entity_type = "Entity Type is required";
		if (!data.entity_id) errors.entity_id = "Entity ID is required";
		if (!data.event_type) errors.event_type = "Event Type is required";
		if (!data.event_source) errors.event_source = "Event Source is required";
		if (!data.webhook_url) errors.webhook_url = "Webhook URL is required";
		if (!data.attributes.status) errors.attributes = { ...errors.attributes, status: "Status is required" };
		if (!data.attributes.importance) errors.attributes = { ...errors.attributes, importance: "Importance is required" };
		return errors;
	};
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	return (
		<div className="space-y-6 max-w-7xl">
			{
				!showPostSaveOptions ?
					<form onSubmit={handleSubmit} className="space-y-6">
						<div className="grid grid-cols-2 gap-6">
							<InputField
								label="Title"
								name="title"
								value={formData.title}
								onChange={handleInputChange}
								error={formErrors.title}
								readOnly={isUpdating}
							/>
							<InputField
								label="Name"
								name="name"
								value={formData.name}
								onChange={handleInputChange}
								error={formErrors.name}
								readOnly={isUpdating}
							/>
							{/*<SelectField*/}
							{/*	label="Target Entity Type"*/}
							{/*	name="entity_type"*/}
							{/*	value={formData.entity_type}*/}
							{/*	options={entityTypeOptions}*/}
							{/*	onChange={handleInputChange}*/}
							{/*	error={formErrors.entity_type}*/}
							{/*	readOnly={isUpdating}*/}
							{/*/>*/}
							{/*<InputField*/}
							{/*	label="Target Entity ID"*/}
							{/*	name="entity_id"*/}
							{/*	value={formData.entity_id}*/}
							{/*	onChange={handleInputChange}*/}
							{/*	error={formErrors.entity_id}*/}
							{/*	readOnly={isUpdating}*/}
							{/*/>*/}
							<SelectField
								label="Event Source"
								name="event_source"
								value={formData.event_source}
								options={eventSourceOptions}
								onChange={handleInputChange}
								error={formErrors.event_source}
								readOnly={isUpdating}
							/>
							<SelectField
								label="Event Type"
								name="event_type"
								value={formData.event_type}
								options={eventTypeOptions}
								onChange={handleInputChange}
								error={formErrors.event_type}
								readOnly={isUpdating}
							/>
							<InputField
								label="Webhook URL"
								name="webhook_url"
								value={formData.webhook_url}
								onChange={handleInputChange}
								error={formErrors.webhook_url}
								readOnly={isUpdating}
							/>
						</div>
						<div className="grid grid-cols-2 gap-6">
							<SelectField
								label="Status"
								name="status"
								value={formData.attributes.status}
								options={statusOptions}
								onChange={handleInputChange}
								error={formErrors.attributes?.status}
								readOnly={isUpdating}
							/>
							{/*<SelectField*/}
							{/*	label="Importance"*/}
							{/*	name="importance"*/}
							{/*	value={formData.attributes.importance}*/}
							{/*	options={importanceOptions}*/}
							{/*	onChange={handleInputChange}*/}
							{/*	error={formErrors.attributes?.importance}*/}
							{/*	readOnly={isUpdating}*/}
							{/*/>*/}
						</div>
						<TextAreaField
							label="Description"
							name="description"
							value={formData.description}
							onChange={handleInputChange}
							error={formErrors.description}
							readOnly={isUpdating}
							rows={5}
						/>
						<div className="flex justify-start space-x-4">
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
								{isUpdating ?
									<ButtonSpinner message={action === "edit" ? "Updating" : "Creating"}/> : 'Save'}
							</button>
						</div>
					</form> :
					<PostSaveOptions message={statusMessage?.message as string}
					                 onClose={handleClose}/>
				
			}
			{statusMessage && !showPostSaveOptions && (
				<FormStatusMessage message={statusMessage.message} type={statusMessage.type}/>
			)}
		</div>
	);
}

export default WebhookForm;
