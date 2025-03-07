import React from "react";
import CsvEditor from "./CsvEditor";
import { splitNewLineSeparatedString, joinNewLineSeparatedString } from "./csvUtils";

interface Props {
    value: any;
    onChange?: Function;
    className?: string;
    readonly?: boolean;
    minCols? : number;
    minRows?: number;
    minSpareRows?: string;
    strech? : boolean;
    convertFunction? : Function;
    convertToStringFunction?: Function;
}

export default function CsvEditorWrapper(props: Props) {
    const convertFunction: Function = props.convertFunction?? splitNewLineSeparatedString;
    let value: string;
    if (typeof props.value == "string") {
        value = props.value
    } else {
        value = props.convertToStringFunction? props.convertToStringFunction(props.value)
            : joinNewLineSeparatedString(props.value);
    }

    const onValueChange = (value?: string) => {
        if (typeof props.value === "string") return props.onChange;
        const newValue: any = convertFunction(value)
        props.onChange && props.onChange(newValue);
    }
    
    return (
        <CsvEditor value={value}
                   onChange={onValueChange}
                   className={props.className}
                   readonly={props.readonly}
                   minCols={props.minCols}
                   minRows={props.minRows}
                   minSpareRows={props.minSpareRows}
                   stretch={props.strech}
                   />
    )
}