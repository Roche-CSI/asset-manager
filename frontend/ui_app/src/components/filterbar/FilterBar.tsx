/* eslint-disable no-mixed-spaces-and-tabs */
import React, {ChangeEvent, useState} from 'react';

export const ResetIcon = ({ className = "size-5" }: { className?: string }) => {
	return (
		<svg xmlns="http://www.w3.org/2000/svg"
			// height="24px"
			 viewBox="0 -960 960 960"
			 width="24px"
			 fill="#5f6368"
			 className={className}>
			<path
				d="M442.12-150.54q-110.31-13.81-182.58-96.48-72.27-82.67-72.27-193.79 0-60.8 24.48-116.13t68.67-96.52l40.04 39.84q-38.15 33-57.69 77.83t-19.54 94.98q0 87.69 55.94 154 55.95 66.31 142.95 80.31v55.96Zm75.96.77v-55.96q86.11-16.54 142.65-82.25 56.54-65.71 56.54-152.83 0-98.88-69.19-168.07-69.2-69.2-168.08-69.2h-15.77l55.62 55.62-39.23 39.42-122.93-122.92 122.93-122.92 39.23 39.23-55.62 55.61H480q122.31 0 207.77 85.46 85.46 85.47 85.46 207.77 0 110.81-72.71 193.19-72.71 82.39-182.44 97.85Z" />
		</svg>
	)
}


// Define the props for the TopBar component
interface BarProps<T> {
	label?: React.ReactNode;
	onSearch: (searchTerm: T) => void;
	onKeyPress?: (searchTerm: string) => void;
	onRightButtonClick?: () => void;
	onReset?: () => void;
	placeholder: string;
	rightButton?: React.ReactNode;
	// rightButtonLabel?: string;
	// rightButtonIcon?: React.ReactNode;
}

// The TopBar component
export const FilterBar = <T, >({
	                                      label,
	                                      onSearch,
										  onKeyPress,
	                                      placeholder,
	                                      rightButton,
                                      }: BarProps<T>) => {
	
	const [inputValue, setInputValue] = useState<string>('');
	
	const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
		const value = e.target.value;
		setInputValue(value);
		onSearch && onSearch(value as unknown as T);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === 'Enter' && onKeyPress) {
			const currentValue = (e.target as HTMLInputElement).value;
			onKeyPress(currentValue);
		}
	}
	
	const handleReset = () => {
		setInputValue('');
		onSearch && onSearch('' as unknown as T);
	};
	
	return (
		<div className="basis-3/4 flex flex-wrap gap-2 self-start mb-4 text-neutral">
			<div className="flex items-center justify-center gap-2 mr-auto">
				{label}
				<input
					type="text"
					placeholder={placeholder}
					className="input input-bordered h-8 w-96 rounded-md text-xs"
					value={inputValue}
					onChange={handleInputChange}
					onKeyDown={handleKeyDown}
				/>
				<button className="btn btn-ghost btn-sm rounded-full p-1" onClick={handleReset}>
					<ResetIcon className="h-5 w-5"/>
				</button>
			</div>
			{/* FILTER BAR END */}
			{rightButton}
		</div>
	);
};

