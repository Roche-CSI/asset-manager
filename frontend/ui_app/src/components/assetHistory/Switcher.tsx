import React from 'react';

const Switcher = ({ value, options, setValue, size = 'md' }) => {
	const handleChange = (option) => {
		setValue(option);
	};
	
	const sizeClasses = {
		sm: 'text-xs h-6',
		md: 'text-sm h-8',
		lg: 'text-base h-10',
	};
	
	return (
		<div className="flex rounded-md bg-white">
			{options.map((option, index) => (
				<label key={option} className="">
					<input
						type="radio"
						className="sr-only"
						checked={value === option}
						onChange={() => handleChange(option)}
					/>
					<span
						className={`flex items-center justify-center px-3 ${index % 2 == 0 ? 'rounded-l-md' : 'rounded-r-md'} ${sizeClasses[size]} cursor-pointer transition-colors duration-200 ${
							value === option
								? 'bg-secondary text-white border border-secondary'
								: 'bg-white text-gray-700 hover:bg-gray-100 border border-base-300'
						}`}
					>
            {option}
          </span>
				</label>
			))}
		</div>
	);
};

export default Switcher;
