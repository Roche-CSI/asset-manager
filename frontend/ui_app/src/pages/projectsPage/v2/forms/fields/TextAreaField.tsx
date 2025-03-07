import React from "react";
import {FieldProps} from "./InputField.tsx";

const TextAreaField: React.FC<FieldProps> = ({label, name, value, onChange, placeholder="", readOnly = false, error}) => (
	<div className="flex-1 mr-2">
		<label htmlFor={name} className="block text-sm font-semibold text-gray-700 mb-1">{label}</label>
		<textarea
			id={name}
			name={name}
			value={value}
			placeholder={placeholder}
			onChange={onChange}
			readOnly={readOnly}
			className={`w-full p-2 text-xs border rounded-md ${readOnly ? "bg-base-200 text-neutral-500" : ""} ${error ? "border-red-500" : ""}`}
			rows={4}
		/>
		{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
	</div>
);

export default TextAreaField;
