import React from 'react';

interface ToggleButtonProps {
    value: string;
    options: string[];
    setValue: (value: string) => void;
    size?: 'sm' | 'md' | 'lg';
}

const ToggleButtons: React.FC<ToggleButtonProps> = ({
                                                        value,
                                                        options,
                                                        setValue,
                                                        size = 'sm'
                                                    }) => {
    const buttonSizeClasses = {
        sm: 'px-2 py-1 text-xs',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base'
    }[size];
    
    return (
        <div className="inline-flex rounded-md shadow-sm" role="group">
            {options.map((option, idx) => {
                const isSelected = value === option;
                const isFirst = idx === 0;
                const isLast = idx === options.length - 1;
                
                return (
                    <button
                        key={idx}
                        type="button"
                        onClick={() => setValue(option)}
                        className={`
                            ${buttonSizeClasses}
                            font-medium
                            focus:outline-none
                            focus:ring-2
                            focus:ring-blue-500
                            focus:z-10
                            transition-colors
                            duration-200
                            ${isSelected
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-white text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                        }
                            ${isFirst
                            ? 'rounded-l-md'
                            : '-ml-px'
                        }
                            ${isLast
                            ? 'rounded-r-md'
                            : ''
                        }
                            ${!isSelected
                            ? 'border border-gray-300 hover:border-gray-400'
                            : 'border border-blue-600'
                        }
                        `}
                    >
                        {option.toUpperCase()}
                    </button>
                );
            })}
        </div>
    );
};

export default ToggleButtons;
