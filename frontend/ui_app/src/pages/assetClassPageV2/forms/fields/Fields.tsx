import React from "react";
import {ChevronDown} from "lucide-react";

import FieldProps from "../../../../components/formElements/fields.interface";

const labelStyles = "block font-semibold text-gray-700 mb-1";
const readOnlyStyles = "bg-base-200 text-neutral-500";
const inputStyles = "w-full p-2 border rounded-md";

export const InputField: React.FC<FieldProps> = ({
	                                                 label, name,
	                                                 value, onChange,
	                                                 placeholder = "",
	                                                 readOnly = false,
	                                                 error
                                                 }) => (
	<div className="flex-1 text-sm ">
		<label htmlFor={name} className={labelStyles}>{label}</label>
		<input
			id={name}
			name={name}
			value={value}
			placeholder={placeholder}
			onChange={onChange}
			readOnly={readOnly}
			className={`${inputStyles} ${readOnly && readOnlyStyles} ${error ? "border-red-500" : ""}`}
		/>
		{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
	</div>
);

interface SelectFieldProps extends FieldProps {
	options: { value: string; label: string }[];
}

export const SelectField: React.FC<SelectFieldProps> = ({
	                                                        label,
	                                                        name,
	                                                        value,
	                                                        onChange,
	                                                        options,
	                                                        readOnly = false,
	                                                        error
                                                        }) => (
	<div className="flex-1 text-sm">
		<label htmlFor={name} className={labelStyles}>{label}</label>
		<div className="relative">
			<select
				id={name}
				name={name}
				value={value}
				onChange={onChange}
				disabled={readOnly}
				className={`w-full p-2 border rounded-md ${readOnly ? "bg-base-200 text-neutral-500" : ""} ${error ? "border-red-500" : ""} appearance-none`}
				style={{WebkitAppearance: "none", MozAppearance: "none"}}
			>
				{options.map((option) => (
					<option key={option.value} value={option.value}>
						{option.label}
					</option>
				))}
			</select>
			<div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
				<ChevronDown className="size-4 text-neutral-500"/>
			</div>
		</div>
		{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
	</div>
);

interface SwitchFieldProps {
	label: string;
	name: string;
	checked: boolean;
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	readOnly?: boolean;
	error?: string;
}

export const SwitchField: React.FC<SwitchFieldProps> = ({label, name, checked, onChange, readOnly = false, error}) => {
	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		// Create a simulated event object that matches the structure
		// of a standard input change event
		const simulatedEvent = {
			target: {
				name: name,
				value: e.target.checked ? 'on' : 'off',
				type: 'checkbox',
				checked: e.target.checked
			}
		} as React.ChangeEvent<HTMLInputElement>;
		
		onChange(simulatedEvent);
	};
	
	return (
		<div className="flex">
			<label htmlFor={name} className="flex items-center cursor-pointer">
				<div className="relative">
					<input
						type="checkbox"
						id={name}
						name={name}
						checked={checked}
						onChange={handleChange}
						disabled={readOnly}
						className="sr-only"
					/>
					<div
						className={`block w-14 h-6 rounded-full ${checked ? 'bg-secondary' : 'bg-base-300'} ${readOnly ? 'opacity-50' : ''}`}
					></div>
					<div
						className={`dot absolute left-1 top-1 bg-white size-4 rounded-full transition ${
							checked ? 'transform translate-x-8' : ''
						}`}
					></div>
				</div>
				<div className="ml-3 text-sm font-semibold text-gray-700">{label}</div>
			</label>
			{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
		</div>
	);
};

interface TextAreaFieldProps extends FieldProps {
	rows?: number;
}

export const TextAreaField: React.FC<TextAreaFieldProps> = ({
	                                                            label,
	                                                            name,
	                                                            value,
	                                                            onChange,
	                                                            placeholder = "",
	                                                            readOnly = false,
	                                                            rows = 4,
	                                                            error
                                                            }) => (
	<div className="flex-1 text-sm">
		<label htmlFor={name} className={labelStyles}>{label}</label>
		<textarea
			id={name}
			name={name}
			value={value}
			placeholder={placeholder}
			onChange={onChange}
			readOnly={readOnly}
			className={`w-full p-2 border rounded-md ${readOnly ? "bg-base-200 text-neutral-500" : ""} ${error ? "border-red-500" : ""}`}
			rows={rows}
		/>
		{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
	</div>
);
