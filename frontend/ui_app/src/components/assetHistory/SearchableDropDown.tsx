import React, {useState, useEffect, useRef} from 'react';
import {ChevronDown, Search, X} from 'lucide-react';

export const SearchableDropdown = ({options, onSelect, placeholder = "Select an option"}) => {
	const [isOpen, setIsOpen] = useState(false);
	const [searchTerm, setSearchTerm] = useState('');
	const [selectedOption, setSelectedOption] = useState(null);
	const dropdownRef = useRef(null);
	
	const filteredOptions = options.filter(option =>
		option.label.toLowerCase().includes(searchTerm.toLowerCase())
	);
	
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
				setIsOpen(false);
			}
		};
		
		document.addEventListener('mousedown', handleClickOutside);
		return () => {
			document.removeEventListener('mousedown', handleClickOutside);
		};
	}, []);
	
	const handleSelect = (option) => {
		setSelectedOption(option);
		setIsOpen(false);
		setSearchTerm('');
		onSelect(option);
	};
	
	const handleKeyDown = (e) => {
		if (e.key === 'Escape') {
			setIsOpen(false);
		}
	};
	
	return (
		<div className="relative w-32" ref={dropdownRef}>
			<div
				className="border border-gray-300 rounded-md p-1 flex items-center justify-between cursor-pointer"
				onClick={() => setIsOpen(!isOpen)}
			>
        <span className="truncate">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
				<ChevronDown className={`w-5 h-5 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}/>
			</div>
			
			{isOpen && (
				<div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
					<div className="p-2">
						<div className="relative">
							<Search
								className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5"/>
							<input
								type="text"
								className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
								placeholder="Search..."
								value={searchTerm}
								onChange={(e) => setSearchTerm(e.target.value)}
								onKeyDown={handleKeyDown}
							/>
							{searchTerm && (
								<button
									className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
									onClick={() => setSearchTerm('')}
								>
									<X className="w-4 h-4"/>
								</button>
							)}
						</div>
					</div>
					<ul className="max-h-60 overflow-auto">
						{filteredOptions.map((option) => (
							<li
								key={option.value}
								className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
								onClick={() => handleSelect(option)}
							>
								{option.label}
							</li>
						))}
						{filteredOptions.length === 0 && (
							<li className="px-4 py-2 text-gray-500">No results found</li>
						)}
					</ul>
				</div>
			)}
		</div>
	);
};

// Demo component to showcase the SearchableDropdown
const SearchableDropdownDemo = () => {
	const [selectedOption, setSelectedOption] = useState(null);
	
	const options = [
		{value: 'react', label: 'React'},
		{value: 'vue', label: 'Vue.js'},
		{value: 'angular', label: 'Angular'},
		{value: 'svelte', label: 'Svelte'},
		{value: 'nextjs', label: 'Next.js'},
		{value: 'nuxtjs', label: 'Nuxt.js'},
		{value: 'gatsby', label: 'Gatsby'},
		{value: 'ember', label: 'Ember.js'},
		{value: 'backbone', label: 'Backbone.js'},
		{value: 'jquery', label: 'jQuery'},
		{value: 'preact', label: 'Preact'},
		{value: 'alpinejs', label: 'Alpine.js'},
		{value: 'lit', label: 'Lit'},
		{value: 'meteor', label: 'Meteor'},
		{value: 'aurelia', label: 'Aurelia'},
	];
	
	const handleSelect = (option) => {
		setSelectedOption(option);
		console.log('Selected:', option);
	};
	
	return (
		<div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md space-y-4">
			<h1 className="text-2xl font-bold text-gray-900">Searchable Dropdown Demo</h1>
			<p className="text-gray-500">Select your favorite JavaScript framework or library:</p>
			<SearchableDropdown
				options={options}
				onSelect={handleSelect}
				placeholder="Choose a framework"
			/>
			{selectedOption && (
				<div className="mt-4 p-4 bg-blue-100 rounded-md">
					<p className="text-blue-800">You selected: {selectedOption.label}</p>
				</div>
			)}
		</div>
	);
};

// export default SearchableDropdownDemo;
