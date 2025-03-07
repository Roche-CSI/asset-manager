import React from "react";

export interface FieldProps {
	label: string;
	name: string;
	value: string;
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	readOnly?: boolean;
	error?: string;
	placeholder?: string;
}

const InputField: React.FC<FieldProps> = ({label, name, value, onChange, placeholder = "", readOnly = false, error}) => (
	<div className="flex-1 mr-2">
		<label htmlFor={name} className="block text-sm font-semibold text-gray-700 mb-1">{label}</label>
		<input
			id={name}
			name={name}
			value={value}
			onChange={onChange}
			readOnly={readOnly}
			placeholder={placeholder}
			className={`w-full p-2 text-xs border rounded-md ${readOnly ? "bg-base-200 text-neutral-500" : ""} ${error ? "border-red-500" : ""}`}
		/>
		{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
	</div>
);



export default InputField;
