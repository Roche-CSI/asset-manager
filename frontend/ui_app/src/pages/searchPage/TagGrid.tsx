/* eslint-disable no-mixed-spaces-and-tabs */
import React, {ChangeEvent, useState} from 'react';
import {RotateCcw} from "lucide-react";
import {TagCategory, Tag} from "./taggable";
import {useFilter} from "./useFilter";


interface TagGridProps {
	groupName: string;
	data: TagCategory[];
	onSelectedTagsChange?: (categories: TagCategory[]) => void;
	showFilterBar?: boolean;
}

interface Category extends TagCategory {
	filtered?: Tag[];
	selected?: Record<string, Tag>;
}

export const TagGrid = ({
	                        groupName,
	                        data,
	                        onSelectedTagsChange,
	                        showFilterBar = true
                        }: TagGridProps) => {
	
	const handleTagSelection = (category: Category) => {
		// Add or update category with selected tags
		const updated: TagCategory[] = []
		data.forEach((cat) => {
			if (cat.name === category.name) {
				updated.push(category);
			} else {
				updated.push(cat);
			}
		});
		
		onSelectedTagsChange && onSelectedTagsChange(updated);
	};
	
	const {items, handleSearch, resetSearch} = useFilter<TagCategory,string>({
		data: data || [],
		filterFunction: filterTags,
	});
	
	const handleReset = () => {
		const updatedCategories: Record<string, Category> = {...selectedCategories};
		Object.values(updatedCategories).forEach(category => {
			category.selected = {};
		});
		resetSearch();
		setSelectedCategories(updatedCategories);
		onSelectedTagsChange && onSelectedTagsChange([]);
	}
	
	return (
		<React.Fragment>
			{
				showFilterBar &&
				<TagFilterBar
					placeholder="Search tags"
					handleSearch={handleSearch}
					resetSearch={handleReset}
				/>
			}
			{items.map((category: TagCategory, index: number) => (
				<CategoryCard
					key={index}
					category={category}
					onTagSelectedChange={handleTagSelection}
				/>
			))}
		</React.Fragment>
	);
};


// Define the props interface
interface TagCardProps {
	category: Category;
	onTagSelectedChange?: (category: Category) => void;
}

// Define the TagCard component
const CategoryCard: React.FC<TagCardProps> = ({category, onTagSelectedChange}) => {
	// Initialize the state with a dictionary where each tag is set to false
	
	// Handle tag click to add or remove tag from selected tags
	const handleTagClick = (tag: Tag) => {
		if (!category.selected) {
			category.selected = {};
		}
		if (tag.name in category.selected) {
			delete category.selected[tag.name];
		} else {
			category.selected[tag.name] = tag;
		}
		// Notify parent component about the change
		onTagSelectedChange && onTagSelectedChange(category);
	}
	
	const tags = category.filtered || category.tags;
	return (
		<React.Fragment>
			<h5 className="font-medium text-neutral-400 mt-4 mb-2 text-xs">
				{category.name}
			</h5>
			<div className="gap-x-8 gap-y-4 space-y-2">
				{
					tags.map((tag, index) => {
						const selected = category.selected ? Object.keys(category.selected).includes(tag.name) : false;
						return (
							<button
								key={index}
								className={`btn btn-xs rounded-md mr-1 font-medium ${selected ? 'bg-secondary text-base-100 hover:bg-primary' : 'text-base-content hover:bg-base-300'}`}
								onClick={() => handleTagClick(tag)}
							>
								<span>{tag.label}</span>
								{/*{selected && <XIcon className="h-4 w-4"/>}*/}
							</button>
						);
					})}
			</div>
		</React.Fragment>
	);
};

// interface for TagFilterBar
interface TagFilterBarProps {
	placeholder: string;
	handleSearch: (search: string) => void;
	resetSearch?: () => void;
}

export const TagFilterBar = ({ placeholder, handleSearch, resetSearch }: TagFilterBarProps) => {
	const [inputValue, setInputValue] = useState('');
	
	const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
		const value = e.target.value;
		setInputValue(value);
		handleSearch(value);
	};
	
	const handleReset = () => {
		setInputValue('');
		if (resetSearch) resetSearch();
		handleSearch(''); // Clear the search results as well
	};
	
	return (
		<div className="flex gap-1">
			<div className="flex gap-1">
				<label className="input input-bordered rounded-md flex items-center gap-2 h-8 grow flex-1 px-2 w-9/12">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						className="h-4 w-4 opacity-70">
						<path
							fillRule="evenodd"
							d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z"
							clipRule="evenodd" />
					</svg>
					<input type="text" className="grow" placeholder={placeholder} value={inputValue}
					       onChange={handleInputChange}/>
				</label>
				{
					inputValue &&
                    <button className="btn btn-square btn-ghost btn-sm"
                            onClick={handleReset}>
                        <RotateCcw className={"size-6"} />
                    </button>
				}
			</div></div>
	);
};

// Function to filter models based on user input

const filterTags = (query: string, data: Category[]): Category[] => {
	// Convert the query to lowercase for case-insensitive matching
	const lowerQuery = query.toLowerCase();
	
	// Filtered categories
	const filteredData: Category[] = [];
	
	data.forEach((category: Category) => {
		// Filter tags based on query
		const filteredTags = category.tags.filter(tag =>
			tag.name.toLowerCase().includes(lowerQuery)
		);
		
		// Update the category with filtered tags if any
		if (filteredTags.length > 0) {
			filteredData.push({
				...category,
				filtered: filteredTags
			});
		}
	});
	
	return filteredData;
};

