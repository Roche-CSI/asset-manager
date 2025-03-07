import {Dropdown, DropdownButton} from "react-bootstrap";
import React, {useEffect, useState} from "react";
import {isEmptyObject} from "../../../utils";

interface DropDownOption {
    eventKey: any
    value: any
}

interface DropDownProps {
    options: DropDownOption[];
    onSelect?: Function;
}

function DropDownMenu(props: DropDownProps) {
    const [active, setActive] = useState({});
    let items = props.options.map(
        (item, idx) => <Dropdown.Item key={idx} eventKey={item.eventKey}> {item.value}</Dropdown.Item>);
    const handleSelect=(e: any) => {
        for (let option of props.options) {
            if (option.eventKey === e) {
                setActive({...active, ...option})
            }
        }
        props.onSelect && props.onSelect(e);
    }
    let title = (!isEmptyObject(active)) ? (active as DropDownOption).value : props.options.length > 0 ? props.options[0].value : "";
    return (
        <DropdownButton title={title} onSelect={handleSelect}>
            {items}
        </DropdownButton>
    )
}
export default DropDownMenu;