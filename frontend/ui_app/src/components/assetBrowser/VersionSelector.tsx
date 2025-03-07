import React from "react";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import { Asset } from "../../servers/asset_server";
import { useLocation, useNavigate } from "react-router-dom";
import { ChevronDropdown } from "../topNav/ChevronDropDown";

interface SelectorProps {
    versions: AssetVersion[];
    activeVersion?: AssetVersion | null;
    asset?: Asset;
}


export default function VersionSelector(props: SelectorProps) {
    const navigate = useNavigate();
    const location = useLocation();

    const changeVersion = (version: string) => {
        // console.log(option, location);
        navigate(`${location.pathname}?version=${version}`);
    }

    const versions = props.versions.sort((first: AssetVersion, second: AssetVersion) => {
        return second.id - first.id;
    })

    const versionLabel = props.activeVersion?.number === props.asset?.leafVersionNumber() ? ' - Latest' : '';

    const options = versions.map((version: AssetVersion, index: number) => {
        return (
            <button className='btn btn-sm btn-ghost w-36 flex items-center justify-start'
                key={index}
                onClick={() => changeVersion(version.number)}>
                <span>{version.number}</span>
            </button>
        )
    })

    return (
        <div>
            {
                props.activeVersion &&
                <ChevronDropdown
                    className="border border-base-300 rounded-md !w-40"
                    label={`${props.activeVersion.number}${versionLabel}`}
                    buttonClassName="btn btn-sm btn-ghost border border-gray-dark rounded-md text-title-xsm hover:text-primary"
                    dropdownClassName="!w-40 bg-base-100">
                    {options}
                </ChevronDropdown>
            }
        </div>
    )

}
