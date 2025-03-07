import React, { useState } from 'react';
import { CLASS_TYPE } from "../../../components/assetClassBrowser";
import { AssetClass } from "../../../servers/asset_server";
import { formatAssetClassName, validateAssetClassName } from "../../assetClassPage/utils";
import { InputField, SelectField } from "./fields/Fields";
import { ButtonSpinner, FormStatusMessage, PostSaveOptions } from "./FormHelpers";
import { StoreNames, useStore } from "../../../stores";
import {isEmptyObject} from "../../../utils";
import {AccessStatus} from "servers/base/accessStatus";
import {Project} from "servers/asset_server";


type FormState = {
	id?: string | null | undefined;
	title?: string;
	class_type?: string;
	name?: string;
	description?: string;
	has_readme?: boolean;
	is_create?: boolean;
	owner?: string;
	created_at?: string;
	status?: string;
};

const emptyForm: FormState = {
	id: "",
	name: "",
	title: "",
	description: "",
	class_type: "",
	has_readme: false,
	is_create: true,
	owner: "",
	created_at: "",
	project_id: null,
	project_name: null
}

interface AssetClassFormProps {
	project: Project;
	assetClass?: AssetClass;
	onSave: (formData: FormState) => void;
	onCancel: () => void;
	action: "edit" | "create";
}

export const AssetClassForm: React.FC<AssetClassFormProps> = ({ project, assetClass, onSave, onCancel, action = "edit" }) => {
	const data = assetClass ? assetClass : { ...emptyForm, project_id: project.id, project_name: project.name };
	const [formData, setFormData] = useState<FormState>(JSON.parse(JSON.stringify(data)));
	const [formErrors, setFormErrors] = useState<Record<string, string>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string;
		data?: any;
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const userStore = useStore(StoreNames.userStore);
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const { name, value } = e.target;
		const updates = { [name]: value };
		if (action === "create" && name === "title") {
			updates["name"] = formatAssetClassName(value);
		}
		setFormData(prev => ({ ...prev, ...updates }));
		setFormErrors(prev => ({ ...prev, [name]: '' }));
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const valid = await validateForm(formData);
		if (!valid) {
			setStatusMessage(null);
			return;
		}
		if (action === "edit") {
			updateAssetClass(formData);
		}else if (action === "create") {
			createAssetClass(formData);
		}else {
			throw new Error("Invalid action type");
		}
	};
	
	const updateAssetClass = (formData: any) => {
		let editFields = ["title", "class_type", "description", "status"];
		const props  = {
			title: assetClass!.title,
			class_type: assetClass!.class_type,
			description: assetClass!.description,
			status: assetClass!.status
		};
		let data: any = {};
		editFields.forEach((field: string) => {
			if ((formData as any)[field] !== (props as any)[field]) {
				data[field] = (formData as any)[field];
			}
		})
		if (!isEmptyObject(data)) {
			data["user"] = userStore.get("user").username;
		}
		setIsUpdating(true);
		setTimeout(() => {
			AssetClass.update(assetClass!.id, data, false).then(res => {
				setIsUpdating(false);
				setStatusMessage({ type: 'success', message: 'Asset Class updated successfully', data: res });
				setShowPostSaveOptions(true);
			}).catch(error => {
				console.log("error:", error);
				setIsUpdating(false);
				setStatusMessage({
					type: 'error',
					message: 'Error updating asset class: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
				});
				setShowPostSaveOptions(false);
			})
		}, 1000); // 1 second delay
	}
	
	const createAssetClass = (formData: any) => {
		const data = JSON.parse(JSON.stringify(formData)); // clone
		if (isEmptyObject(data)) {
			throw new Error("No data to save");
		}
		
		data["user"] = userStore.get("user").username;
		setIsUpdating(true);
		setTimeout(() => {
			AssetClass.create(data, false).then(res => {
				setIsUpdating(false);
				setFormData(res);
				setStatusMessage({ type: 'success', message: 'Asset Class created successfully', data: res });
				setShowPostSaveOptions(true);
			}).catch(error => {
				console.log("error:", error);
				setIsUpdating(false);
				setStatusMessage({
					type: 'error',
					message: 'Error creating asset class: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
				});
				setShowPostSaveOptions(false);
			})
		}, 1000); // 1 second delay
	}
	
	const validateForm = async (data: FormState): Promise<boolean> => {
		const errors: Record<string, string> = {};
		if (!data.title || data.title === "n/a") errors.title = "Title is required";
		if (!data.name) errors.name = "Name is required";
		if (data.name && !validateAssetClassName(data.name)) errors.name =
			"Name must be fewer than 52 characters, and only consists of lower case letters, digits, underscore, hyphen, or dot";
		if (!data.class_type || data.class_type === "others") errors.class_type = "Type is required";
		if (!data.description) errors.description = "Description is required";
		
		if (Object.keys(errors).length > 0) {
			setFormErrors(errors);
			setStatusMessage({ type: 'error', message: 'Please fix the errors in the form' });
			return false;
		}
		return true;
	};
	
	const categoryOptions = Object.values(CLASS_TYPE).map((type) => ({
		value: type,
		label: type
	}));
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	return (
		<div className="space-y-6 max-w-7xl">
			{!showPostSaveOptions ? (
				<React.Fragment>
					<form onSubmit={handleSubmit} className="">
						<div className="grid grid-cols-3 gap-4">
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
							            readOnly={action === "edit" || isUpdating}
							            error={formErrors.name}/>
							
							<SelectField label="Type"
							             name="class_type"
							             value={formData.class_type}
							             options={categoryOptions}
							             onChange={handleInputChange}
							             error={formErrors.class_type}
							             readOnly={isUpdating}/>
							
							<SelectField label="Status" name="status"
							             value={formData.status}
							             options={AccessStatus.getAll()}
							             onChange={handleInputChange}
							             error={formErrors.status}
							             readOnly={isUpdating}/>
							
							<InputField label="ID"
							            name="id"
							            value={formData.id}
							            onChange={handleInputChange}
							            readOnly={true}
							            error={formErrors.id}/>
						</div>
						<div className="mt-6">
							<label htmlFor="description"
							       className="block text-sm font-semibold text-gray-700 mb-1">About</label>
							<textarea
								id="description"
								name="description"
								value={formData.description}
								onChange={handleInputChange}
								className={`w-full p-2 border rounded ${formErrors.description ? "border-red-500" : ""}`}
								rows={4}
								readOnly={isUpdating}
							/>
							{formErrors.description &&
                                <p className="text-red-500 text-xs mt-1">{formErrors.description}</p>}
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
								{isUpdating ? <ButtonSpinner
									message={action === "create" ? "Creating..." : "Updating"}/> : 'Save'}
							</button>
						</div>
					</form>
					{
						statusMessage && !showPostSaveOptions && (
							<FormStatusMessage message={statusMessage.message} type={statusMessage.type}/>
						)
					}
				</React.Fragment>
			) : (
				<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose}/>
			)}
		</div>
	);
}
