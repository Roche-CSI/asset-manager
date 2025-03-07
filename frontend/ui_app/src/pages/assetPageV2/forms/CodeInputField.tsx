import React from 'react';
import CodeEditor from 'components/codeEditor/CodeEditor';

interface FieldProps {
	label: string;
	name: string;
	value: string;
	placeholder?: string;
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	readOnly?: boolean;
	error?: string;
	language?: string;
}

const CodeInputField: React.FC<FieldProps> = ({
	                                              label,
	                                              name,
	                                              value,
	                                              placeholder,
	                                              onChange,
	                                              readOnly = false,
	                                              error,
	                                              language = 'plaintext'
                                              }) => {
	return (
		<div className="mb-4">
			<label
				className="block text-gray-700 text-md font-semibold mb-2"
				htmlFor={name}>{label}
			</label>
			<div className="border border-base-300 rounded-md">
				<CodeEditor
					value={value}
					onChange={onChange}
					readOnly={readOnly}
					language={language}
					placeholder={placeholder}
					className={`w-full ${error ? 'border-red-500' : ''}`}
					name={name}
				/>
			</div>
			{error && (
				<div className="mt-2 text-red-600">
					{error}
				</div>
			)}
		</div>
	);
};

export default CodeInputField;
