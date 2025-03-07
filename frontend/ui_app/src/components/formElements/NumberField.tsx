import React, { ChangeEvent } from 'react';

import FieldProps from './fields.interface';

interface NumberFieldProps extends FieldProps {
    fieldName: string;
    label: string;
    value: number;
    description?: string;
    onChange: (value: string | number) => void;
    readOnly?: boolean;
    error?: string;
    validated?: boolean;
    className?: string;
}

const NumberField: React.FC<NumberFieldProps> = ({
    fieldName,
    label,
    value,
    description,
    onChange,
    readOnly,
    validated,
    error
}: NumberFieldProps) => {
    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const inputValue = e.target.value;
        // Check if the input value is empty
        if (inputValue === "") {
            onChange("");
        } else {
            // Convert the string value to a number
            const numericValue = parseFloat(inputValue);
            onChange(numericValue);
        }
    };

    return (
        <div className="mb-4 text-left">
            <label className="block text-neutral-800 text-lg font-bold mb-2" htmlFor={fieldName}>
                {label}
            </label>
            <input
                className={`border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline 
                    ${validated ? (error ? 'border-red-500' : 'border-green-500') : 'border-gray-300'}`}
                id={fieldName}
                type="number"
                value={value}
                onChange={handleChange}
                readOnly={readOnly}
            />
            <p className="mt-2 text-lg text-gray-600">
                {description}
            </p>
            {validated && (
                <div className={`mt-2 ${error ? 'text-red-600' : 'text-green-600'}`}>
                    {error || "Looks good"}
                </div>
            )}
        </div>
    )
}

export default NumberField;