import React, { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";
import { DataState } from "../../components/commonHooks/useLoadingState";
import Spinner from "../../components/spinner/Spinner";

export const repos = [
    { value: 'asset_client', label: 'Command Line Interface' },
    { value: 'asset_dashboard', label: 'Dashboard UI' },
];

export default function IssueTrackerFormV2({ onSubmit, onFieldChanged, title, description, validated, 
    loadingState,
    errors = {} }) {
    const [formErrors, setFormErrors] = useState({});
    const [isValidated, setIsValidated] = useState(false);
    
    useEffect(() => {
        setFormErrors({ ...errors });
        setIsValidated(validated);
    }, [errors, validated]);
    
    function handleSubmit(event) {
        event.preventDefault();
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            setIsValidated(true);
        } else {
            onSubmit(event);
        }
    }
    
    return (
        <form onSubmit={handleSubmit} className="bg-white p-6 border border-slate-300 rounded-lg">
            <div className="mb-6">
                <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-1">Title</label>
                <input
                    id="title"
                    type="text"
                    placeholder="Enter Summary"
                    value={title}
                    onChange={(e) => onFieldChanged(e, "title")}
                    className={`w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        formErrors.title ? 'border-red-500' : 'border-gray-300'
                    }`}
                    required
                />
                {formErrors.title && <p className="mt-1 text-sm text-red-500">{formErrors.title}</p>}
            </div>
                        
            <div className="mb-6">
                <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-1">Description</label>
                <textarea
                    id="description"
                    placeholder="Enter Issue Description"
                    value={description}
                    onChange={(e) => onFieldChanged(e, "description")}
                    rows={6}
                    className={`w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        formErrors.description ? 'border-red-500' : 'border-gray-300'
                    }`}
                    required
                />
                {formErrors.description && <p className="mt-1 text-sm text-red-500">{formErrors.description}</p>}
            </div>
            
            {formErrors.unknown && (
                <div className="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700">
                    <div className="flex">
                        <AlertCircle className="h-5 w-5 mr-2" />
                        <p>An unknown error occurred. Please try again.</p>
                    </div>
                </div>
            )}
            
            {loadingState.data_state === DataState.fetching ? <Spinner message={"Submitting..."} />
            :
                <div className="flex justify-center">
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Submit
                </button>
                </div>
            }
        </form>
    );
}
