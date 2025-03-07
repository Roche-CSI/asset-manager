import {Search, X} from "lucide-react";
import React from "react";

interface SearchBarProps {
	searchString: string;
	onSearch: (searchQuery: string) => void;
	inputRef?: React.RefObject<HTMLInputElement>;
}

export const SearchBar: React.FC<SearchBarProps> = ({searchString, onSearch, inputRef}) => {
	const [searchQuery, setSearchQuery] = React.useState<string>(searchString);
	const [error, setError] = React.useState<boolean>(false);
	
	const handleSearch = (e: React.FormEvent) => {
		e.preventDefault();
		if (searchQuery.trim() === '') {
			setError(true);
			return;
		}
		setError(false);
		if (searchQuery !== searchString) {
			onSearch(searchQuery);
		}
	}
	
	const handleClear = () => {
		setSearchQuery('');
		setError(false);
		inputRef?.current?.focus();
	}
	
	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setSearchQuery(e.target.value);
		if (error) setError(false);
	}
	
	return (
		<div className="flex flex-col gap-1">
			<form onSubmit={handleSearch} className="">
				<div
					className={`bg-white flex items-center w-[584px] h-12 rounded-full px-4 transition-all
                    ${error
						? 'border-1 border-red-500 shadow-sm shadow-red-200'
						: 'border border-gray-200 hover:shadow-md focus-within:shadow-md'
					}`}
				>
					<Search className={`mr-3 ${error ? 'text-red-500' : 'text-gray-500'}`} size={20}/>
					<input
						type="text"
						value={searchQuery}
						onChange={handleChange}
						className={`flex-grow outline-none text-lg ${error ? 'placeholder-red-400' : 'placeholder-gray-500'}`}
						placeholder="Search using meta keywords, tags etc."
						ref={inputRef}
					/>
					{searchQuery && (
						<button
							type="button"
							onClick={handleClear}
							className="p-1 hover:bg-gray-100 rounded-full"
							aria-label="Clear search"
						>
							<X className={`size-4 ${error ? 'text-red-500' : 'text-gray-500'}`}/>
						</button>
					)}
				</div>
			</form>
			{error && (
				<span className="text-red-500 text-sm pl-4">
                Please enter a search term
            </span>
			)}
		</div>
	)
}
