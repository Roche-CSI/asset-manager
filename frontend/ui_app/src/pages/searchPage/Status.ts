export enum StatusEnums {
	PUBLIC = 1,
	PRIVATE = 2,
	DELETED = 3,
	DEPRECATED = 4,
	OBSOLETE = 5,
	ARCHIVE_FLAGGED = 6,
	ARCHIVED = 7,
}


export default class Status {
	
	status: number;
	
	constructor(status: number) {
		this.status = status;
	}
	
	description(): string {
		switch (this.status) {
			case StatusEnums.PUBLIC:
				return "Public";
			case StatusEnums.PRIVATE:
				return "Private";
			case StatusEnums.DELETED:
				return "Deleted";
			case StatusEnums.DEPRECATED:
				return "Deprecated";
			case StatusEnums.OBSOLETE:
				return "Obsolete";
			case StatusEnums.ARCHIVE_FLAGGED:
				return "Archive-Flagged";
			case StatusEnums.ARCHIVED:
				return "Archived";
			default:
				return "Unknown";
		}
	}
	
}



