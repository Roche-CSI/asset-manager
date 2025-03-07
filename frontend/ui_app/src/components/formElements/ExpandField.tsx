import React, { useState } from 'react';

interface ExpandFieldProps {
    label: string;
    children: React.ReactNode;
}

const ExpandField = ({
    label,
    children
}: ExpandFieldProps) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="w-full">
            <div className='flex flex-row justify-start my-3'>
                <div className='text-lg font-bold text-primary'>
                    {label}
                </div>
                <div className="flex justify-end items-center cursor-pointer">
                    <div
                        onClick={() => setIsOpen(!isOpen)}
                        aria-expanded={isOpen}
                        aria-label="show more"
                        className="ml-2 focus:outline-none"
                    >
                        {isOpen ? (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                            </svg>
                        ) : (
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        )}
                    </div>
                </div>
            </div>
            <div className={`${isOpen ? 'opacity-100 visible static' : 'absolute opacity-0 invisible'} transition-opacity duration-500 ease-in-out`}>
                {children}
            </div>
        </div>
    );
};

export default ExpandField;