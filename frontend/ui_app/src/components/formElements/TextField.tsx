import React from 'react';

import FieldProps from './fields.interface';

interface TextFieldProps extends FieldProps{
    fieldName: string;
    label: string;
    value: string;
    description?: string;
    onChange: (value: string | number | null) => void;
    readOnly?: boolean;
    error?: string | null;
    validated?: boolean;
    className?: string;
}

const TextField: React.FC<TextFieldProps> = ({
    fieldName,
    label,
    value,
    description,
    onChange,
    readOnly,
    validated,
    error
}: TextFieldProps) => {
    return (
        <div className="mb-4 text-left">
            <label className="block text-neutral-800 text-lg font-bold mb-2" htmlFor={fieldName}>
                {label}
            </label>
            <input
                className={`border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline 
                    ${validated ? (error ? 'border-red-500' : 'border-green-500') : 'border-gray-300'}`}
                id={fieldName}
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
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

export default TextField;