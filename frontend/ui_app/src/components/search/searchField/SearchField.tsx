import React from "react";
import { SearchBar, SearchBarProps } from "../searchBar";
import ControlledSearchBar from "../searchBar/ControlledSearchBar";
import defaultStyles from "./search.module.scss";


export default function SearchField(props?: SearchBarProps) {
    const styles = props?.styles || defaultStyles
    
    if (props && props.controlled) {
        return <ControlledSearchBar 
            styles={styles}
            iconPosition={(props && props.iconPosition) || "left"}
            placeholder={props && props.placeholder}
            onChange={props && props.onChange}
            onSubmit={props && props.onSubmit} />
    }

    return <SearchBar styles={styles}
                      iconPosition={"left"}
                      placeholder={props && props.placeholder}
                      onChange={props && props.onChange}/>
}