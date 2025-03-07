import React, { RefObject } from "react";
import { Link } from "react-router-dom";
import { ColumnDef, createColumnHelper } from '@tanstack/react-table';

import { Asset, AssetClass } from "../../../../servers/asset_server";
import { StoreNames, useStore } from "../../../../stores";
import { convertToCurrentTimeZone } from "../../../../utils/dateUtils";
import { CopyButton } from "../../../copyButton";
import { TextHighlighter } from "../../../textHighlighter";
import { AssetSearchTerms } from "../AssetListControlledTable";

import styles from "../asset_list_table.module.scss";

interface TableProps {
    assetClass: AssetClass;
    searchRef: RefObject<AssetSearchTerms>;
}

const getHighlightFromTerms: (term: "owner" | "alias" | "seq_id", searchTerms: AssetSearchTerms | null) =>
    string | undefined = (term, searchTerms) => {
        if (searchTerms?.hasOwnProperty(term)) {
            return searchTerms?.[term]
        }
        return searchTerms?.['search_by']
    }

const hightlightClassName: string = 'font-bold text-primary'

export default function useColumns(props: TableProps) {
    const userStore = useStore(StoreNames.userStore, true);
    const project_id = userStore.get("active_project")

    const columnHelper = createColumnHelper<Asset>()

    const searchRef: RefObject<any> = props.searchRef

    // Use display because sorting/filtering is done on the server
    const columns = React.useMemo<ColumnDef<Asset>[]>(() => [
        columnHelper.display({
            id: "name",
            cell: props => assetNameCell(props.row.original, false, searchRef),
        }),
        columnHelper.display({
            id: "alias",
            cell: props => assetNameCell(props.row.original, true, searchRef)
        }),
        columnHelper.display({
            id: "commit_message",
            cell: props =>
                <div className={styles.infoField}>
                    {props.row.original.leafVersion()?.commit_message}
                </div>
        }),
        columnHelper.display({
            id: "created_by",
            cell: props => createdByCell(props.row.original, searchRef)
        }),
        columnHelper.display({
            id: "date",
            cell: props =>
                <div className={styles.infoField}>
                    {convertToCurrentTimeZone(props.row.original.leafVersion()?.created_at, "date")}
                </div>
        }),
    ], []);

    return columns;


    function assetNameCell(row: Asset, displayAlias: boolean = true, searchRef: RefObject<AssetSearchTerms>) {
        const assetClass = props.assetClass
        const asset = row
        return (
            <div className={styles.assetName}>
                <Link to={
                    `/asset/${project_id}/${assetClass.name}/${asset.seq_id}/files?version=${asset.leafVersionNumber()}`}>
                    {displayAlias ?
                        <TextHighlighter
                            text={asset.alias}
                            highlight={getHighlightFromTerms("alias", searchRef.current)}
                            className={hightlightClassName} />
                        :
                        <TextHighlighter
                            text={`${assetClass.name}/${asset.seq_id}`}
                            highlight={getHighlightFromTerms("seq_id", searchRef.current)}
                            className={hightlightClassName} />
                    }
                </Link>
                <div className={styles.assetCopy}>
                    {displayAlias && asset.alias &&
                        <CopyButton
                            textToCopy={` ${assetClass.name}/${asset.alias}`}
                            tooltip={"copy"}
                            styles={styles}
                        />
                    }
                    {!displayAlias &&
                        <CopyButton
                            textToCopy={`asset clone ${assetClass.name}/${asset.seq_id}`}
                            tooltip={"copy"}
                            styles={styles}
                        />
                    }
                </div>
            </div>
        )
    }

    function createdByCell(row: Asset, searchRef: RefObject<AssetSearchTerms>) {
        return (
            <div className={styles.infoField}>
                <TextHighlighter
                    text={row.leafVersion()?.created_by}
                    highlight={getHighlightFromTerms("owner", searchRef.current)}
                    className={hightlightClassName} />
            </div>
        )
    }

}