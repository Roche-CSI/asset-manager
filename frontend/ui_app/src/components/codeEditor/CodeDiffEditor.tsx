// ref: https://microsoft.github.io/monaco-editor/playground.html#customizing-the-appearence-exposed-colors
// ref1: https://code.visualstudio.com/api/references/theme-color#diff-editor-colors
import React from "react";
import { DiffEditor } from "@monaco-editor/react";

interface Props {
    language?: string;
    original?: any;
    modified?: any;
    readonly?: boolean;
    height?: number;
    className?: string;
    originalLanguage?: string;
    modifiedLanguage?: string;
    originalEditable?: boolean;
}
const defaultHeight = 600;

export default function CodeDiffEditor(props: Props) {
    // const onChange = (value: string | undefined, monaco: any) => {
    //     props.onChange && props.onChange(value);
    // }
    const height = `${props.height || defaultHeight}px`;

    function handleEditorDidMount(editor: any, monaco: any) {
        monaco.editor.defineTheme('my-theme', {
            base: 'vs',
            inherit: true,
            rules: [],
            colors: {
                'diffEditor.insertedTextBackground': '#ABF2BC',
                'diffEditor.removedTextBackground': "#FF818266",
                'diffEditor.insertedLineBackground': '#E6FFEC',
                'diffEditor.removedLineBackground': '#FFEBE9',
                "diffEditor.diagonalFill": "#FFFFFF",
            },
        });
        monaco.editor.setTheme('my-theme')
    }

    return (
        <DiffEditor
            className={props.className || ""}
            height={height}
            language={props.language || "json"}
            // theme={"xcode-default"}
            onMount={handleEditorDidMount}
            original={props.original || ""}
            modified={props.modified || ""}
            originalLanguage={props.originalLanguage || "json"}
            modifiedLanguage={props.modifiedLanguage || "json"}
            options={{
                selectOnLineNumbers: true,
                originalEditable: Boolean(props.originalEditable),
                readOnly: Boolean(props.readonly)
            }}
        />
    );
}