import React from 'react';
import styles from './searchbar.module.scss';
import {BiSearch} from "react-icons/bi";

export interface SearchBarProps {
    styles?: any;
    searchIcon?: any;
    iconPosition?: "left" | "right";
    placeholder?: string;
    onChange?: Function;
    onSubmit?: Function;
}

export default function ControlledSearchBar(props?: SearchBarProps) {
    const barStyles = props && props.styles ? props.styles : styles;
    const SearchIcon = props && props.searchIcon ? props.searchIcon : BiSearch;
    const iconPosition = props && props.iconPosition ? props.iconPosition : "right";
    const placeholder = props && props.placeholder ? props.placeholder : 'Search here...';

    return (
        <div className={barStyles.searchBar}>
            {iconPosition === "left" ? <div className={barStyles.searchIcon}>
                <SearchIcon onClick={() => {props && props.onSubmit && props.onSubmit()}}/></div> : null}
            <input type="text"
                   placeholder={placeholder}
                   onChange={(e: any) => {props && props.onChange && props.onChange(e.target.value)}}
                   onKeyDown={(e: any) => {
                    console.log(props?.onSubmit)
                    if (e.key === 'Enter') { props && props.onSubmit && props.onSubmit() }
                }} />
            {iconPosition === "right" ? <div className={barStyles.searchIcon}>
                <SearchIcon onClick={() => {props && props.onSubmit && props.onSubmit()}}/></div> : null}
        </div>
    );
}