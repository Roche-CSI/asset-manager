import React from 'react';

interface OptionsFieldProps {
    fieldName: string;
    label: string;
    value: string | boolean;
    description?: string;
    onChange: (value: string | boolean) => void;
    readOnly?: boolean;
    error?: string;
    validated?: boolean;
    options: Array<string | boolean>;
}

const OptionsField: React.FC<OptionsFieldProps> = ({
    fieldName,
    label,
    value,
    description,
    onChange,
    readOnly,
    validated,
    error,
    options
}: OptionsFieldProps) => {
    const isBoolean = typeof options[0] === 'boolean';

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedValue = e.target.value;
        if (isBoolean) {
            onChange(selectedValue === 'true');
        } else {
            onChange(selectedValue);
        }
    };

    return (
        <div className="mb-4 text-left">
            <label className="block text-neutral-800 text-lg font-bold mb-2" htmlFor={fieldName}>
                {label}
            </label>
            <select
                className={`border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline
                    ${validated ? (error ? 'border-red-500' : 'border-green-500') : 'border-gray-300'}`
                }
                id={fieldName}
                value={String(value)}
                onChange={handleChange}
                disabled={readOnly}
            >
                {options.map((option, idx) => (
                    <option value={String(option)} key={idx}>
                        {isBoolean ? (option ? 'true' : 'false') : option.toString()}
                    </option>
                ))}
            </select>
            <p className="mt-2 text-lg text-gray-600">
                {description}
            </p>
            {validated && (
                <div className={`mt-2 ${error ? 'text-red-600' : 'text-green-600'}`}>
                    {error || "Looks good"}
                </div>
            )}
        </div>
    );
}

export default OptionsField;