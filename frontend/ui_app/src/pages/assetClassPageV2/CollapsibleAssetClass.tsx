import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Edit, Save, X, FileText } from 'lucide-react';

const CollapsibleAssetClass = ({ assetClass, onSave, onShowReadme }) => {
	const [isExpanded, setIsExpanded] = useState(false);
	const [isEditing, setIsEditing] = useState(false);
	const [editedAssetClass, setEditedAssetClass] = useState(assetClass);
	
	const toggleExpand = () => setIsExpanded(!isExpanded);
	
	const handleEdit = () => {
		setIsEditing(true);
		setIsExpanded(true);
	};
	
	const handleCancel = () => {
		setIsEditing(false);
		setEditedAssetClass(assetClass);
	};
	
	const handleSave = () => {
		onSave(editedAssetClass);
		setIsEditing(false);
	};
	
	const handleInputChange = (e) => {
		const { name, value } = e.target;
		setEditedAssetClass(prev => ({ ...prev, [name]: value }));
	};
	
	const renderContent = () => {
		if (!editedAssetClass) {
			return null;
		}
		if (isEditing) {
			return (
				<div className="bg-white border border-base-300 rounded-lg p-6 relative">
					<div className="flex mb-4">
						<div className="flex-1 mr-2">
							<label htmlFor="title" className="block font-semibold text-gray-700 mb-1">Title</label>
							<input
								id="title"
								name="title"
								value={editedAssetClass.title}
								onChange={handleInputChange}
								className="w-full p-2 border rounded"
							/>
						</div>
						<div className="flex-1 mr-2">
							<label htmlFor="type" className="block font-semibold text-gray-700 mb-1">Type</label>
							<input
								id="type"
								name="type"
								value={editedAssetClass.type}
								onChange={handleInputChange}
								className="w-full p-2 border rounded"
							/>
						</div>
						<div className="flex-1">
							<label htmlFor="id" className="block font-semibold text-gray-700 mb-1">ID</label>
							<input
								id="id"
								name="id"
								value={editedAssetClass.id}
								onChange={handleInputChange}
								className="w-full p-2 border rounded"
							/>
						</div>
					</div>
					<div>
						<label htmlFor="description" className="block font-semibold text-gray-700 mb-1">About</label>
						<textarea
							id="description"
							name="description"
							value={editedAssetClass.description}
							onChange={handleInputChange}
							className="w-full p-2 border rounded"
							rows="4"
						/>
					</div>
					<div className="mt-4 flex justify-end space-x-2">
						<button
							onClick={handleCancel}
							className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
						>
							Cancel
						</button>
						<button
							onClick={handleSave}
							className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
						>
							Save
						</button>
					</div>
				</div>
			);
		}
		
		return (
			<div className="bg-white border border-base-300 rounded-lg p-6 relative">
				<button
					onClick={handleEdit}
					className="absolute btn-ghost top-4 right-4 text-blue-500 hover:text-blue-600"
					aria-label="Edit"
				>
					<Edit className="w-5 h-5" />
				</button>
				<div className="flex mb-4">
					<div className="flex-1">
						<h3 className="font-semibold text-gray-700">Title</h3>
						<p>{assetClass.title}</p>
					</div>
					<div className="flex-1">
						<h3 className="font-semibold text-gray-700">Type</h3>
						<p>{assetClass.type || "General"}</p>
					</div>
					<div className="flex-1">
						<h3 className="font-semibold text-gray-700">ID</h3>
						<p>{assetClass.id}</p>
					</div>
				</div>
				<div>
					<h3 className="font-semibold text-gray-700 mb-2">About</h3>
					<p className="text-gray-600 whitespace-pre-wrap">{assetClass.description}</p>
				</div>
			</div>
		);
	};
	
	if (!assetClass) {
		return null;
	}
	
	return (
		<div className=''>
			<div className="flex items-center justify-between w-full">
				<div
					onClick={toggleExpand}
					className="flex items-center text-left cursor-pointer"
				>
					<h2 className="text-2xl font-bold text-neutral-500 mr-2 mt-6">
						{assetClass.title.normalize(" ").toTitleCase()}
					</h2>
					{isExpanded ? (
						<ChevronUp className="w-6 h-6 text-neutral-500 mt-6" />
					) : (
						<ChevronDown className="w-6 h-6 text-neutral-500 mt-6" />
					)}
				</div>
				<div className="flex items-center mt-6 space-x-4">
					<span className="text-sm text-gray-500 font-semibold ml-10">
						Last Updated: {assetClass.modified_at} GMT
					</span>
					<button
						onClick={onShowReadme}
						className="btn btn-sm rounder-lg btn-ghost hover:bg-white hover:text-primary hover:underline"
						aria-label="Show README">
						<FileText className="w-4 h-4 mr-1" />README.md
					</button>
				</div>
			</div>
			{isExpanded && (
				<div className="pt-4 transition-all duration-300 ease-in-out">
					{renderContent()}
				</div>
			)}
		</div>
	);
};

export default CollapsibleAssetClass;
