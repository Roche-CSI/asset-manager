import React, { useCallback } from 'react';
import styles from './searchbar.module.scss';
import {BiSearch} from "react-icons/bi";
import { debounce } from '../../../utils';

export interface SearchBarProps {
    styles?: any;
    searchIcon?: any;
    iconPosition?: "left" | "right";
    placeholder?: string;
    onChange?: Function;
    onSubmit?: Function;
    controlled?: boolean;
}

export default function SearchBar(props?: SearchBarProps) {
    const barStyles = props && props.styles ? props.styles : styles;
    const SearchIcon = props && props.searchIcon ? props.searchIcon : BiSearch;
    const iconPosition = props && props.iconPosition ? props.iconPosition : "right";
    const placeholder = props && props.placeholder ? props.placeholder : 'Search here...';

    const setKeyword = (val: string) => {
        // console.log(val)
        props && props.onChange && props.onChange(val)
    };

    const debouncedSetKeyword = useCallback(debounce(setKeyword, 500), [debounce]);

    return (
        <div className={barStyles.searchBar}>
            {iconPosition === "left" ? <div className={barStyles.searchIcon}><SearchIcon/></div> : null}
            <input type="text"
                   placeholder={placeholder}
                   onChange={(e) => debouncedSetKeyword(e.target.value)}/>
            {iconPosition === "right" ? <div className={barStyles.searchIcon}><SearchIcon/></div> : null}
        </div>
    );
}