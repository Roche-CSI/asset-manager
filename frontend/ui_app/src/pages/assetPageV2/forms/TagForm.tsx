import React, { useState, useMemo } from 'react';
import { Asset, AssetInterface } from "servers/asset_server";
import { isEmptyObject } from "utils";
import { StoreNames, useStore } from "stores";
import { FormStatusMessage, PostSaveOptions } from "../../assetClassPageV2/forms/FormHelpers";
import {Plus} from "lucide-react";

interface TagFormData {
	tags: string[];
}

interface TagFormProps {
	asset: Asset;
	tags: string[];
	onSave: (formData: TagFormData) => void;
	onCancel: () => void;
}

const TagForm: React.FC<TagFormProps> = ({
	                                           asset,
	                                           tags,
	                                           onSave,
	                                           onCancel
                                           }) => {
	// Memoize initial data to prevent unnecessary recalculations
	const initialData = useMemo(() => ({tags: tags || []}), [tags]);
	
	const [formData, setFormData] = useState<TagFormData>(initialData);
	const [formErrors, setFormErrors] = useState<Record<string, string>>({});
	const [isUpdating, setIsUpdating] = useState(false);
	const [newTag, setNewTag] = useState('');
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string;
		data?: any;
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const userStore = useStore(StoreNames.userStore);
	const currentUser = userStore.get("user");
	
	// Helper function to check if data has actually changed
	const hasDataChanged = (newData: TagFormData): boolean => {
		try {
			// Compare tags arrays
			debugger;
			if (initialData.tags.length !== newData.tags.length) return true;
			
			newData.tags.forEach(tag => {
				if (!initialData.tags.includes(tag)) return true;
			});
			return false;
		} catch (e) {
			console.error('Error comparing data:', e);
			return false;
		}
	};
	
	const handleAddTag = () => {
		const sanitizedTag = newTag.trim();
		if (!sanitizedTag) return;
		
		// Split by comma and trim each tag
		const newTags = sanitizedTag
			.split(',')
			.map(tag => removeAllQuotes(tag.trim()))
			.filter(tag => tag.length > 0);
		
		if (newTags.length === 0) return;
		console.log('newTags:', newTags);
		
		setFormData(prev => ({
			...prev,
			tags: [...new Set([...prev.tags, ...newTags])] // Remove duplicates
		}));
		setNewTag('');
	};
	
	const handleRemoveTag = (tagToRemove: string) => {
		setFormData(prev => ({
			...prev,
			tags: prev.tags.filter(tag => tag !== tagToRemove)
		}));
	};
	
	const removeAllQuotes = (str: string): string => {
		return str.replace(/["\\\s]+/g, '').trim();
	}
	
	const handleTagKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === 'Enter') {
			e.preventDefault();
			handleAddTag();
		}
	};
	
	const validateForm = (): boolean => {
		const errors: Record<string, string> = {};
		setFormErrors(errors);
		if (Object.keys(errors).length > 0) {
			setStatusMessage({ type: 'error', message: 'Please fix the errors in the form' });
			return false;
		}
		return true;
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		if (!validateForm()) return;
		
		// Only proceed with update if data has actually changed
		if (!hasDataChanged(formData)) {
			setStatusMessage({ type: 'info', message: 'No changes detected' });
			return;
		}
		
		updateAsset(formData);
	};
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		onSave(formData);
	};
	
	const updateAsset = (formData: TagFormData) => {
		let data: Partial<AssetInterface> = {};
		
		try {
			// Compare tags
			if (!arraysEqual(formData.tags, initialData.tags)) {
				data.tags = formData.tags;
			}
			
			if (isEmptyObject(data)) {
				setStatusMessage({ type: 'info', message: 'No changes to save' });
				return;
			}
			
			data.modified_by = currentUser.username;
			data.user = currentUser.username;
			
			setIsUpdating(true);
			Asset.update(asset.id, data).then(res => {
				setIsUpdating(false);
				setStatusMessage({ type: 'success', message: 'Asset tags updated successfully', data: res });
				setShowPostSaveOptions(true);
			}).catch(error => {
				console.error("error:", error);
				setIsUpdating(false);
				setStatusMessage({
					type: 'error',
					message: 'Error updating asset tags: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
				});
				setShowPostSaveOptions(false);
			});
		} catch (error) {
			console.error("Error preparing update data:", error);
			setStatusMessage({ type: 'error', message: 'Error preparing update data' });
		}
	};
	
	// Helper function to compare arrays of tags
	const arraysEqual = (a: string[], b: string[]): boolean => {
		if (a.length !== b.length) return false;
		return a.every(tag => b.includes(tag));
	};
	
	return (
		<div className="space-y-6 max-w-7xl">
			{!showPostSaveOptions ? (
				<React.Fragment>
					<form onSubmit={handleSubmit} className="space-y-6">
						<div className="space-y-4">
							<label className="block text-gray-700 text-md font-semibold mb-2">
								Edit Tags
							</label>
							
							<div className="flex space-x-2">
								<input
									type="text"
									value={newTag}
									onChange={(e) => setNewTag(e.target.value)}
									onKeyPress={handleTagKeyPress}
									placeholder="Add new tag (comma-separated for multiple)"
									className="flex-1 border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
								/>
								<button
									type="button"
									onClick={handleAddTag}
									className="btn btn-sm btn-secondary rounded-md"
								>
									<Plus className={"size-4"}/>
								</button>
							</div>
							
							<div className="flex flex-wrap gap-2">
								{formData.tags.map((tag, index) => (
									<div
										key={`${tag}-${index}`}
										className="flex items-center bg-gray-100 rounded-full px-3 py-1"
									>
										<span className="text-sm text-gray-700">{tag}</span>
										<button
											type="button"
											onClick={() => handleRemoveTag(tag)}
											className="ml-2 text-gray-500 hover:text-gray-700"
										>
											×
										</button>
									</div>
								))}
							</div>
						</div>
						
						<div className="flex justify-start space-x-4">
							<button
								type="button"
								onClick={onCancel}
								className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
								disabled={isUpdating}
							>
								Cancel
							</button>
							<button
								type="submit"
								className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
								disabled={isUpdating}
							>
								{isUpdating ? 'Saving...' : 'Save'}
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
	);
};

export default TagForm;
