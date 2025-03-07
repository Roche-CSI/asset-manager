import React, { useRef, useState } from "react";
import styles from "./dropdown.module.scss";
import {MenuItem} from "../../common";
import { useOutsideClick } from "../../commonHooks";

interface BadgeDropDownProps {
    icon?: any;
    badge?: any
    customToggle?: Function,
    contentData?: any[],
    renderItems?: Function,
    renderFooter?: Function
}

export default function BadgedDropDown(props: BadgeDropDownProps) {
    const dropdownEl = useRef(null)
    const [show, setShow] = useState(false)

    const handleClick = () => {
        setShow(!show)
    }
    
    const handleOutsideClick = () => {
        if (show) {
            setShow(false);
        }
    }

    useOutsideClick(dropdownEl, handleOutsideClick)

    return (
        <div ref={dropdownEl} className="">
            {dropButton(props)}
            <div className={`${styles.dropdownContent} ${show? styles.active: ''}`}>
                {content(props)}
                {footer(props)}
            </div>
        </div>
    );

    function dropButton(props: BadgeDropDownProps) {
        return (
            <button onClick={handleClick} className="">
                {props.icon ? <div className={styles.dropdownToggleIcon}>{props.icon}</div> : ""}
                {props.badge ? <span className={styles.dropdownToggleBadge}>{props.badge}</span> : ""}
                {props.customToggle ? props.customToggle() : ""}
            </button>
        )
    }

    function content(props: BadgeDropDownProps) {
        const contentData = props.contentData;
        const renderItems = props.renderItems;
        return (contentData && renderItems) ? contentData.map((item, index) => renderItems(item, index)) : null;
    }

    function footer(props: BadgeDropDownProps) {
        return (
            props.renderFooter ? (
                <div className={styles.dropdownFooter}>
                    {props.renderFooter()}
                </div>
            ) : ''
        )
    }



}
