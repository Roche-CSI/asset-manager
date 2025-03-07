import React from 'react';

interface buttonsGroupProps {
    value: string;
    options: string[];
    onClick: Function;
    className?: any;
}

const ButtonsGroup = (props: buttonsGroupProps) => {
    const leftButtonClassName: string = 'inline-flex rounded-l-lg border border-stroke py-1 px-2 font-medium text-black hover:!border-primary hover:bg-primary hover:text-white dark:hover:border-primary sm:py-3 sm:px-6'
    const middleButtonClassName: string = 'inline-flex border-y border-stroke py-1 px-2 font-medium text-black hover:!border-primary hover:bg-primary hover:text-white dark:border-strokedark dark:text-white dark:hover:border-primary sm:py-3 sm:px-6'
    const rightButtonClassName: string = 'inline-flex rounded-r-lg border border-stroke py-1 px-2 font-medium text-black hover:!border-primary hover:bg-primary hover:text-white dark:border-strokedark dark:text-white dark:hover:border-primary sm:py-3 sm:px-6'

    return (
        <div className='flex items-center rounded-lg'>
            {props.options.map((option: string, idx: number) => {
                const positionClassName: string = idx === 0 ? leftButtonClassName : idx === props.options.length - 1 ? rightButtonClassName : middleButtonClassName
                const isActive: boolean = props.value === option;
                return (
                    <button onClick={() => props.onClick(option)}
                        key={idx}
                        className={`${positionClassName} ${isActive && '!border-primary !bg-primary !text-white'} ${props.className && props.className}`}>
                        {option}
                    </button>
                )
            }
            )}
        </div>
    )
}

export default ButtonsGroup;
