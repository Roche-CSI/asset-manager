import React, {useState} from 'react';
import {AssetClass} from "../../../servers/asset_server";
import {validateAssetClassName} from "../../assetClassPage/utils";
import {InputField, TextAreaField, SelectField} from "./fields/Fields";
import Template, {TEMPLATE_CATEGORIES, TemplateData} from "../../../servers/asset_server/template";
import {StoreNames, useStore} from "../../../stores";
import {ButtonSpinner, FormStatusMessage, PostSaveOptions} from "./FormHelpers";

interface FormProps {
	assetClass: AssetClass;
	data?: TemplateData;
	onSave: (formData: TemplateData) => void;
	onCancel: () => void;
	action: "edit" | "create";
}

const EmptyTemplateData: TemplateData = {
	id: "",
	title: "",
	name: "",
	category: "",
	description: "",
	created_by: "",
	created_at: "",
	is_active: true,
	readme: "",
	version: "",
	configs: {}
};

export const TemplateForm: React.FC<FormProps> = ({
	                                                  assetClass,
	                                                  onSave,
	                                                  onCancel,
	                                                  action = "create",
	                                                  data
                                                  }) => {
	const [formData, setFormData] = useState<TemplateData>(JSON.parse(JSON.stringify(data || EmptyTemplateData)));
	const [formErrors, setFormErrors] = useState<TemplateData>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const userStore = useStore(StoreNames.userStore);
	const currentUser = userStore.get("user");
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const {name, value} = e.target;
		const updates = {[name]: value};
		setFormData(prev => ({...prev, ...updates}));
		setFormErrors(prev => ({...prev, [name]: ''}));
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const errors = await validateForm(formData);
		if (Object.keys(errors).length > 0) {
			setFormErrors(errors);
			setStatusMessage({type: 'error', message: 'Please fix the errors in the form'});
			return;
		}
		setIsUpdating(true);
		setStatusMessage(null);
		
		try {
			if (action === "create" && !formData.id) {
				Template.create(currentUser.username, {...formData, class_id: assetClass.id}, true).then((res) => {
					console.log("Template created successfully:", res);
					setIsUpdating(false);
					setStatusMessage({type: 'success', message: 'Template created successfully'});
					setShowPostSaveOptions(true);
				});
			} else {
				const updatedFields = Object.keys(formData).filter((key) => formData[key] !== data[key]);
				if (updatedFields.length > 0) {
					const updates = updatedFields.reduce((acc, key) => ({...acc, [key]: formData[key]}), {});
					Template.update(currentUser.username, formData.id, updates, true).then((res) => {
						console.log("Template updated successfully:", res);
						setIsUpdating(false);
						setStatusMessage({
							type: 'success',
							message: `Template ${action === "edit" ? "updated" : "created"} successfully`
						});
						setShowPostSaveOptions(true);
					});
				} else {
					setIsUpdating(false);
					setStatusMessage({type: 'info', message: 'No changes detected'});
				}
			}
		} catch (error: any) {
			console.error("Error updating template:", error);
			setIsUpdating(false);
			setStatusMessage({
				type: 'error',
				message: 'Error updating template: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
			});
		}
	};
	
	const validateForm = async (data: TemplateData): Promise<TemplateData> => {
		const errors: TemplateData = {};
		if (!data.title || data.title === "n/a") errors.title = "Title is required";
		if (!data.name) errors.name = "Name is required";
		if (data.name && !validateAssetClassName(data.name)) errors.name =
			"Name must be fewer than 52 characters, and only consists of lower case letters, digits, underscore, hyphen, or dot";
		if (!data.category) errors.category = "Category is required";
		if (!data.description) errors.description = "Description is required";
		return errors;
	};
	
	const options: { value: string, label: string }[] = Object.values(TEMPLATE_CATEGORIES).map((type) => ({
		value: type as string,
		label: type as string
	}));
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	return (
		<div className="space-y-6 max-w-7xl">
			{!showPostSaveOptions ? (
				<form onSubmit={handleSubmit} className="max-w-7xl">
					<div className="grid grid-cols-2 gap-6">
						<InputField label="Title"
						            name="title"
						            value={formData.title}
						            onChange={handleInputChange}
						            error={formErrors.title}
						            readOnly={isUpdating}/>
						
						<InputField label="Name"
						            name="name"
						            value={formData.name}
						            onChange={handleInputChange}
						            readOnly={isUpdating}
						            error={formErrors.name}/>
						
						<SelectField label="Category"
						             name="category"
						             value={formData.category}
						             options={options}
						             readOnly={isUpdating}
						             onChange={handleInputChange}
						             error={formErrors.category}/>
						
						<InputField label="ID"
						            name="id"
						            value={formData.id}
						            onChange={handleInputChange}
						            readOnly={true}
						            error={formErrors.id}/>
					</div>
					<div className="mt-6">
						<TextAreaField label={"Description"}
						               name={"description"}
						               value={formData.description}
						               rows={6}
						               onChange={handleInputChange}
						               readOnly={isUpdating}
						               error={formErrors.description}/>
					</div>
					<div className="mt-6">
						<TextAreaField label={"Configurations"}
						               name={"configs"}
						               value={JSON.stringify(formData.configs, null, 2)}
						               rows={6}
						               readOnly={isUpdating}
						               onChange={handleInputChange}/>
					</div>
					<div className="mt-6">
						<TextAreaField label={"Sample Data"}
						               name={"sample_data"}
						               value={JSON.stringify(formData.sample_data, null, 2)}
						               rows={6}
						               readOnly={isUpdating}
						               onChange={handleInputChange}/>
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
							{isUpdating ? <ButtonSpinner/> : 'Save'}
						</button>
					</div>
				</form>
			) : (
				<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose}/>
			)}
			{
				statusMessage && !showPostSaveOptions && (
					<FormStatusMessage message={statusMessage.message} type={statusMessage.type}/>
				)
			}
		</div>
	);
}
