import React, { useState } from "react";
import CopyAllIcon from '@mui/icons-material/CopyAll';
import CheckIcon from '@mui/icons-material/Check';
import defaultStyles from "./copy.module.scss";

interface CopyProps {
    textToCopy: string;
    Icon?: any;
    tooltip?: string;
    styles?: any;
}

export default function CopyButton(props: CopyProps) {
    const [copied, setCopied] = useState(false);

    const onClick = () => {
        navigator.clipboard.writeText(props.textToCopy)
        if (!copied) {
            setCopied(true)
            setTimeout(() => setCopied((copied) => !copied), 2000);
        }
    }

    const styles: any = props.styles ? props.styles : defaultStyles;
    return (
        <div className={styles.copyButton} onClick={onClick}>
            {!copied ?
                <div>
                    {props.Icon ?
                        <props.Icon className={defaultStyles.copyIcon} /> :
                        <CopyAllIcon className={defaultStyles.copyIcon} />
                    }
                    <div className={defaultStyles.tooltip}>
                        <span className={defaultStyles.tooltipText}>
                            {props.tooltip ?? "Copy raw contents"}
                        </span>
                    </div>
                </div>
                :
                <div>
                    <CheckIcon className={defaultStyles.checkIcon} />
                    <div className={defaultStyles.tooltip}>
                        <span className={defaultStyles.tooltipText}>Copied!</span>
                    </div>
                </div>
            }
        </div>
    )
}