import React, { FunctionComponent } from 'react';

interface Props {
    text: string;
    highlight?: string;
    className?: string;
}

/** Returns a span where the highlighted text is rendered by special style */
const TextHighlighter: FunctionComponent<Props> = (props: Props) => {
    if (!props.text || !props.highlight) {
        return <span>{props.text}</span>
    }

    const parts: string[] = props.text.split(new RegExp(`(${props.highlight})`, 'gi'));
    const defaultHightlightClassName: string = 'font-bold'

    return (
        <span>
            {parts.map((part: string, i: number) =>
                <span
                    key={i}
                    className={part.toLowerCase() === props.highlight?.toLowerCase() ?
                        props.className ? props.className : defaultHightlightClassName
                        : ''}
                >
                    {part}
                </span>)
            }
        </span>
    )
}

export default TextHighlighter;