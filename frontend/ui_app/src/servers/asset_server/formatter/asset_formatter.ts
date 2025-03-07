import Asset from "../asset";
import {convertToCurrentTimeZone} from "../../../utils";
import {AssetVersion} from "../assetVersion";

export default class AssetFormatter {
    asset: Asset;

    constructor(asset: Asset) {
        this.asset = asset;
    }
    assetFields(): object {
        return {
            "ID": this.asset.id,
            "Owner": this.asset.owner,
            "Creator": this.asset.created_by,
            "Created": convertToCurrentTimeZone(this.asset.created_at, "date"),
            "Modified": this.asset.modified_by,
            "Modifier": convertToCurrentTimeZone(this.asset.modified_at, "date")
        }
    }
    versionFields(version: AssetVersion): object {
        return {
            "ID": version.id,
            "Creator": version.created_by,
            "Created": convertToCurrentTimeZone(version.created_at, "date"),
            "Commit hash": version.commit_hash,
            "Commit message": version.commit_message
        }
    }
}