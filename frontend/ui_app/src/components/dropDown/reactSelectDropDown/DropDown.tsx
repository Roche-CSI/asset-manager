import React, { Component } from 'react'
import Select from 'react-select'
import styles from "./dropdown.module.scss";

// const options = [
//     { value: 'chocolate', label: 'Chocolate' },
//     { value: 'strawberry', label: 'Strawberry' },
//     { value: 'vanilla', label: 'Vanilla' }
// ]

interface Option {
    value: string,
    label: any
}

interface DropDownProps {
    options?: Option[];
    onChange?: Function;
    active?: Option;
    className?: string; // css classname for custom styling
}

export default function DropDown(props: DropDownProps) {
    const active: any = {
        value: props.active && props.active.value,
        label: props.active && props.active.label
    };
    const customStyles = {
        control: (base: any) => ({
            ...base,
            height: 35,
            minHeight: 35
        })
    };
    const className = props.className || "";
    return (
        <div>
            <Select options={props.options}
                    classNames={{
                        control: () => className,
                    }}
                    value={active}
                    onChange={(option) => props.onChange && props.onChange(option)}/>
        </div>

    )
}

