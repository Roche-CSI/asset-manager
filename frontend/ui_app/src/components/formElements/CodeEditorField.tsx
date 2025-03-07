import React from 'react';
import CodeEditor from '../codeEditor/CodeEditor';

interface CodeEditorFieldProps {
    fieldName: string;
    label: string;
    value: string;
    description?: string;
    onChange: (value: string) => void;
    readOnly?: boolean;
    error?: string;
    validated?: boolean;
    height?: number;
    language?: string;
    className?: string;
}

const CodeEditorField: React.FC<CodeEditorFieldProps> = ({
    fieldName,
    label,
    value,
    description,
    onChange,
    readOnly,
    validated,
    error,
    height,
    language,
    className
}: CodeEditorFieldProps) => {
    return (
        <div className="mb-4 text-left">
            <label className={`block text-neutral-800 text-lg font-bold mb-2 ${className}`} htmlFor={fieldName}>
                {label}
            </label>
            <CodeEditor
                className={`w-full pt-1 border rounded-b-md ${validated ? (error ? 'border-red-500' : 'border-green-500') : 'border-gray-300'
                        }`}
                height={height || 200}
                language={language || "json"}
                value={value}
                onChange={(text: string) => onChange(text)}
                readonly={readOnly}
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

export default CodeEditorField;