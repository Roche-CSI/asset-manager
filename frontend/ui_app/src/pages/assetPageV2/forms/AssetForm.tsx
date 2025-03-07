import React, { useState } from 'react';
import _ from 'lodash'
import { Asset, AssetInterface } from "../../../servers/asset_server";
import { InputField, SelectField, TextAreaField } from "../../assetClassPageV2/forms/fields/Fields";
import { CodeEditorField } from '../../../components/formElements';
import { ButtonSpinner, FormStatusMessage, PostSaveOptions } from "../../assetClassPageV2/forms/FormHelpers";
import { StoreNames, useStore } from "../../../stores";
import { isEmptyObject, safeClone } from "../../../utils";
import { AssetPhase } from "../../../servers/asset_server/assetPhase";
import { AccessStatus } from "../../../servers/base/accessStatus";
import ErrorBoundary from "../../../components/errorBoundary/ErrorBoundary";

type FormState = Partial<AssetInterface>;

interface AssetFormProps {
	asset: AssetInterface;
	onSave: (formData: FormState) => void;
	onCancel: () => void;
	action: "edit" | "create";
}


export const AssetForm: React.FC<AssetFormProps> = ({ asset, onSave, onCancel, action = "edit" }) => {
	const [formData, setFormData] = useState<FormState>(safeClone(asset));
	const [formErrors, setFormErrors] = useState<Record<string, string>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string;
		data?: any;
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);

	const userStore = useStore(StoreNames.userStore);
	const currentUser = userStore.get("user");

	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const { name, value } = e.target;
		const result: string | number = name === 'status' ? Number(value) : value;
		setFormData(prev => ({ ...prev, [name]: result }));
		setFormErrors(prev => ({ ...prev, [name]: '' }));
	};

	const handleAttributesChange = (value: string) => {
		const newAtrributes = JSON.parse(value);
		setFormData(prev => ({ ...prev, 'attributes': newAtrributes }));
	}

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const valid = await validateForm(formData);
		if (!valid) {
			setStatusMessage(null);
			return;
		}
		updateAsset(formData);
	};

	const updateAsset = (formData: FormState) => {
		let editFields: (keyof AssetInterface)[] = ["title", "description", "owner", "alias", "status", "phase", "attributes"];
		let data: Partial<AssetInterface> = {};
		editFields.forEach((field) => {
			if (!_.isEqual(formData[field], asset[field])) {
				data[field] = formData[field];
			}
		});
		if (!isEmptyObject(data)) {
			data.modified_by = currentUser.username;
		}
		data.user = currentUser.username;
		setIsUpdating(true);
		setTimeout(() => {
			Asset.update(asset.id, data).then(res => {
				setIsUpdating(false);
				setStatusMessage({ type: 'success', message: 'Asset updated successfully', data: res });
				setShowPostSaveOptions(true);
			}).catch(error => {
				console.log("error:", error);
				setIsUpdating(false);
				setStatusMessage({
					type: 'error',
					message: 'Error updating asset: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
				});
				setShowPostSaveOptions(false);
			});
		}, 1000);
	};

	const validateForm = async (data: FormState): Promise<boolean> => {
		const errors: Record<string, string> = {};
		// if (!data.title) errors.title = "Title is required";
		if (!data.asset_class) errors.asset_class = "Asset class is required";
		if (!data.description) errors.description = "Description is required";
		if (!data.owner) errors.owner = "Owner is required";

		if (Object.keys(errors).length > 0) {
			setFormErrors(errors);
			setStatusMessage({ type: 'error', message: 'Please fix the errors in the form' });
			return false;
		}
		return true;
	};

	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};

	return (
		<ErrorBoundary>
			<div className="space-y-6 max-w-7xl">
				{!showPostSaveOptions ? (
					<React.Fragment>
						<form onSubmit={handleSubmit} className="">
							<div className="grid grid-cols-3 gap-4">
								<InputField
									label="Title"
									name="title"
									value={formData.title}
									onChange={handleInputChange}
									error={formErrors.title}
									readOnly={isUpdating}
								/>

								<InputField
									label="Owner"
									name="owner"
									value={formData.owner}
									onChange={handleInputChange}
									error={formErrors.owner}
									readOnly={isUpdating}
								/>

								<InputField
									label="Alias"
									name="alias"
									value={formData.alias}
									onChange={handleInputChange}
									error={formErrors.alias}
									readOnly={isUpdating}
								/>
								<SelectField label="Status" name="status"
									value={formData.status}
									options={AccessStatus.getAll()}
									onChange={handleInputChange}
									error={formErrors.status}
									readOnly={isUpdating} />
								<SelectField
									label="Phase"
									name="phase"
									value={formData.phase}
									options={AssetPhase.getAll()}
									onChange={handleInputChange}
									error={formErrors.status}
									readOnly={isUpdating} />
							</div>
							<div className="mt-6">
								<TextAreaField label={"Description"}
									name={"description"}
									value={formData.description}
									readOnly={isUpdating}
									error={formErrors.description}
									onChange={handleInputChange} />
								<CodeEditorField
									label={"Attributes"}
									fieldName={"attributes"}
									className={"block font-semibold !text-gray-700 mb-1 text-sm"}
									readOnly={isUpdating}
									value={JSON.stringify(formData.attributes)}
									onChange={handleAttributesChange}
									error={formErrors.attributes}
								/>
							</div>
							<div className="mt-6 grid grid-cols-3 gap-4">
								<InputField
									label="ID"
									name="id"
									value={formData.id}
									onChange={handleInputChange}
									readOnly={true}
									error={formErrors.id}
								/>
								<InputField
									label="Asset Class ID"
									name="asset_class"
									value={formData.asset_class}
									onChange={handleInputChange}
									error={formErrors.asset_class}
									readOnly={action === "edit" || isUpdating}
								/>
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
									{isUpdating ? (
										<ButtonSpinner message={action === "create" ? "Creating..." : "Updating"} />
									) : (
										'Save'
									)}
								</button>
							</div>
						</form>
						{statusMessage && !showPostSaveOptions && (
							<FormStatusMessage message={statusMessage.message} type={statusMessage.type} />
						)}
					</React.Fragment>
				) : (
					<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose} />
				)}
			</div>
		</ErrorBoundary>
	);
};
