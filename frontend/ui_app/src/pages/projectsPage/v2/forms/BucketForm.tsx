import {BucketData} from "../../../../servers/asset_server/bucket.ts";
import React, {useState} from 'react';
import {Project} from "../../../../servers/asset_server";
import InputField from "./fields/InputField.tsx";
import TextAreaField from "./fields/TextAreaField.tsx";

interface FormProps {
	data: BucketData;
	project: Project;
	adminUser: any;
	action: "edit" | "create";
	onSave: (formData: BucketData) => void;
	onCancel: () => void;
}

export const BucketForm: React.FC<FormProps> = ({
	                                                data,
	                                                project,
	                                                adminUser,
	                                                action,
	                                                onSave,
	                                                onCancel
                                                }) => {
	const [formData, setFormData] = useState<BucketData>(data);
	const [formErrors, setFormErrors] = useState<BucketData>({});
	
	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		const {name, value} = e.target;
		const updates = {[name]: value};
		setFormData(prev => ({...prev, ...updates}));
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		const errors = await validateForm(formData);
		if (Object.keys(errors).length === 0) {
			onSave(formData);
		} else {
			setFormErrors(errors);
		}
	};
	
	const validateForm = async (data: BucketData): Promise<BucketData> => {
		const errors: BucketData = {};
		if (!data.bucket_url || data.bucket_url === "n/a") errors.bucket_url = "Url is required";
		if (!data.keys) errors.keys = "Bucket keys are required";
		if (!data.description) errors.description = "Description is required";
		return errors;
	};
	
	return (
		<form onSubmit={handleSubmit} className="">
			<div className="grid grid-cols-1 space-y-8 max-w-2xl">
				<InputField label="Bucket URL"
				            name="title"
				            value={formData.bucket_url}
				            onChange={handleInputChange}
				            error={formErrors.bucket_url}/>
				
				<TextAreaField label={"Bucket Description"}
				               name={"description"}
				               value={formData.description}
				               onChange={handleInputChange}
				               error={formErrors.description}/>
				
				<TextAreaField label={"Bucket Keys"}
				               name={"keys"}
				               value={JSON.stringify(formData.keys)}
				               onChange={handleInputChange}
				               error={formErrors.keys}/>
				
				<TextAreaField label={"Bucket Configuration"}
				               name={"configs"}
				               value={JSON.stringify(formData.configs)}
				               readOnly={true}
				               onChange={handleInputChange}
				               error={JSON.stringify(formErrors.configs)}/>
				
				<InputField label="Created By"
				            name="createdBy"
				            value={formData.created_by}
				            onChange={handleInputChange}
				            readOnly={true}
				            error={formErrors.created_by}/>
				
				<InputField label="Created At"
				            name="createdAt"
				            value={formData.created_at}
				            onChange={handleInputChange}
				            readOnly={true}
				            error={formErrors.created_at}/>
			
			</div>
			<div className="mt-4 flex justify-start space-x-2">
				<button
					type="button"
					onClick={onCancel}
					className="btn btn-sm rounded-md border border-neutral-300">
					Cancel
				</button>
				<button
					type="submit"
					className="btn btn-sm rounded-md bg-primary text-white border-primary">
					Save
				</button>
			</div>
		</form>
	);
}
