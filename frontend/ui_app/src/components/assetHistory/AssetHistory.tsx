import React, { useEffect, useState } from "react";
import styles from "./history.module.scss";
import { Asset } from "../../servers/asset_server";
import { HistoryTable } from "../tables";
import { isEmptyObject, useQuery } from "../../utils/utils";
import CompareVersionSelector from "./CompareVersionSelector";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { ObjectBrowser } from "../objectBrowser";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { AlertDismissible } from "../alerts";
import { SpinIndicator } from "../spinIndicator";
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import { DiffTreeViewer } from "../FileTree/DiffTreeViewer";
import { ToggleButtons } from "../toggleButtons";
import { BiSearch } from "react-icons/bi";
import { diffItem } from "../../servers/asset_server/assetVersion"
import { icon } from "../tables/historyTable/HistoryTable"
import { DropDown } from "../dropDown";

interface HistoryProps {
    asset: Asset;
    className?: string;
    view: string;
}

export default function AssetHistory(props: HistoryProps) {
    const { class_name, seq_id, view } = useParams();
    const [error, setError] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    // query
    const navigate = useNavigate();
    const location = useLocation();
    const base: string = useQuery().get('base');
    const compare: string = useQuery().get('compare');
    const path: string = useQuery().get('path');
    // state
    const [versionDiffArray, setVersionDiffArray] = useState<any[]>([])
    const [diffObject, setDiffObject] = useState<any>({})
    const [diffArray, setDiffArray] = useState<any[]>([])
    const [category, setCategory] = useState<string>("")
    // view
    const [fileView, setFileView] = useState<"flat" | "folder">("folder")

    const onPathClick = (pathName: string) => {
        navigate(`${location.pathname}?base=${base}&compare=${compare}&path=${pathName}`);
    }

    const updateDiffs = () => {
        if (base === compare) { //nothing to compare
            setDiffObject({})
            setDiffArray([])
            return;
        }
        const baseVersion: AssetVersion | null = props.asset.getVersion(base);
        AssetVersion.updateVersionObjects(props.asset, baseVersion)
        const compareVersion: AssetVersion | null = props.asset.getVersion(compare);
        AssetVersion.updateVersionObjects(props.asset, compareVersion)
        // console.log("base: ", baseVersion, "compare: ", compareVersion)
        let { diffObject, diffArray }: any = AssetVersion.computeDiff(baseVersion, compareVersion)
        setVersionDiffArray(diffArray)
        setDiffObject(diffObject)
        setDiffArray(diffArray)
        diffArray.length > 0 && onPathClick(diffArray[0].path)
        // console.log("diffObject:", diffObject, "DiffArray:", diffArray)
    }

    const updateVersions = () => {
        if (isEmptyObject(props.asset.all_objects) || isEmptyObject(props.asset.versions)) {
            setLoading(true)
            let assetName: string = Asset.getName(class_name as string, seq_id as any);
            Asset.getFromServer(null, assetName).then((json) => {
                let full_asset: any = json[0];
                props.asset.updateObjects(full_asset.all_objects)
                props.asset.updateVersions(full_asset.versions)
                updateDiffs(); // after assets updated, update diffs
                setLoading(false)
            }).catch(error => {
                setError(error);
                setLoading(false)
            })
        }
    }

    useEffect(() => {
        updateVersions();
    }, [props.asset])

    useEffect(() => {
        updateDiffs();
    }, [base, compare])

    return (
        <div className={styles.card}>
            {header()}
            {infoHeader()}
            {main()}
            {error && <AlertDismissible>{error}</AlertDismissible>}
            {loading &&
                <div className={styles.spinnerContainer}>
                    <SpinIndicator message={"Loading..."} />
                </div>
            }
        </div>
    )

    function main() {
        return (
            <div>
                {base === compare ?
                    <div className={styles.emptyContainer}>
                        <CompareArrowsIcon />
                        <h4>There isn&apos;t anything to compare.</h4>
                        <p>You&apos;ll need to use two versions to get a valid comparison.</p>
                    </div>
                    :
                    historyView()
                }
            </div>
        )
    }

    function historyView() {
        return (
            <div className={styles.historyContainer}>
                <div className={styles.historyPanel}>
                    <div className={styles.panelField}>
                        <div className={styles.searchBar}>
                            <div className={styles.searchIcon}><BiSearch /></div>
                            <input type="text" placeholder="Filter changed files"
                                onChange={(e: any) => onSearch(e.target.value)} />
                        </div>
                        <div className={styles.categoryDropDown}>
                            {categoryDropDown()}
                        </div>
                    </div>
                    {historyTable()}
                </div>
                <div className={styles.historyViewer}>
                    {objectBrowser()}
                </div>
            </div>
        )
    }

    function historyTable() {
        return (
            <div>
                {fileView === "flat" ?
                    <div className={styles.historyTable}>
                        <HistoryTable
                            path={path}
                            onPathClick={onPathClick}
                            diffArray={diffArray} />
                    </div>
                    :
                    <div className={styles.historyTable}>
                        <DiffTreeViewer
                            path={path}
                            onPathClick={onPathClick}
                            diffArray={diffArray} />
                    </div>
                }
            </div>
        )
    }

    function objectBrowser() {
        return (
            <ObjectBrowser
                asset={props.asset}
                path={path}
                view={props.view}
                diffObject={diffObject}
                base={base}
                compare={compare} />
        )
    }

    function header() {
        return (
            <div className={styles.cardHeader}>
                <div className={styles.headerItem}>
                    <AccountCircleIcon />
                    <span style={{ fontWeight: "bold" }}>{props.asset.created_by}</span>
                </div>
                <div className={styles.compareVersionSelector}>
                    <CompareVersionSelector versions={props.asset.versions} base={base} compare={compare} />
                </div>
            </div>
        )
    }

    function infoHeader() {
        const diffLength = `${diffArray.length} changed ${diffArray.length === 1 ? "file" : "files"}`
        return (
            <div className={styles.infoHeader}>
                <div>
                    {diffLength}
                    <div className={styles.headerItem}>
                        <ToggleButtons value={fileView} options={["flat", "folder"]}
                            setValue={setFileView} size={"sm"} />
                    </div>
                </div>
                <div>{path}</div>
            </div>
        )
    }

    function categoryDropDown() {
        const options: any[] = ["", "added", "altered", "removed"].map((option: string) => (
            {
                value: option,
                label: icon(option)
            }
        ))
        return (
            <div>
                <DropDown options={options}
                    onChange={onCategoryChange}
                    active={
                        {
                            value: category,
                            label: icon(category)
                        }
                    }
                    className={styles.categoryDropDown} />
            </div>
        )
    }

    function onSearch(path: string) {
        if (!path) {
            setDiffArray(versionDiffArray)
            return;
        }
        let filteredArray: diffItem[] = versionDiffArray.filter(
            (item: diffItem) => {
                return item.path.toLowerCase().includes(path.toLowerCase())
            })
        setDiffArray(filteredArray)
    }

    function onCategoryChange(option: any) {
        setCategory(option.value)
        let filteredArray: diffItem[] = versionDiffArray.filter(
            (item: diffItem) => {
                return item.category.includes(option.value)
            })
        setDiffArray(filteredArray)
    }
}