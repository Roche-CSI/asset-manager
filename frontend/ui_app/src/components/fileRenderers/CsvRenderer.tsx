import React from "react";
import { CsvEditor } from "../csvEditor";
import styles from "./csv.module.scss";

interface TableProps {
    content: any;
}

export default function CsvRenderer(props: TableProps) {

    return (
        <div className={styles.csvContainer}>
            <CsvEditor 
                value={props.content}
                readonly={true}
                minCols={1}
                minRows={1}
                colHeaders={true}
                rowHeaders={true}
                filters={true}
                dropdownMenu={true}
                sort={true}
            />
        </div>
    )
}