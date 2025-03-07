import {StatusEnums} from "pages/searchPage/Status";


export default class Access {
	canRead: boolean;
	canWrite: boolean;
	canDelete: boolean;
	canAdmin: boolean;
	data: any;
	status: number;
	
	constructor(data: any) {
		this.canRead = Boolean(data.can_read);
		this.canWrite = Boolean(data.can_write);
		this.canDelete = Boolean(data.can_delete);
		this.canAdmin = Boolean(data.can_admin || data.can_admin_project);
		this.status = data.status;
	}
	
	hasPermission(): boolean {
		return this.canRead || this.canWrite || this.canDelete || this.canAdmin;
	}
	
	hasAdminPermission(): boolean {
		return this.canAdmin;
	}
	
	isDeprecated(): boolean {
		return this.status === StatusEnums.DEPRECATED;
	}
	
	isObsolete(): boolean {
		return this.status === StatusEnums.OBSOLETE;
	}
	
	isDeleted(): boolean {
		return this.status === StatusEnums.DELETED;
	}
	
	isArchived(): boolean {
		return this.status === StatusEnums.ARCHIVED;
	}
	
	isPrivate(): boolean {
		return this.status === StatusEnums.PRIVATE;
	}
}
