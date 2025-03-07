import React from 'react';
import CodeEditor from '../codeEditor/CodeEditor';

interface FileFieldProps {
    fieldName: string;
    label: string;
    value: string;
    description?: string;
    onFieldChanged: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onChange: (value: string) => void;
    readOnly?: boolean;
    error?: string;
    validated?: boolean;
    height?: number;
    language?: string;
    className?: string;
}

const FileField: React.FC<FileFieldProps> = ({
    fieldName,
    label,
    value,
    description,
    onFieldChanged,
    onChange,
    readOnly,
    validated,
    error,
    height,
    language,
    className
}: FileFieldProps) => {
    return (
        <div className="mb-4 text-left">
            <label className="block text-neutral-800 text-lg font-bold mb-2" htmlFor="graph_yaml">
                {label}
            </label>
            <div className=''>
                <input
                    className={`border-x-2 border-t-2 rounded-t-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${error ? 'border-red-500' : ''}`}
                    id={fieldName}
                    type="file"
                    disabled={readOnly}
                    onChange={(e) => onFieldChanged(e)}
                />
                <CodeEditor
                    className={`w-full border-2 rounded-b 
                        ${validated ? (error ? 'border-red-500' : 'border-green-500') : 'border-gray-300'}`
                    }
                    height={height || 350}
                    language={language || "yaml"}
                    value={value}
                    onChange={(text: string) => onChange(text)}
                    readonly={readOnly}
                />
            </div>
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

export default FileField;